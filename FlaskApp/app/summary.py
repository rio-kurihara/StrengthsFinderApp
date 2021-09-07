import plotly.graph_objs as go
import yaml

import dash_core_components as dcc
import dash_html_components as html
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header

# load setting file
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# 集計対象の部署名を設定
departments = config['departments']
departments.remove("retiree")


def get_plot_score_data(sr_score_all, dict_colors_strengths, honbu_name):
    list_honbu = sr_score_all.index.levels[0]
    if honbu_name in list_honbu:
        sr_score = sr_score_all.loc[honbu_name].sort_values()[::-1]
        list_unknown = list(
            set(dict_colors_strengths.keys()) - set(sr_score.index))
        x = list(sr_score.index)
        x += list_unknown
        y = list(sr_score.values)
        y += [-1 for x in list_unknown]

        trace0 = go.Bar(
            x=x,
            y=y,
            marker=dict(
                color=[dict_colors_strengths[_strengths] for _strengths in x]),
        )

        data = [trace0]
    else:
        data = []
    return data


def get_plot_cnt_data(df_top5, df_all34):
    y0, y1 = [], []

    for department in departments:
        df_tmp_top5 = df_top5[df_top5['department'] == department]
        df_tmp_all34 = df_all34[df_all34['department'] == department]
        if not (len(df_tmp_all34) == 0 and len(df_tmp_top5) == 0):
            set_top5_person = set(list(df_tmp_top5.index))
            set_all34_person = set(list(df_tmp_all34.index))

            y0.append(len(set_all34_person))
            y1.append(len(set_top5_person) - len(set_all34_person))
        else:
            y0.append(0)
            y1.append(0)

    trace0 = go.Bar(
        x=departments,
        y=y0,
        name='全資質オープン済'
    )
    trace1 = go.Bar(
        x=departments,
        y=y1,
        name='TOP5のみ'
    )
    data = [trace0, trace1]
    return data


def get_layout(df_top5, df_all34, sr_score_all, dict_colors_strengths):
    graph_layout = [
        nav_menu,
        create_content_header('診断済み社員数：{}名'.format(
            len(set(df_top5.index))), ''),
        html.Div(
            dcc.Graph(
                id='cnt',
                figure={
                    'data': get_plot_cnt_data(df_top5, df_all34),
                    'layout': {
                        'barmode': 'stack',
                        'title': '部署別診断済みの社員数',
                        'yaxis': dict(title='人数'),
                        'xaxis': dict(title='本部')
                    }
                }
            ), style={'display': 'inline-block'}),
    ]

    # 各本部別の集計グラフをlayoutにappend
    graph_layout.append(create_content_header('資質ランキング', ''))

    for i, department in enumerate(departments):
        graph_layout.append(
            html.Div(
                dcc.Graph(
                    id='score_summary{}'.format(i+1),
                    figure={
                        'data': get_plot_score_data(sr_score_all, dict_colors_strengths, department),
                        'layout': {
                            'title': '資質の合計スコア({})'.format(department)
                        }
                    }
                ),
                style={'display': 'inline-block'})
        )

    layout = html.Div(graph_layout,
                      style={'width': '100%', 'height': '100%',
                             #   'display': 'inline-block',
                             'margin': '50px'})

    return layout
