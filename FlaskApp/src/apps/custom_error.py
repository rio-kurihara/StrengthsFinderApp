from dash import html


# 403 エラー
layout_403 = html.Div(
    [
        html.H5('アクセスが制限されています',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.Br(),
        html.P('社内ネットワークに接続した状態で再度アクセスしてください。')
    ]
)


# 404 エラー
layout_404 = html.Div(
    [
        html.H5('404 Page Not Found',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.Br(),
        html.P('ページが見つかりません。\nサイト上部のナビゲーションバーから各種リンクにアクセスしてください。')
    ]
)
