import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import markdown
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import pickle

from argparse import ArgumentParser
from dash.dependencies import Input
from dash.dependencies import Output
from flask import Flask
from flask import Markup
from flask import render_template
from flaskext.markdown import Markdown


def protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.url_base_pathname):
            dashapp.server.view_functions[view_func]

server = Flask(__name__)
set_port = 55449

@server.route('/')
def index():
    content = """
## [Top](http://192.168.99.157:{}/)

## DashBoard  

* [Summary](http://192.168.99.157:55449/dashboard/summary)  
* [Person](http://192.168.99.157:55449/dashboard/person)  
* [Group](http://192.168.99.157:55449/dashboard/group)  

## Data Upload  

* これから作るよ  

""".format(set_port)
    content = Markup(markdown.markdown(content))
    return render_template('index.html', **locals())

# =============================
# Summary Page
# =============================
dashapp_summary = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/summary')
protect_dashviews(dashapp_summary)

md_text = dcc.Markdown('''
---  
## 資質の平均順位(昇順表示)  

**選択した本部内メンバーの資質の平均順位を表示します**  

赤  ： 実行力  (「何かを実行したい」「完遂したい」資質)  
黄色： 影響力  (「人に影響を与えたい」「人を動かしたい」資質)  
緑  ： 人間関係構築力  (「人とつながりたい」「関係性を築きたい」資質)  
青  ： 戦略的思考力  (「考えたい」「頭脳活動をしたい」資質)

グループ分けの意味の詳細は[こちら](https://heart-lab.jp/strengthsfinder/sftheme4groups/)
''')

def _calc_rank_mean(df):
    rank_mean = df.groupby('strengths')['rank'].mean().sort_values()
    values = np.round(rank_mean.values, 1)
    index = rank_mean.index
    return index, values

dashapp_summary.layout = html.Div([
        md_text,
        dcc.RadioItems(
                    id='input_id',
                    options=[{'label': i, 'value': i} for i in ['AS','SD','DS','MP','AIB','CO','ALL']]
        ),
        dcc.Graph(id='my-graph')]
)

@dashapp_summary.callback(Output('my-graph', 'figure'), [Input('input_id', 'value')])
def update_graph(name):
    # load data
    df_top5 = pd.read_csv('./data/df_top5.csv', index_col='index')
    df_all34 = pd.read_csv('./data/df_all34.csv', index_col='index')
    with open('./data/mst/dict_colors_strengths.pkl', mode='rb') as f:
        dict_colors_strengths = pickle.load(f)

    # data filtering
    if not name == 'ALL':
        df_top5 = df_top5[df_top5['所属本部'] == name]
        df_all34 = df_all34[df_all34['所属本部'] == name]
    
    index_top5, values_top5 = _calc_rank_mean(df_top5)
    index_all34, values_all34 = _calc_rank_mean(df_all34)
    
    trace0 = go.Table(
        domain=dict(x=[0, 0.49],
                y=[0, 1.0]),
        header=dict(values=list(['資質', '順位の平均']),
                    fill = dict(color='#bbbbbb'),
                    line = dict(color = '#506784'),
                    font = dict(size = 12)
                   ),
        cells=dict(values=[index_all34, values_all34],
                   fill = dict(color=[[dict_colors_strengths[x] for x in index_all34], '#fffff4']
                              ),
                   line = dict(color = '#506784'),
                   font = dict(size = 12),
                   height = 30,
                   ))

    trace1 = go.Table(
        domain=dict(x=[0.5, 1.0],
                y=[0, 1.0]),
        header=dict(values=list(['資質', '順位の平均']),
                    fill = dict(color='#bbbbbb'),
                    line = dict(color = '#506784'),
                    font = dict(size = 12)
                   ),
        cells=dict(values=[index_top5, values_top5],
                   fill = dict(color=[[dict_colors_strengths[x] for x in index_top5], '#fffff4']
                              ),
                   line = dict(color = '#506784'),
                   font = dict(size = 12),
                   height = 30,
                   ))

    ann1 = dict(font=dict(size=13),
                showarrow=False,
                text='ALL34',
                # Specify text position (place text in a hole of pie)
                x=0.22,
                y=1.03
                )
    ann2 = dict(font=dict(size=13),
                showarrow=False,
                text='TOP5',
                x=0.77,
                y=1.03
                )
    layout = go.Layout(title ='順位平均',
                       annotations=[ann1,ann2],
                       height=1300
                       )
    
    return {'data':[trace0, trace1], 'layout': layout}


# =============================
# Person Page
# =============================
dashapp_person = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/person')
protect_dashviews(dashapp_person)

md_text = dcc.Markdown('''
# 順位相関(降順表示)  

- 選択した方とそれ以外の方との順位相関を降順表示します
''')

df_corr_all34 = pd.read_csv('./data/for_plot/df_corr_all34.csv', index_col='index')
label = df_corr_all34.columns

dashapp_person.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='heatmap',
            figure={
                'data': [
                    go.Heatmap(x=label,
                           y=label,
                           z=df_corr_all34,
                           colorscale='Viridis')
                ],
                'layout': {
                    'title': '相関',
                    'width': 700,
                    'height': 700
                }
            })],
        style={'width': '49%', 'display': 'inline-block', 'padding': 0})
    ,
    html.Div([
        md_text,
        dcc.RadioItems(
                    id='input_id',
                    options=[{'label': i, 'value': i} for i in df_corr_all34.columns],
                    labelStyle={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='my-graph')],
        style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
#         style={'width': '49%', 'display': 'inline-block', 'padding': 0}),
])

@dashapp_person.callback(Output('my-graph', 'figure'), [Input('input_id', 'value')])
def update_graph(name):
    df_soukan = pd.DataFrame(df_corr_all34[name].sort_values()[::-1].drop(name)).reset_index()
    df_soukan.columns = ['氏名', '相関係数']
    df_soukan['相関係数'] = df_soukan['相関係数'].round(decimals=2)
    
    trace = go.Table(
        #     columnorder = [1,2],
        columnwidth = [20,30],
        header=dict(values=list(df_soukan.columns),
                    fill = dict(color='#C2D4FF')
                   ),
        cells=dict(values=[df_soukan['氏名'], df_soukan['相関係数']],
                   fill = dict(color='#F5F8FF'),
                   ))
    return {'data':[trace], 'layout': {'height': 800}}




# =============================
# Group Page
# =============================
dashapp_group = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/group')
protect_dashviews(dashapp_group)

md_text = dcc.Markdown('''
# グループの傾向把握

- 選択した方達の全体傾向と個人の傾向を可視化
''')
# load data
df_top5 = pd.read_csv('./data/df_top5.csv', index_col='index')
df_mst = pd.read_csv('./data/mst_category.csv')
list_category =df_mst['category'].unique()
dict_strengths_category = df_mst.set_index('strengths')['category'].to_dict()

dashapp_group.layout = html.Div([
    md_text,
    dcc.Dropdown(
        id='input_id',
        options=[{'label': i, 'value': i} for i in np.unique(df_top5.index)],
        multi=True,
    ),
#     dcc.RadioItems(
#                 id='input_id',
#                 options=[{'label': i, 'value': i} for i in np.unique(df_top5.index)],
#                 labelStyle={'width': '49%', 'display': 'inline-block'}),
    dcc.Graph(id='my-graph')]
)

def calc_score(person_name: str):
    sr_agr_score = df_top5.loc[person_name].groupby('category')['score'].sum()
    dict_score = sr_agr_score.to_dict()
    return dict_score

def create_trace(dict_score: dict, person_name: str):    
    # TOP5に存在しない資質カテゴリはスコアを0にする
    for _categry in list_category:
        if not _categry in dict_score:
            dict_score[_categry] = 0
    
    dict_score = dict(sorted(dict_score.items()))
    trace = go.Scatterpolar(
        r = list(dict_score.values()),
        theta = list(dict_score.keys()),
        fill = 'toself',
        name = person_name,
        opacity=0.9,
        marker = dict(
            symbol = "square",
            size = 8
        ),
    )
    
    return trace


@dashapp_group.callback(Output('my-graph', 'figure'), [Input('input_id', 'value')])
def update_graph(list_person):
    dict_rank_to_score = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    df_top5['category'] = df_top5[['strengths']].applymap(dict_strengths_category.get)
    df_top5['score'] = df_top5[['rank']].applymap(dict_rank_to_score.get)

    data = []

    # 初期化
    dict_scores = {}
    for _categry in list_category:
        dict_scores[_categry] = 0


    for _person in list_person:
        dict_score = calc_score(_person)
        dict_score = dict(sorted(dict_score.items()))
        for _categry, _score in dict_score.items():
            dict_scores[_categry] += _score

        trace = create_trace(dict_score, _person)
        data.append(trace)

    dict_scores = dict(sorted(dict_scores.items()))

    trace0 = go.Scatterpolar(
        r = list(dict_scores.values()),
        theta = list(dict_scores.keys()),
        fill = 'toself',
        fillcolor = 'gray',
        name='合計',
        opacity=0.7,
        marker = dict(
            symbol = "square",
            size = 8
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
        annotations=[ann1,ann2],
        showlegend = True,
        polar2 = dict(
          domain = dict(
            x = [0,0.4],
            y = [0,1]
          ),
          radialaxis = dict(
            tickfont = dict(
              size = 8
            )
          ),
        ),
        polar = dict(
          domain = dict(
            x = [0.6,1],
            y = [0,1]
          ),
          radialaxis = dict(
            tickfont = dict(
              size = 8
            )
          ),
        )
    )


    
    return {'data':data, 'layout': layout}




if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    port = int(os.environ.get('PORT', set_port))
    server.run(debug=options.debug, port=port, host='0.0.0.0')
