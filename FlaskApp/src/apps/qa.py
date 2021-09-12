import yaml
from dash import html


# load setting file
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)


algorithm_contents = html.Div(
    [
        html.H5('各機能のアルゴリズム詳細',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)

contact_contents = html.Div(
    [
        html.H5('問い合わせ先',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P(config['contact'])
    ]
)

layout = html.Div(
    [
        algorithm_contents,

        html.P('作成中'),

        contact_contents,
    ],
    style=dict(margin='50px')
)
