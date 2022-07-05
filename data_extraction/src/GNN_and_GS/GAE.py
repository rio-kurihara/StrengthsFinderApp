from attrdict import AttrDict
from networkx import from_scipy_sparse_matrix
from networkx import Graph
from networkx import relabel_nodes
from networkx import selfloop_edges
from networkx.linalg import adjacency_matrix
from pandas import DataFrame
from sklearn.manifold import TSNE
from torch import Tensor
from torch_geometric.nn import GCNConv, GAE, VGAE
from torch_geometric.utils import from_networkx
from torch_geometric.utils import train_test_split_edges
import argparse
import matplotlib.font_manager
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import pandas as pd
import pickle
import torch
import torch.nn.functional as F
import torch_geometric.transforms as T
import yaml

font_path = '/System/Library/Fonts/Hiragino Sans GB.ttc'
font_prop = matplotlib.font_manager.FontProperties(fname=font_path)

# parser = argparse.ArgumentParser()
# parser.add_argument('-c', '--config', default='./config.yaml')
kwargs = {'GAE': GAE, 'VGAE': VGAE}


def load_config(config_path: str) -> AttrDict:
    """config(yaml)ファイルを読み込む

    Parameters
    ----------
    config_path : string
        config fileのパスを指定する

    Returns
    -------
    config : attrdict.AttrDict
        configを読み込んでattrdictにしたもの
    """
    with open(config_path, 'r', encoding='utf-8') as fi_:
        return AttrDict(yaml.load(fi_, Loader=yaml.SafeLoader))


def make_dict(df: DataFrame) -> dict:
    """社員ノードと特徴量の変換辞書を作成する

    Parameters
    ----------
    df : pd.DataFrame
        今回の分析対象csvをread_csvしたdf
        ```
        >>> df.columns
        Index(['rank', '氏名1', '氏名2', ...])
        ```

    Returns
    -------
    dict
        社員名とストレングスのidとの対応辞書
    """
    syain = {k: num for num, k in enumerate(df.columns[1:])}
    syain_swap = {v: k for k, v in syain.items()}
    strength_set = set(df[syain.keys()][:5].values.flatten())
    strength = {k: num for num, k in enumerate(strength_set)}
    strength_swap = {v: k for k, v in strength.items()}
    return dict(
        syain=dict(
            str_num=syain,      # 社員名: id
            num_str=syain_swap  # id: 社員名
        ),
        strength=dict(
            str_num=strength,   # ストレングス: id
            num_str=strength_swap  # id: ストレングス
        )
    )


def make_feature_matrix(df: DataFrame,
                        num_dict: dict,
                        user_num: int = 32,
                        strength_num: int = 10,
                        name_list: list = None) -> Tensor:
    """特徴量行列を作成する

    Parameters
    ----------
    df: DataFrame
        今回の分析対象csvをread_csvしたdf
    num_dict: dict
        {'syain': {社員名: id}, 'strength': {ストレングス: id}}の辞書
    user_num: int
        何人のデータで処理するか
    strength_num: int
        評価するストレングスの数
    name_list: list or None
        name_listに社員を入れておくとその人たちで評価する

    Returns
    -------
    Tensor
        特徴量行列のtensor
    """
    if name_list is None:
        name_list = list(df.columns[1: user_num])
    strength = df[name_list][: strength_num].replace(
        num_dict['strength']['str_num']).to_numpy().T
    output = np.zeros((len(name_list) if name_list else user_num, len(
        num_dict['strength']['str_num'])), dtype=np.float32)
    for num, i in enumerate(strength):
        # 今回特徴量行列には重みをつけていない
        output[num, i] = 1.
    return torch.from_numpy(output)


def make_graph(df: DataFrame,
               num_dict: dict,
               user_num: int = 32,
               strength_num: int = 10,
               name_list: list = None) -> Graph:
    """networkxを用いてグラフのオブジェクトを生成

    Parameters
    ----------
    df: DataFrame
        今回の分析対象csvをread_csvしたdf
    num_dict: dict
        {'syain': {社員名: id}, 'strength': {ストレングス: id}}の辞書
    user_num: int
        何人のデータで処理するか
    strength_num: int
        評価するストレングスの数
    name_list: list or None
        name_listに社員を入れておくとその人たちで評価する

    G: Graph
        社員ネットワークのグラフオブジェクト w/o 特徴量行列
    """
    if name_list is None:
        name_list = list(df.columns[1: user_num + 1])
    user_num = len(name_list)
    name_dict = {k: num_dict['syain']['str_num'][k] for k in name_list}
    stre_dict = df[name_list][: strength_num].to_dict(orient='list')

    G_bipartite = Graph()
    G_bipartite.add_nodes_from(list(name_dict.values()), bipartite=1)

    for name, stre in stre_dict.items():
        name_num = num_dict['syain']['str_num'][name]
        for num, s in enumerate(stre[::-1]):
            G_bipartite.add_edge(name_num,
                                 str(num_dict['strength']['str_num'][s]),
                                 weight=num*0.3+1)

    mapping = {num: v for num, v in enumerate(G_bipartite.nodes)}
    A_mat = adjacency_matrix(G_bipartite)
    A_mat2 = A_mat**2
    # 隣接行列の二乗からグラフを作成
    G = from_scipy_sparse_matrix(A_mat2)
    # ノードのラベルを換える
    G = relabel_nodes(G, mapping)
    # 自己ループを削除
    G.remove_edges_from(selfloop_edges(G))
    # 社員だけを抜き出す
    G = G.subgraph(set(name_dict.values())).copy()
    return G


def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def cos_sim_matrix(matrix):
    """cos類似度を行列で一気に計算
    """
    d = matrix @ matrix.T
    norm = (matrix * matrix).sum(axis=1, keepdims=True) ** .5
    return d / norm / norm.T


def calc_cos(name: str, res: np.array, mapping: dict, mapping_swap: dict):
    target_vec = res[mapping_swap[name]]
    cos = np.apply_along_axis(lambda x: cos_sim(x, target_vec), 1, res)
    for num, i in enumerate(range(len(cos))):
        print(
            f'{mapping[np.argsort(cos)[::-1][i]]:<15}\t{np.sort(cos)[::-1][i]}')
        if num > 19:
            break


def plot_graph(G, dic, save_pos=False):
    plt.figure(figsize=(8, 8))
    if os.path.exists('./pos.pkl'):
        with open('./pos.pkl', mode='rb') as fi:
            pos = pickle.load(fi)
    else:
        pos = nx.spring_layout(G, k=0.1)
    edge_width = [(d['weight']*0.05) for (u, v, d) in G.edges(data=True)]
    nx.draw_networkx(G,
                     pos=pos,
                     node_size=200,
                     node_color='#A0CBE2',
                     width=edge_width,
                     edge_cmap=plt.cm.Blues,
                     edge_color='grey',
                     with_labels=False)
    data = nx.draw_networkx_labels(G,
                                   pos=pos,
                                   labels=dic,  # num->str
                                   font_size=4)
    for t in data.values():
        t.set_fontproperties(font_prop)
    plt.axis('off')
    plt.show()
    if save_pos:
        with open('./pos.pkl', mode='wb') as fo:
            pickle.dump(pos, fo)


def prefer_order(list_A: list, list_B: list, num_dict: dict, res_mat: np.array) -> tuple:
    """cos類似度行列から希望順をピックアップさせる
    """
    list_A_num = [num_dict['syain']['str_num'][name] for name in list_A]
    list_B_num = [num_dict['syain']['str_num'][name] for name in list_B]
    order_A_val = res_mat[list_A_num][:, list_B_num]  # list_Aから見たlist_Bのcos数値
    order_B_val = res_mat[list_B_num][:, list_A_num]  # list_Bから見たlist_Aのcos数値
    # srder_A_valの値に従い高い順にlist_Bを並べ替える
    order_A_name = np.array(list_B)[np.argsort(order_A_val)[:, ::-1]]
    # srder_B_valの値に従い高い順にlist_Aを並べ替える
    order_B_name = np.array(list_A)[np.argsort(order_B_val)[:, ::-1]]
    set_A = {a: ob for a, ob in zip(list_A, list(order_A_name))}
    set_B = {b: oa for b, oa in zip(list_B, list(order_B_name))}
    return (set_A, set_B)


class Encoder(torch.nn.Module):
    def __init__(self, in_channels, out_channels, model='GAE'):
        super(Encoder, self).__init__()
        self.model = model
        self.conv1 = GCNConv(in_channels, 2 * out_channels, cached=True)
        if self.model in ['GAE']:
            self.conv2 = GCNConv(2 * out_channels, out_channels, cached=True)
        elif self.model in ['VGAE']:
            self.conv_mu = GCNConv(2 * out_channels, out_channels, cached=True)
            self.conv_logstd = GCNConv(2 * out_channels, out_channels,
                                       cached=True)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        if self.model in ['GAE']:
            return self.conv2(x, edge_index)
        elif self.model in ['VGAE']:
            return self.conv_mu(x, edge_index), self.conv_logstd(x, edge_index)


def main(config_path):
    # settings
    conf = load_config(config_path)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    base_dir = conf['base_dir']
    strengths_path = base_dir + conf['strengths_path']

    # load data
    df = pd.read_csv(strengths_path)

    num_dict = make_dict(df)
    fm = make_feature_matrix(df, num_dict, **conf.feature_matrix)

    G = make_graph(df, num_dict, **conf.graph)
    preprocess_G = G.copy()
    for (u, v, d) in G.edges(data=True):
        if d["weight"] <= 6:    # 重みが6以下のエッジは削除する
            preprocess_G.remove_edge(u, v)
    G = preprocess_G

    # 下記の対応表がないとtorch geometric <-> 社員名の変換ができない
    mapping = {num: num_dict['syain']['num_str'][i]
               for num, i in enumerate(G.nodes)}
    # 一旦ここで画像が表示されるため止まる
    plot_graph(G, mapping, conf.save_pos)
    mapping_swap = {v: k for k, v in mapping.items()}
    data = from_networkx(G)
    # 特徴量行列
    data.x = fm
    # 標準化
    transform = T.NormalizeFeatures()
    data = transform(data)

    # GAE
    model = kwargs[conf.gae.model](
        Encoder(data.x.shape[1], conf.gae.dim, model=conf.gae.model)).to(device)
    data.train_mask = data.val_mask = data.test_mask = data.y = None

    # 今回全データでGAEを実行してしまう
    data = train_test_split_edges(data)
    x, train_pos_edge_index = data.x.to(
        device), data.train_pos_edge_index.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    def train():
        """train"""
        model.train()
        optimizer.zero_grad()
        z = model.encode(x, train_pos_edge_index)
        loss = model.recon_loss(z, train_pos_edge_index)
        if conf.gae.model in ['VGAE']:
            loss = loss + (1 / data.num_nodes) * model.kl_loss()
        loss.backward()
        optimizer.step()
        return loss.item()

    def test(pos_edge_index, neg_edge_index):
        """test"""
        model.eval()
        with torch.no_grad():
            z = model.encode(x, train_pos_edge_index)
        return model.test(z, pos_edge_index, neg_edge_index)

    # 学習実行
    print("start training")
    for epoch in range(1, conf.num_iter + 1):
        loss = train()
        auc, ap = test(data.test_pos_edge_index, data.test_neg_edge_index)
        if epoch % (conf.num_iter//10) == 0:
            print(
                f'Epoch: {epoch:02d}, Loss: {loss:.4f}, AUC: {auc:.4f}, AP: {ap:.4f}')

    @torch.no_grad()
    def plot_points():
        """学習済みモデルで学習データの分散表現をTSNEで2次元圧縮し、可視化する"""
        model.eval()
        res = model.encode(x, train_pos_edge_index)
        z = TSNE(n_components=2).fit_transform(res.cpu().numpy())

        plt.figure(figsize=(8, 8))
        plt.scatter(z[:, 0], z[:, 1], s=20)
        for num, [x_pos, y_pos] in enumerate(z):
            label = mapping[num]
            plt.annotate(
                label,
                (x_pos, y_pos),
                size=10,
                ha='center',
                fontproperties=font_prop
            )
        plt.axis('off')
        plt.show()
        return res.cpu().numpy()
    # 二次元圧縮と可視化
    res = plot_points()

    if conf.save_res:
        res_vec_save_path = base_dir + conf['res_vec_path']
        df_res = pd.DataFrame(res)
        df_res.to_csv(res_vec_save_path)

    if conf.save_res:
        res_cos_save_path = base_dir + conf['res_cos_path']
        df_res = pd.DataFrame(cos_sim_matrix(res))
        df_res.to_csv(res_cos_save_path)


if __name__ == '__main__':
    print('*** Start GAE ***')

    config_path = 'config.yaml'
    main(config_path)

    print('*** Finished GAE ***')
