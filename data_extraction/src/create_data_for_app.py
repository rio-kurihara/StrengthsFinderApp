import os
from logging import getLogger

import pandas as pd
import yaml

from GNN_and_GS import GAE
# from src.GNN_and_GS import GAE  # pytest 時のみこちらでインポートする

logger = getLogger(__name__)


def convert_vertical(df: pd.DataFrame) -> pd.DataFrame:
    """ 資質ランキングデータを横持ちから縦持ちに変換する

    Args:
        df (pd.DataFrame): 全メンバーの資質ランキングデータ（横持ち）

    Returns:
        pd.DataFrame: 全メンバーの資質ランキングデータ（経持ち）
    """
    # ランクのリストを取得（[1, 2, ..., 34]）
    list_ranks = df.columns
    # 格納用に空のデータフレームを作成
    df_member = pd.DataFrame()

    for _rankN in list_ranks:
        # N 位の全員分の資質
        rankN_strengths = pd.DataFrame(df[_rankN])
        # 列名の設定および "rank" 列を追加し、データフレームを整形する
        rankN_strengths.columns = ['strengths']
        rankN_strengths['rank'] = _rankN
        # 格納用データフレームに追加していく
        df_member = pd.concat([df_member, rankN_strengths], axis=0)

    df_member.index.name = 'user_name'
    df_member.reset_index(inplace=True)

    return df_member


def split_top5_and_all34(df: pd.DataFrame) -> pd.DataFrame:
    """ 全メンバーの資質ランキングデータを、TOP5 のデータと全資質 (34位まで) のデータに分割
    ※上位 5 位までしか結果を出していない人は全資質用のデータから除外する

    Args:
        df (pd.DataFrame): 全メンバーの資質ランキングデータ（縦持ち）

    Returns:
        pd.DataFrame: [description]
    """
    # 1~5 位のデータを抽出
    df_top5 = df[df['rank'] <= 5]
    df_top5.reset_index(inplace=True)

    # NULL があるユーザー＝ 5 位までしか結果を入力していないユーザーを抽出
    drop_users = df[df['strengths'].isnull()].index

    # 1~34 位のデータを作成
    df_all34 = df.drop(drop_users)
    df_all34.reset_index(inplace=True)

    return df_top5, df_all34


def check_top5_null(df: pd.DataFrame) -> pd.DataFrame:
    """ 1~5位 のデータが NULL ならそのユーザーを削除する

    Args:
        df (pd.DataFrame): 全メンバーの資質ランキングデータ（縦持ち）

    Returns:
        pd.DataFrame: 上記条件に該当するメンバーを除外した、資質ランキングデータ（縦持ち）
    """
    # 1~5 位までのデータを抽出
    df_top5 = df[df['rank'] <= 5]

    if any(df_top5['strengths'].isnull()):
        # 除外するユーザー名をリストで取得
        sr_null_user_names = df_top5[df_top5['strengths'].isnull()]['user_name']
        list_null_user_unique = set(list(sr_null_user_names))
        drop_index = df.index[df['user_name'].isin(list_null_user_unique)]
        # 該当するユーザーの行を全て削除
        df = df.drop(drop_index, axis=0)
        # インデックスを振り直す
        df = df.reset_index(drop=True)

        logger.warning('Deleted user name {} because the TOP5 data contained NULL'.format(list_null_user_unique))

    return df


def calc_corr(df: pd.DataFrame) -> pd.DataFrame:
    """ ユーザー同士の相関を計算してラベルと一緒に返す

    Args:
        df (pd.DataFrame): 全メンバーの資質ランキングデータ（縦持ち, 1~34 位まで）

    Returns:
        pd.DataFrame: 相関行列
    """
    df = df.set_index(keys="user_name")

    df_pivot = df[['strengths', 'rank']].pivot(columns='strengths')
    df_pivot = df_pivot.fillna(0)
    df_corr = df_pivot.T.corr()
    df_corr = df_corr.sort_index()
    df_corr = df_corr.round(2)

    return df_corr


def main():
    print('*** start preprocess ***')

    # settings.yaml の読み込み
    with open('settings.yaml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # パスの設定
    base_dir = config['base_dir']
    strengths_path = base_dir + config['strengths_path']
    demogra_path = base_dir + config['demogra_path']
    all34_exsits_null_path = base_dir + config['all34_exsits_null_path']
    top5_path = base_dir + config['top5_path']
    all34_path = base_dir + config['all34_path']
    all34_corr_path = base_dir + config['all34_corr_path']

    # GCS からデータを読み込む
    df_member_org = pd.read_csv(strengths_path, index_col='rank').T
    df_member_demogura = pd.read_csv(demogra_path)

    # データの整形
    # 横持ちに変換
    df_vertical = convert_vertical(df_member_org)
    # TOP5のデータがNULLでないかチェック
    df_vertical = check_top5_null(df_vertical)

    # チーム名を追加
    df_vertical_add_demogura = pd.merge(
        df_vertical, df_member_demogura,
        how='left', left_on=['user_name'], right_on=['name']
    )
    df_vertical_add_demogura = df_vertical_add_demogura.drop('name', axis=1)
    df_vertical_add_demogura = df_vertical_add_demogura.set_index('user_name')

    # TOP5のデータとALL34のデータに分割(上位5つしか結果を出していない人はALL34から除外)
    df_top5, df_all34 = split_top5_and_all34(df_vertical_add_demogura)

    # Scoreの追加
    dict_rank_to_score = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
    df_top5['score'] = df_top5[['rank']].applymap(dict_rank_to_score.get)
    # TODO: pandas の SettingWithCopyWarning
    # df_top5_copy = df_top5.copy()
    # df_top5_copy.loc[:, 'score'] = df_top5[['rank']].applymap(dict_rank_to_score.get)

    # 相関行列
    df_corr_all34 = calc_corr(df_all34)
    df_corr_all34.index.name = 'user_name'

    # run GAE
    GS_config_path = config['GS_config_path']
    GAE.main(GS_config_path)

    # saving
    df_vertical = df_vertical.fillna('nan')
    df_vertical.to_csv(all34_exsits_null_path, index=False)
    df_top5.to_csv(top5_path, index=False)  # TODO
    # df_top5_copy.reset_index().to_csv(top5_path, index=False)
    df_all34.to_csv(all34_path, index=False)
    df_corr_all34.to_csv(all34_corr_path)

    print('saving done')


if __name__ == "__main__":
    main()
