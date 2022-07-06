import base64

import dash_bootstrap_components as dbc
from dash import html


def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')


def create_card(image_path: str, card_title: str, card_text: str, button_link: str) -> dbc.Card:
    """
    dash-bootstrap-components の card を作成する

    Args:
        image_path (str): オーバーレイする画像のファイルパス
        card_title (str): カードのタイトル
        card_text (str): カードのテキスト（説明文）
        button_link (str): カード内のボタンをクリックしたときに飛ぶリンク

    Return:
        dbc.Card
    """
    card = dbc.Card(
        [
            dbc.CardImg(
                src=b64_image(image_path),
                top=True,
                style={"opacity": 0.3},
            ),
            dbc.CardImgOverlay(
                dbc.CardBody(
                    [
                        html.H5(card_title, className="card-title"),
                        html.P(
                            card_text,
                            className="card-text",
                        ),
                        dbc.Button("Go",
                                   outline=True,
                                   color="secondary",
                                   href=button_link,
                                   external_link=True,
                                   className="me-1"),
                    ],
                ),
            ),
        ],
        style={"width": "14rem"},
    )
    return card


# ヘッダーの定義
welcome_message = html.H5(
    'ストレングスファインダーWebAppへようこそ',
    style=dict(padding="10px", borderLeft="5px #b31b1b solid")
)

header_contents = html.Div(
    [
        welcome_message,
        html.Br()
    ]
)

# アップロードを促すテキストの定義
recomend_upload = dbc.Alert(
    [
        html.H4("まずは受診結果をアップロードしましょう", className="alert-heading"),
        dbc.Button("アップロードフォームへ",
                   color="secondary",
                   href='/data/upload',
                   external_link=True,
                   className="me-1"),
        html.Hr(),
        html.P(
            "アップロード済みの方はダッシュボードへどうぞ↓",
            className="mb-0",
        ),
    ]
)

# ダッシュボードへ誘導するためのカードを定義
card_person = create_card(image_path='icon_images/person.png',
                          card_title='他の人の結果を見てみましょう',
                          card_text='アップロード済みのメンバーの受診結果を見ることができます',
                          button_link='/list')

card_team = create_card(image_path='icon_images/team.png',
                        card_title='共通の強みは何でしょうか',
                        card_text='足りない要素を見ることもできます',
                        button_link='/dashboard/team')

card_matching = create_card(image_path='icon_images/matching.png',
                            card_title='メンターメンティーマッチング',
                            card_text='メンター集合とメンティー集合を入力すると、組み合わせを提示します',
                            button_link='/dashboard/matching')

card_overview = create_card(image_path='icon_images/overview.png',
                            card_title='所属部署の傾向を見てみましょう',
                            card_text='各部署の傾向を見ることができます',
                            button_link='/overview')

card_setting = dbc.Card(
    [
        dbc.CardImg(
            src=b64_image('icon_images/setting.png'),
            top=True,
            style={"opacity": 0.3},
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H5('データの編集・削除はこちらから', className="card-title"),
                    html.P('', className="card-text"),
                    dbc.Button("編集",
                               outline=True,
                               color="secondary",
                               href='/data/edit',
                               external_link=True,
                               className="me-1"),
                    dbc.Button("削除",
                               outline=True,
                               color="secondary",
                               href='/data/delete',
                               external_link=True,
                               className="me-1"),
                ],
            ),
        ),
    ],
    style={"width": "14rem"},
)

row_content = dbc.Row(
    [
        dbc.Row(
            dbc.Col(recomend_upload, width={"size": 8})
        ),
        html.P(),
        html.P(),
        dbc.Row(
            [
                dbc.Col(card_person, width={"size": 2}),
                dbc.Col(card_overview, width={"size": 2}),
                dbc.Col(card_team, width={"size": 2}),
                dbc.Col(card_matching, width={"size": 2}),
            ]
        ),
        html.P(),
        html.P(),
        dbc.Row(
            dbc.Col(card_setting, width={"size": 2})
        ),
    ],
)

layout = html.Div(
    [
        header_contents,
        row_content
    ]
)
