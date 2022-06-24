import yaml
from flask import request
from apps import custom_error

# settings
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

accepted_ip = config['accepted_ip']


def check_ip(func):
    def wrapper(*args, **kwargs):
        if len(accepted_ip) == 0:  # 許可する IP リストが空の場合は制限なし
            return func(*args, **kwargs)
        elif request.remote_addr in accepted_ip:  # アクセスされた IP が、許可する IP リストに含まれていればアクセスok
            print('IP Check : OK')
            return func(*args, **kwargs)
        else:  # 許可している IP アドレス以外からのアクセスなら 403
            print("403")
            return custom_error.layout_403
    return wrapper
