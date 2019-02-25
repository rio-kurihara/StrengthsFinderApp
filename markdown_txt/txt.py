def get_top_content(port):
    content = """
## [Top](http://192.168.99.157:{}/)

## DashBoard  

* [Summary](http://192.168.99.157:55449/dashboard/summary)  
* [Person](http://192.168.99.157:55449/dashboard/person)  
* [Group](http://192.168.99.157:55449/dashboard/group)  

## Data Upload  

* これから作るよ  

""".format(port)
    return content

def get_summary_content():
    content = """
---  
---  
## 資質の平均順位(昇順表示)  

**選択した本部内メンバーの資質の平均順位を表示します**  

赤  ： 実行力  (「何かを実行したい」「完遂したい」資質)  
黄色： 影響力  (「人に影響を与えたい」「人を動かしたい」資質)  
緑  ： 人間関係構築力  (「人とつながりたい」「関係性を築きたい」資質)  
青  ： 戦略的思考力  (「考えたい」「頭脳活動をしたい」資質)

グループ分けの意味の詳細は[こちら](https://heart-lab.jp/strengthsfinder/sftheme4groups/)
"""
    return content

def get_person_content():
    content = '''
---  
---  
# 順位相関(降順表示)  

- 選択した方とそれ以外の方との順位相関を降順表示します
'''
    return content

def get_group_content():
    content = '''
---  
---  
# グループの傾向把握

- 選択した方達の全体傾向と個人の傾向を可視化
'''
    return content