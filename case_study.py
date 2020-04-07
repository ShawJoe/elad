# -*- coding: utf-8 -*-
"""
 @author: ‘ShawJoe‘
 @time: 2020/02/21 17:21
"""
from utils.common.init_func import Initiator
import pickle
from utils.settings import experiment_path
from itertools import combinations
from collections import Counter
import json


def ranking_papers():
    """论文数量的排名"""
    type_scholars = pickle.load(open(experiment_path + "job_hopping/original_data/type_scholars.dict", 'rb'))
    papers_geo_all = pickle.load(open(experiment_path + "job_hopping/original_data/papers_geo_all.dict", 'rb'))
    scholars = pickle.load(open(experiment_path + "job_hopping/original_data/scholars.dict", 'rb'))
    print(len(type_scholars.keys()))
    list1 = []
    for s in type_scholars:
        if s == "数据挖掘":
            for u in type_scholars[s]:
                list1.append(u[3])
    print(len(list1))
    list2 = []
    for u in list1:
        for p in scholars[u]["pubs"]:
            list2.append(p["i"])
    print(len(list2))
    dict1 = dict()
    for u in list2:
        if u in papers_geo_all and "authors" in papers_geo_all[u]:
            set1 = set()
            for a in papers_geo_all[u]["authors"]:
                if "org_id" in a and a["org_id"] != "":
                    set1.add(a["org_id"])
            for o in set1:
                if o not in dict1:
                    dict1[o] = 0
                dict1[o] += 1
    list1 = sorted(dict1.items(), key=lambda x: x[1], reverse=True)
    orgs = pickle.load(open(experiment_path + "job_hopping/original_data/orgs.dict", 'rb'))
    list3 = []
    for u in list1[:10]:
        print(orgs[u[0]]["name_en"], u[1])
        list3.append(u[0])
    edges_list = []
    for u in list2:
        if u in papers_geo_all and "authors" in papers_geo_all[u]:
            set1 = set()
            for a in papers_geo_all[u]["authors"]:
                if "org_id" in a and a["org_id"] != "" and a["org_id"] in list3:
                    set1.add(a["org_id"])
            for p in combinations(set1, 2):
                if p[0] > p[1]:
                    edges_list.append((p[0], p[1]))
                else:
                    edges_list.append((p[1], p[0]))
    nodes = []
    edges = []
    nodes_weight = dict()
    for u in Counter(edges_list).most_common():
        edges.append({"sourceID": orgs[u[0][0]]["name_en"], "targetID": orgs[u[0][1]]["name_en"], "weight": u[1]})
        if u[0][0] not in nodes_weight:
            nodes_weight[u[0][0]] = 0
        if u[0][1] not in nodes_weight:
            nodes_weight[u[0][1]] = 0
        nodes_weight[u[0][0]] += 1
        nodes_weight[u[0][1]] += 1
    for u in nodes_weight:
        nodes.append({"id": orgs[u]["name_en"], "name": orgs[u]["name_en"], "size": nodes_weight[u]})
    obj1 = {"nodes": nodes, "edges": edges}
    file1 = open(experiment_path + "org/xlore/case_study/network.json", 'w')
    file1.write(json.dumps(obj1))
    file1.close()


def main(log):
    global log1
    log1 = log
    ranking_papers()


if __name__ == '__main__':
    init = Initiator(main)
