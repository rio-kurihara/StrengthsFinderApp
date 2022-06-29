import yaml
import os
import base64
import datetime
import pandas as pd
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage


def pdf_to_txt(path: str) -> list:
    """ PDF ファイル読み込み、パースしてテキストを返す

    Args:
        path (str): PDF ファイルのパス

    Returns:
        list: PDF をパースしたテキストを改行で区切ったリスト
    """

    resource_manager = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    laparams.detect_vertical = True  # Trueにすることで綺麗にテキストを抽出できる
    device = TextConverter(resource_manager, retstr, codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(resource_manager, device)
    maxpages = 0
    caching = True
    pagenos = set()

    fstr = ''
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, caching=caching, check_extractable=True):
        interpreter.process_page(page)

        str = retstr.getvalue()
        fstr += str
        break

    fp.close()
    device.close()
    retstr.close()

    list_text = fstr.split('\n')

    return list_text


def convert_parsed_txt(list_text: list) -> list:
    """ PDF をパースしたテキストを整形し、資質のみを抜き出して、ランク順にリストとして返す

    Args:
        list_text (str): 文字列のリスト。文字列は PDF ファイルをパースした、それぞれの箇所ごとのテキスト。
            例: 
            ['TARO YAMADA || dd-mm-yyyy',
            'TARO YAMADA', '', 'あなたのクリフトンストレングス34の結果 ',
            ...,
            '1. 1.  目標志向 ',
            '2. 2.  指令性 指令性 ',
            ...,
            '34. 34.  活発性 活発性',
            ...]

    Returns:
        list: ランキング順の資質リスト（1位~34位）
            例:
            ['目標志向', '指令性', ..., '活発性']
    """

    list_strengths = []

    try:
        for rank in range(1, 35):
            # list_text から資質部分のみを抜き出した文字列の例: '1. 1.  目標志向' or 1.1.  目標志向 目標志向
            extracted_strengths = [x for x in list_text if x.startswith('{}.'.format(rank))][0]
            # 資質リストを作成するために、資質名のみを抜き出した例: ['目標志向'] or ['目標志向', '目標志向']
            list_strength_names = [x for x in extracted_strengths.split(' ') if not x.startswith('{}.'.format(rank)) and not x == '']
            # list_strength_names が重複する場合があるため、 set をとって資質名を取得: ['目標志向']
            set_strength_name = set(list_strength_names)
            # 資質名の文字列を取得: '目標志向'
            strength_name = list(set_strength_name)[0]

            # 資質名をリストに追加
            list_strengths.append(strength_name)
    except:
        # パースが上手くいかなかった場合、list_strengths は空のリストのまま返す
        # TODO：エラーハンドリングうまいことやりたい
        pass
    return list_strengths


def check_parsed_txt(list_strength):
    if len(list_strength) == 34:
        status = True
    else:
        status = False
    return status


def create_fname_for_save_pdf(filename):
    # PDF を保存するファイル名を生成する: "現在日時＋アップロード時のファイル名.pdf"
    # 現在日時を取得
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    datetime_now = dt_now_jst_aware.strftime('%Y%m%d_%H%M%S_')

    # PDF を保存するパスを生成
    pdf_save_fname = datetime_now + filename

    return pdf_save_fname


def save_pdf_to_local(contents: str, save_path: str) -> None:
    """ バイナリデータを文字列に変換し、PDF ファイルとしてローカルに保存する

    Args:
        contents (str): ユーザーから送られてきたファイル（バイナリ）
        save_path (str): 保存先のパス
    """
    # str -> bytes
    bytes_base64 = contents.encode("utf8").split(b";base64,")[1]
    # Base64をデコード
    decoded_data = base64.decodebytes(bytes_base64)

    with open(save_path, "wb") as fp:
        fp.write(decoded_data)

    print('saved PDF file to local')


def save_pdf_to_gcs(bucket, pdf_local_path, upload_gcs_path):
    # ローカルに一時保存したPDFファイルを GCS にアップロードする
    blob = bucket.blob(upload_gcs_path)
    blob.upload_from_filename(pdf_local_path)
    print('saved PDF file to GCS')


def format_to_dataframe(list_strengths: list) -> pd.DataFrame:
    """
    PDF をパースしたリストをデータフレーム化する

    Args:
        list_strengths (list): 資質名のリスト（5個 or 34個 の要素）
    Return:
        pd.DataFrame:
    """
    df = pd.DataFrame(list_strengths)
    df.index = df.index + 1  # 1始まりにするため
    df = df.reset_index()
    df.columns = ['rank', 'strengths']

    return df


def is_pdf(filename: str) -> bool:
    # ファイルが PDF か否かを返す関数
    # ファイル名から拡張子を取得
    root_ext_pair = os.path.splitext(filename)
    ext = root_ext_pair[1]

    # PDF ファイルのみ True を返す
    if ext == '.pdf':
        return True
    else:
        return False


def is_not_input_empty(input_value: str) -> bool:
    # 入力データが空でなればTrue、空ならFalseを返す関数
    if input_value != ' ':
        return True
    else:
        return False


def is_exists_user(df_department: pd.DataFrame, input_value: str) -> bool:
    # すでに存在するユーザー名であればFalseを返す関数
    user_names = list(df_department['name'])
    if not input_value is user_names:
        return True
    else:
        return False


def is_correct_input_strengths(input_rows: list) -> bool:
    """
    ユーザーが入力した資質ランキングのテーブルが正しい形式になっているか確認
    正しければ True, そうでなければ False を返す

    Args:
        input_rows (list): dash_table.DataTable() から入力されたデータ
    """
    # 空のデータが含まれないか確認
    flag = [True if dict_row['strengths'] != '' else False for dict_row in input_rows]

    return all(flag)
