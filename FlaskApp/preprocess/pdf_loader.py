from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def convert_pdf_to_txt(path):  # 引数にはPDFファイルパスを指定
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    laparams.detect_vertical = True  # Trueにすることで綺麗にテキストを抽出できる
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
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
    return fstr


def format_strength(txt):
    txt1 = txt.split('\n')
    list_strength = []
    dict_results = {'status': None,
                    'error_message': None,
                    'result': None}
    try:
        for i in range(1, 35):
            tmp_strength = [
                x for x in txt1 if x.startswith('{}.'.format(i))][0]
            strength_tmp = [x for x in tmp_strength.split(
                ' ') if not x.startswith('{}.'.format(i)) and not x == '']
            assert len(set(strength_tmp)) == 1
            strength = list(set(strength_tmp))[0]
            list_strength.append(strength)
        dict_results['status'] = True
        dict_results['result'] = list_strength
    except:
        dict_results['status'] = False
        dict_results['error_message'] = 'PDFの読み込みに失敗しました。お手数ですが手動入力の程お願い致します。'
    return dict_results
