def get_route_content():
    content = """
## ストレングスファインダー可視化Webアプリへようこそ
---  

"""
    return content


def get_top_content():
    content = """
## 受診済みの方の資質一覧  

### ※参照したい方の氏名を入力してください！(複数可)
赤  ： 実行力  (「何かを実行したい」「完遂したい」資質)  
黄色： 影響力  (「人に影響を与えたい」「人を動かしたい」資質)  
緑  ： 人間関係構築力  (「人とつながりたい」「関係性を築きたい」資質)  
青  ： 戦略的思考力  (「考えたい」「頭脳活動をしたい」資質)

"""
    return content


def get_summary_title_content():
    content = """
## 本部別の受診者数  
"""
    return content


def get_summary_content():
    content = """
## 各資質の合計スコア(TOP5のみ)  

赤  ： 実行力  (「何かを実行したい」「完遂したい」資質)  
黄色： 影響力  (「人に影響を与えたい」「人を動かしたい」資質)  
緑  ： 人間関係構築力  (「人とつながりたい」「関係性を築きたい」資質)  
青  ： 戦略的思考力  (「考えたい」「頭脳活動をしたい」資質)  

**※マイナス値は1人もTOP5にない資質**
"""
    return content


def get_person_content():
    content = '''
## 
## 相関  
任意の名前を1名入力すると、登録済みのメンバー全員との相関がみられます

'''
    return content


def get_person_content2():
    content = '''
## 次元圧縮  

グラフ内で拡大・縮小ができます

'''
    return content


def get_group_content():
    content = '''
####

選択した方達の全体傾向と個人の傾向を可視化
'''
    return content


def get_matching_content():
    content = '''
### マッチング
#### 2つの入力ボックスに対象の方の氏名を入力してください

使用例：TODO

'''
    return content
