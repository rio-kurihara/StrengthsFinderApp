import pandas as pd
from dash import html


header_contents = html.Div(
    [
        html.H5('アップロードが完了しました',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('マッチング機能のみ、反映に5分程かかります。')
    ]
)

layout = html.Div(
    [
        header_contents
    ]
)
