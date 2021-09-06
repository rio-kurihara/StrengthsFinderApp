import os

from logging import getLogger

import pandas as pd
import yaml
from analytics.GNN_and_GS import GAE

logger = getLogger(__name__)


def _convert_vertical(df):
    # 縦もちに変換
    list_rank = df.columns
    df_member = pd.DataFrame()

    for _rank in list_rank:
        tmp = pd.DataFrame(df[_rank])
        tmp.columns = ['strengths']
        tmp['rank'] = _rank
        df_member = pd.concat([df_member, tmp], axis=0)
    return df_member


def _split_top5_and_all34(df):
    """
    TOP5のデータとALL34のデータに分割(上位5つしか結果を出していない人はALL34から除外)
    """
    df_top5 = df[df['rank'] <= 5]
    list_drop = df[df['strengths'].isnull()].index
    df_all34 = df.drop(list_drop)
    return df_top5, df_all34


def _check_top5_null(df):
    """
    TOP5のデータがNULLならその人は削除(warning)
    """
    df_top5_tmp = df[df['rank'] <= 5]
    if any(df_top5_tmp['strengths'].isnull()):
        logger.warning('top5_null_exists it is deleted')
        list_drop = df_top5_tmp[df_top5_tmp['strengths'].isnull()].index
        df = df.drop(list_drop)

    return df


def calc_corr(df):
    """
    相関を計算してラベルと一緒に返す
    """
    df_pivot = df.pivot(columns='strengths')
    df_pivot = df_pivot.fillna(0)
    df_corr = df_pivot.T.corr()
    df_corr = df_corr.sort_index()
    return df_corr


def main():
    print('*** start preprocess ***')
    with open('settings.yaml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # load data
    # df_mst = pd.read_csv('{}/mst/mst_category.csv'.format(dir_data))
    df_member_org = pd.read_csv(
        config['data_path']['strengths_csv'], index_col='rank').T
    df_member_demogura = pd.read_csv(config['data_path']['demogra_csv'])

    # データの整形
    # 横持ちに変換
    df_vertical = _convert_vertical(df_member_org)

    # 所属本部を追加
    df_vertical_add_demogura = pd.merge(df_vertical.reset_index(
    ), df_member_demogura, how='left', left_on=['index'], right_on=['name']).drop('name', axis=1)
    df_vertical_add_demogura = df_vertical_add_demogura.set_index('index')

    # TOP5のデータがNULLでないかチェック
    df_vertical_add_demogura = _check_top5_null(df_vertical_add_demogura)

    # TOP5のデータとALL34のデータに分割(上位5つしか結果を出していない人はALL34から除外)
    df_top5, df_all34 = _split_top5_and_all34(df_vertical_add_demogura)

    # Scoreの追加
    dict_rank_to_score = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
    df_top5['score'] = df_top5[['rank']].applymap(dict_rank_to_score.get)

    # 相関行列
    # df_corr_top5 = calc_corr(df_top5[['strengths', 'rank']])
    df_corr_all34 = calc_corr(df_all34[['strengths', 'rank']])
    df_corr_all34.index.name = 'index'

    # create directory
    tmp_dir = os.path.dirname(config['data_path']['all34_exsits_null'])
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    del tmp_dir
    
    # saving
    df_vertical = df_vertical.fillna('nan')
    df_vertical.reset_index().to_csv(
        config['data_path']['all34_exsits_null'], index=False)
    df_top5.reset_index().to_csv(config['data_path']['top5'], index=False)
    df_all34.reset_index().to_csv(config['data_path']['all34'], index=False)
    # df_corr_top5.to_csv('{}/for_plot/df_corr_top5.csv'.format(dir_data))
    df_corr_all34.to_csv(config['data_path']['all34_corr'])

    # run GAE
    GAE.main(config['data_path']['GS_config'])

    print('saving done')


if __name__ == "__main__":
    main()
