#!/usr/bin/python
# -*- coding: UTF-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
import csv
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei'] 

ELB_DATA_FILE="elb-data.csv"

def read_from_csv(filename):
    '''
    IN: csv_file
    OUT: list:n*n
    '''
    info_arr = []
    csv_lines = csv.reader(open(filename, 'r', encoding="UTF-8"))
    for line in csv_lines:
        info_arr.append(line)
    return info_arr

if __name__ == "__main__":
    G = nx.DiGraph()
    elb_data = read_from_csv(ELB_DATA_FILE)
    for line in elb_data:
        if line[2] == '俄罗斯':
            line_color = 'blue'
            line[2] = ''
            G.add_edge(line[0], line[1], color=line_color, label=line[2])
        else:
            line_color = 'red'
            G.add_edge(line[0], line[1], color=line_color, label=line[2])

    '''
    for line in app_data:
        if line[2] == '俄罗斯':
            line_color = 'green'
            line[2] = ''
        else:
            line_color = 'orange'
    '''
    '''
    　　circular_layout：节点在一个圆环上均匀分布
    　　random_layout：节点随机分布
    　　shell_layout：节点在同心圆上分布
    　　spring_layout： 用Fruchterman-Reingold算法排列节点（样子类似多中心放射状）
    　　spectral_layout：根据图的拉普拉斯特征向量排列节点
    '''


    edges = G.edges()
    colors = [G[u][v]['color'] for u,v in edges]
    labels = dict([((u,v,),d['label'])for u,v,d in G.edges(data=True)])
    pos = nx.circular_layout(G)
    nx.draw_circular(G, with_labels=True,edges=edges, font_size=8, edge_color=colors, node_color='lightyellow', node_size = 1500,width=0.8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels =labels, font_size=6, label_pos=0.7,  font_color='r',rotate=True,clip_on=True)
    plt.show()
    plt.savefig("network.png")
    
