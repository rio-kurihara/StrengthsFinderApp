import yaml
from dash import html

# settings.yaml の読み込み
with open('src/settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

contact_address = config['contact']

algorithm_contents = html.Div(
    [
        html.H5('各機能のアルゴリズム詳細',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.Br()
    ]
)

contact_contents = html.Div(
    [
        html.H5('問い合わせ先',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P(contact_address)
    ]
)

layout = html.Div(
    [
        algorithm_contents,
        html.P('作成中'),
        contact_contents,
    ]
)
