import json
import os
import pickle
from argparse import ArgumentParser

import numpy as np

import dash_html_components as html
import markdown
import pandas as pd
import plotly.graph_objs as go
import yaml
from app import download, group, help_page, matching, person, summary, top
from app.utils import create_app, create_content_header, nav_menu
from app.upload import convert_pdf_to_txt, format_strength
from attrdict import AttrDict
from dash.dependencies import Input, Output
from dash_extensions.snippets import send_data_frame
from flask import Flask, Markup, redirect, render_template, request

server = Flask(__name__)

# load setting file
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# load data
df_top5 = pd.read_csv(config['data_path']['top5'], index_col='index')
df_all34 = pd.read_csv(config['data_path']['all34'], index_col='index')
df_mst = pd.read_csv(config['data_path']['mst_category'])
df_strength = pd.read_csv(config['data_path']['strengths_csv'])
df_all = pd.read_csv(config['data_path']
                     ['all34_exsits_null'], index_col='index')
df_all = df_all.fillna('nan')
df_corr_all34 = pd.read_csv(
    config['data_path']['all34_corr'], index_col='index')
rank_matrix = df_all34.reset_index().pivot(
    index='strengths', columns='index', values='rank')
rank_matrix = 35 - rank_matrix
list_person = np.unique(df_all.index)

with open(config['data_path']['dict_colors_strengths'], mode='rb') as f:
    dict_colors_strengths = pickle.load(f)
with open(config['data_path']['dict_strengths_desc'], mode='rb') as f:
    dict_strengths_desc = pickle.load(f)
with open(config['data_path']['mst_message_json'], 'r', encoding='utf-8') as r:
    dict_strengths_message = json.load(r)
with open(config['data_path']['GS_config'], 'r', encoding='utf-8') as fi_:
    GS_conf = AttrDict(yaml.load(fi_, Loader=yaml.SafeLoader))

target_person = np.unique(df_corr_all34.index)

# =============================
# Route Page
# =============================
dashapp = create_app(server, url_base_pathname='/')
dashapp.layout = html.Div([nav_menu, create_content_header('ストレングスファインダーWebAppへようこそ', '')],
                          style=dict(margin="50px"))

# =============================
# Top Page
# =============================
dashapp_top = create_app(server, url_base_pathname='/top/')
dashapp_top.layout = top.get_layout(list_person)


@dashapp_top.callback(Output('my-graph', 'figure'), [Input('input_id', 'value')])
def update_graph(list_person):
    data = top.get_plot_table_data(
        df_all, dict_colors_strengths, dict_strengths_desc, list_person)

    layout = go.Layout(
        font=dict(size=16),
        hovermode='closest',
        height=1800,
        width=1000,
        barmode='stack',
        showlegend=False,
        xaxis=dict(side='top',
                   tickangle=90),
        yaxis=dict(
            autorange='reversed',
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            dtick=1,
        )
    )

    return {'data': data, 'layout': layout}

# =============================
# upload page
# =============================


def check_extension(filename, extension='.pdf'):
    if os.path.splitext(filename)[1] == extension:
        return True
    else:
        return False


@server.route('/exists/')
def exists():
    text = '**すでに存在するユーザーです。**'
    content = Markup(markdown.markdown(text))
    return render_template('index.html', **locals())


dashapp_upload_done = create_app(server, url_base_pathname='/upload_done/')
dashapp_upload_done.layout = html.Div([nav_menu,
                                       create_content_header('アップロードが完了しました。',
                                                             'マッチング機能のみ、反映に5分程かかります。')],
                                      style=dict(margin="50px"))


@server.route('/upload/')
def upload_new():
    return render_template("upload.html",
                           departments=config['departments'])


@server.route('/upload_check', methods=['POST'])
def upload_check():
    username = request.form['username']
    department = request.form['department']

    dict_list = []
    dict_list.append({'name': 'username', 'label': '名前', 'value': username})
    dict_list.append(
        {'name': 'department', 'label': '本部', 'value': department})

    strength = pd.read_csv(config['data_path']['strengths_csv'])
    if username in strength.columns:
        return redirect('/exists/')

    if not 'file' in request.files:  # ファイル未指定
        message = '**ファイルが未選択です。ファイルを選択してください。**'
        content = Markup(markdown.markdown(message))
        return render_template('index.html', **locals())
    elif not check_extension(request.files['file'].filename):  # 拡張子チェック
        message = 'PDFファイルのみアップロード可能です。PDFファイルを選択してください。'
        content = Markup(markdown.markdown(message))
        return render_template('index.html', **locals())
    else:
        # ファイルの保存
        savepath = os.path.join(config['data_path']['upload_dir'],
                                request.files['file'].filename)
        request.files['file'].save(savepath)

        # pdf2txt
        txt = convert_pdf_to_txt(savepath)
        dict_result = format_strength(txt)
        if not dict_result['status']:  # convert失敗
            message = dict_result['error_message']
            for i in range(0, 34):
                dict_list.append({'name': 'rank' + str(i + 1),
                                  'label': str(i + 1),
                                  'value': ''})
        else:
            message = '結果を確認'

            # format
            list_strength = dict_result['result']
            for i, sf in enumerate(list_strength):
                dict_list.append({'name': 'rank' + str(i + 1),
                                  'label': str(i + 1),
                                  'value': sf})

            # アップロードされたファイルの削除
            os.remove(savepath)
        return render_template("./upload_check.html", upload_list=dict_list,
                               message=message)


@server.route('/post', methods=["GET", "POST"])
def post():
    # get form values
    username = request.form['username']
    department = request.form['department']
    elements = []

    for i in range(1, 35):
        try:
            _element = request.form['rank'+str(i)]
            _element = _element.strip('\u3000')
        except:
            _element = np.nan
        elements.append(_element)
    # output streangth
    strength = pd.read_csv(config['data_path']['strengths_csv'])
    strength[username] = elements
    strength.to_csv(config['data_path']['strengths_csv'], index=False)

    # output streangth
    demogra = pd.read_csv(config['data_path']['demogra_csv'])
    demogra = demogra.append(pd.Series([username, department], index=["name", "department"]),
                             ignore_index=True)
    demogra.to_csv(config['data_path']['demogra_csv'], index=False)

    return redirect('/upload_done/')


# =============================
# Overview Page
# =============================
dashapp_summary = create_app(server, url_base_pathname='/dashboard/overview/')
sr_score_all = df_top5.groupby(['department', 'strengths'])['score'].sum()
dashapp_summary.layout = summary.get_layout(
    df_top5, df_all34, sr_score_all, dict_colors_strengths)

# =============================
# Person Page
# =============================
dashapp_person = create_app(server, url_base_pathname='/dashboard/person/')
dashapp_person.layout = person.get_layout(target_person)
list_method = ['PCA(2d)', 'NMF(2d)', 'NMF(3d)']


@dashapp_person.callback(Output('my-graph', 'figure'), [Input('input_id', 'value')])
def update_graph(target_person):
    data = person.get_plot_table_data(df_corr_all34, target_person)

    layout = go.Layout(
        font=dict(size=16),
        hovermode='closest',
        height=2000,
        width=1000,
        barmode='stack',
        showlegend=False,
        xaxis=dict(title="Strengths",
                   side='top',
                   tickangle=90),
        yaxis=dict(
            autorange='reversed',
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            dtick=1,
        )
    )

    return {'data': data, 'layout': layout}


# =============================
# Group Page
# =============================
dashapp_group = create_app(server, url_base_pathname='/dashboard/group/')
list_category = df_mst['category'].unique()
dict_strengths_category = df_mst.set_index('strengths')['category'].to_dict()
dashapp_group.layout = group.get_layout(df_top5)


@dashapp_group.callback(Output('my-graph', 'figure'), [Input('group_persons', 'value')])
def update_graph(list_person):
    dict_rank_to_score = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    df_top5['category'] = df_top5[['strengths']
                                  ].applymap(dict_strengths_category.get)
    df_top5['score'] = df_top5[['rank']].applymap(dict_rank_to_score.get)

    data = []

    # 初期化
    dict_scores = {}
    for _categry in list_category:
        dict_scores[_categry] = 0

    for _person in list_person:
        dict_score = group.calc_score(df_top5, _person)
        dict_score = dict(sorted(dict_score.items()))
        for _categry, _score in dict_score.items():
            dict_scores[_categry] += _score

        trace = group.create_trace(list_category, dict_score, _person)
        data.append(trace)

    dict_scores = dict(sorted(dict_scores.items()))

    trace0 = go.Scatterpolar(
        r=list(dict_scores.values()),
        theta=list(dict_scores.keys()),
        fill='toself',
        fillcolor='gray',
        name='合計',
        opacity=0.7,
        marker=dict(symbol="square",
                    size=8
                    ),
        line=dict(color='black'),
        subplot='polar2'
    )

    data.append(trace0)

    ann1 = dict(font=dict(size=14),
                showarrow=False,
                text='合計スコア',
                # Specify text position (place text in a hole of pie)
                x=0.16,
                y=1.18
                )
    ann2 = dict(font=dict(size=14),
                showarrow=False,
                text='各人のスコア',
                x=0.85,
                y=1.18
                )

    layout = go.Layout(
        annotations=[ann1, ann2],
        showlegend=True,
        polar2=dict(domain=dict(x=[0, 0.4],
                                y=[0, 1]
                                ),
                    radialaxis=dict(tickfont=dict(size=8)),
                    ),
        polar=dict(domain=dict(x=[0.6, 1],
                               y=[0, 1]
                               ),
                   radialaxis=dict(tickfont=dict(size=8)),
                   )
    )

    return {'data': data, 'layout': layout}


# ユニークな強み表示
@dashapp_group.callback(
    Output('person_drop_down', 'options'),
    [Input('group_persons', 'value')])
def set_cities_options(selected_country):
    return [{'label': i, 'value': i} for i in selected_country]


@dashapp_group.callback(Output('person_drop_down', 'value'),
                        [Input('person_drop_down', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']


@dashapp_group.callback(Output('target_name', 'children'),
                        [Input('group_persons', 'value'),
                         Input('person_drop_down', 'value')])
def update_unique_strestrength(list_person, target_name):
    text = 'このグループ内における{}さんのユニークな強みは下記の通りです。'.format(target_name)
    return text


@dashapp_group.callback(Output('unique_strengths_1', 'children'),
                        [Input('group_persons', 'value'),
                         Input('person_drop_down', 'value')])
def update_unique_strestrength_1(list_person, target_name):
    dict_result = group.main(
        df_strength, target_name, list_person)
    text = group.create_maerkdown_text(
        dict_strengths_message, dict_result, 0, target_name)
    return text


@dashapp_group.callback(Output('unique_strengths_2', 'children'),
                        [Input('group_persons', 'value'),
                         Input('person_drop_down', 'value')])
def update_unique_strestrength_2(list_person, target_name):
    dict_result = group.main(
        df_strength, target_name, list_person)
    text = group.create_maerkdown_text(
        dict_strengths_message, dict_result, 1, target_name)
    return text
    

# 不足している資質表示
topN = 10  # topN位以上の資質が含まれていれば足りない資質ではないとする
output_num = 2  # 最大でいくつの資質を出力するか

@dashapp_group.callback(Output('lack_strengths_1', 'children'),
                        [Input('group_persons', 'value')])
def update_lack_strength_1(list_person):
    dict_lack_result = group.lack_strengths_in_group(
        df_all, list_person, topN, output_num)
    text = group.create_maerkdown_text_with_lack(
        dict_strengths_message, dict_lack_result, 0)
    return text


@dashapp_group.callback(Output('lack_strengths_2', 'children'),
                        [Input('group_persons', 'value')])
def update_lack_strength_2(list_person):
    dict_lack_result = group.lack_strengths_in_group(
        df_all, list_person, topN, output_num)
    text = group.create_maerkdown_text_with_lack(
        dict_strengths_message, dict_lack_result, 1)
    return text


# =============================
# Matching Page
# =============================
dashapp_matching = create_app(server, url_base_pathname='/dashboard/matching/')
dashapp_matching.layout = matching.get_layout(df_top5)


@dashapp_matching.callback(Output('matching_check', 'children'),
                           [Input('group_personsA', 'value'),
                            Input('group_personsB', 'value')])
def check_matching_input(list_personA, list_personB):
    if len(set(list_personA) & set(list_personB)) != 0:
        return 'メンティー集合とメンター集合に重複があります'
    elif len(set(list_personA)) > len(set(list_personB)):
        return 'メンティー集合の要素をメンター集合の要素と同等以下になるように減らしてください'
    else:
        return True


@dashapp_matching.callback(Output('matching', 'figure'),
                           [Input('matching_check', 'children'),
                            Input('group_personsA', 'value'),
                            Input('group_personsB', 'value')])
def update_matching(check_result, list_personA, list_personB):
    try:
        del result
        print('delete result')
    except:
        pass

    if not check_result == True:
        return {'data': [], 'layout': []}
    else:
        num_dict = matching.make_dict(df_strength)
        res_mat = np.loadtxt(GS_conf.save_res_cos_name, delimiter=',')
        set_A, set_B = matching.prefer_order(
            list_personA, list_personB, num_dict, res_mat)
        result = matching.search_stable_matching(set_A, set_B)

        df_result = pd.DataFrame.from_dict(
            result, orient='index').reset_index()
        df_result.columns = ['メンター', 'メンティー']
        df_result = df_result[['メンティー', 'メンター']]
        df_result = df_result[df_result['メンティー'] != '']

        data = [go.Table(
                header=dict(values=df_result.columns,
                            align='center',
                            line=dict(color='darkslategray'),
                            fill=dict(color=['#FFE4E1', '#E6E6FA'],)
                            ),
                cells=dict(values=df_result.values.T,
                           align='center',
                           line=dict(color='darkslategray'),
                           font=dict(color='darkslategray'),
                           fill=dict(color='white'),
                           ),
                )]

        layout = go.Layout(
            title='マッチング結果',
            font=dict(size=15),
            hovermode='closest',
            # height=1800,
            # width=2500,
            barmode='stack',
            showlegend=False,
            xaxis=dict(title="Strengths",
                       side='top',
                       tickangle=90),
            yaxis=dict(
                autorange='reversed',
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks='',
                dtick=1,
            )
        )

        return {'data': data, 'layout': layout}


# =============================
# Downloader Page
# =============================
dashapp_download = create_app(server, url_base_pathname='/download/')
dashapp_download.layout = download.get_layout()

@dashapp_download.callback(Output("mst_download", "data"),
                           [Input('mst_download_btn', 'n_clicks')])
def get_master(n_clicks):
    if not n_clicks == None:
        df = pd.read_csv(config['data_path']['demogra_csv'])
        return send_data_frame(df.to_csv, filename="member_demogra.csv")
    else:
        return None

@dashapp_download.callback(Output("strengths_download", "data"),
                           [Input('strengths_download_btn', 'n_clicks')])
def get_strengths(n_clicks):
    if not n_clicks == None:
        df = pd.read_csv(config['data_path']['strengths_csv'])
        return send_data_frame(df.to_csv, filename="member_strengths.csv")
    else:
        return None


# =============================
# Help Page
# =============================
dashapp_help = create_app(server, url_base_pathname='/help/')
dashapp_help.layout = help_page.get_layout()

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    port = int(os.environ.get('PORT', config['port']))
    server.run(debug=options.debug, port=port, host='0.0.0.0')
