from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage


def pdf_to_txt(path):  # 引数にはPDFファイルパスを指定
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    laparams.detect_vertical = True  # Trueにすることで綺麗にテキストを抽出できる
    device = TextConverter(rsrcmgr, retstr, codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
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
    fstr = fstr.split('\n')
    return fstr


def convert_parsed_txt(fstr):
    list_strength = []
    for i in range(1, 35):
        tmp_strength = [x for x in fstr if x.startswith('{}.'.format(i))][0]
        strength_tmp = [x for x in tmp_strength.split(' ') if not x.startswith('{}.'.format(i)) and not x == '']
        unique_strength = set(strength_tmp)
        strength = list(unique_strength)[0]
        list_strength.append(strength)

    return list_strength


def check_parsed_txt(list_strength):
    status = False
    # TODO: list_strengthのチェックを追加
    if True:
        status = True
    return status
