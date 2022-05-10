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

    return list_strengths


def check_parsed_txt(list_strength):
    # TODO: list_strengths のチェックを追加
    if len(list_strength) == 34:
        status = True
    else:
        status = False
    return status
