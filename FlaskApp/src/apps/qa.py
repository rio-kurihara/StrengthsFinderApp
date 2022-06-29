import yaml
from dash import html

# settings.yaml の読み込み
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

algorithm_contents = html.Div(
    [
        html.H5('各機能のアルゴリズム詳細',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.Br()
    ]
)

google_form_url = config['contact_form']
contact_form = html.Iframe(src=google_form_url,
                           style={
                               "height": "700px",
                               "width": "700px"
                           }
                           )

contact_contents = html.Div(
    [
        html.H5('お問い合わせ',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        contact_form
    ]
)


layout = html.Div(
    [
        algorithm_contents,
        html.P('作成中'),
        contact_contents
    ]
)
