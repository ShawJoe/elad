# -*- coding: utf-8 -*-
"""
 @author: ‘ShawJoe‘
 @time: 2019/11/22 20:43
"""
from utils.common.init_func import Initiator
from utils.data_base_tools.database_connection import connect_org_na_db
from remote.engineering.data_tools.SZTools import check_other_language
from utils.settings import experiment_path, image_path
import pickle
import json
from remote.engineering.data_tools.SZTools import is_json
from remote.paper.paper_tools.visual_related.curve_fitting import sta_bar_norm_pic


org_na_db = connect_org_na_db()
papers_springer = org_na_db["papers_springer"]


def statistics_papers_affiliations():
    """统计论文中出现了多少次的affiliation"""
    count1 = 0
    set1 = set()
    for paper in papers_springer.find({}).limit(100000):
        if "authors" in paper:
            for author in paper["authors"]:
                if "org" in author:
                    if not check_other_language(author["org"]):
                        count1 += 1
                        set1.add(author["org"])
    log1.info(count1)
    log1.info(len(set1))


def statistic_baseline():
    """统计baseline相关的结果"""
    result_baseline = org_na_db["result_baseline"]
    list1 = []
    set1 = set()
    log1.info(result_baseline.find({}).count())
    count1 = 0
    for u in result_baseline.find({}):
        count1 += 1
        if "stm_org" in u:
            for org in u["stm_org"]:
                list1.append(org)
                set1.add(org)
        else:
            print(u)
    log1.info(count1)
    log1.info(len(list1))
    log1.info(len(set1))
    log1.info(len(set1) / count1)


count_uris = []


def traverse_count_uri_number(obj1):
    """遍历属性对象中的所有的uri"""
    for u in obj1:
        if type(obj1[u]) is dict:
            traverse_count_uri_number(obj1[u])
        elif type(obj1[u]) is list:
            for m in obj1[u]:
                if type(m) is str:
                    count_uris.append('http://xlore.org/instance/'+m)
                elif type(m) is dict:
                    traverse_count_uri_number(m)
                else:
                    log1.info(m)
        elif type(obj1[u]) is str:
            if u.lower().strip() == "uri":
                count_uris.append(obj1[u])
        else:
            pass
    return count_uris


def involved_data():
    """试验中所涉及的数据的统计"""
    affiliation = pickle.load(open(experiment_path + "org/xlore/affiliation.dict", "rb"))
    log1.info(len(affiliation))  # 包含了其他字符的
    n_gram = pickle.load(open(experiment_path + "org/xlore/n_gram.dict", "rb"))
    log1.info(len(n_gram))
    count1 = 0
    list1 = []
    f2_words = []
    for n in n_gram:
        count1 += len(n_gram[n])
        f2_words.append(len(n_gram[n]))
        list1.extend(n_gram[n])
    log1.info(count1)
    log1.info(count1 / len(n_gram))
    log1.info(len(set(list1)))
    l = sorted(f2_words)
    log1.info(l[0])
    log1.info(l[-1])
    citation_all_info = {
        "path": image_path + 'f2_words.png',
        "title": "f2_words",
        "xlabel": "Number of Scholars",
        "ylabel": "Citations",
    }
    sta_bar_norm_pic(f2_words, citation_all_info)
    entity = pickle.load(open(experiment_path + "org/xlore/entity.dict", "rb"))
    log1.info(len(entity))
    set1 = set()
    count2 = 0
    h_results = []
    entity_uri = []
    for n in entity:
        if is_json(entity[n]):
            obj1 = json.loads(entity[n])
            start = len(count_uris)
            traverse_count_uri_number(obj1)
            end = len(count_uris)
            count2 += len(obj1["content"])
            h_results.append(len(obj1["content"]))
            entity_uri.append(end - start)
            if len(obj1["content"]) > 0:
                for c in obj1["content"]:
                    try:
                        set1.add(c["uri"])
                    except:  # list类型的就不管
                        pass
    l = sorted(h_results)
    log1.info(l[0])
    log1.info(l[-1])
    citation_all_info = {
        "path": image_path + 'h_results.png',
        "title": "h_results",
        "xlabel": "Number of Scholars",
        "ylabel": "Citations",
    }
    sta_bar_norm_pic(h_results, citation_all_info)
    l = sorted(entity_uri)
    log1.info(l[0])
    log1.info(l[-1])
    citation_all_info = {
        "path": image_path + 'entity_uri.png',
        "title": "entity_uri",
        "xlabel": "Number of Scholars",
        "ylabel": "Citations",
    }
    sta_bar_norm_pic(entity_uri, citation_all_info)
    log1.info(count2 / len(n_gram))
    log1.info(len(set1))
    uri = pickle.load(open(experiment_path + "org/xlore/uri.dict", "rb"))
    log1.info(len(uri))
    log1.info(len(count_uris))
    print(len(set(count_uris)))
    log1.info(len(count_uris) / len(n_gram))
    visualize_involved_data(f2_words, h_results, entity_uri)


def visualize_involved_data(f2_words, h_results, entity_uri):
    """可视化所涉及到的数据"""
    pass


def candidate_statistic():
    """候选集相关的统计"""
    candidates = pickle.load(open(experiment_path + "org/xlore/candidates.dict", 'rb'))
    log1.info(len(candidates))
    count1 = 0
    count2 = 0
    for c in candidates:
        count1 += len(candidates[c])
        for u in candidates[c]:
            if "uri" in u:
                count2 += 1
    log1.info(count1)
    log1.info(count1 / len(candidates))
    log1.info(count2)
    log1.info(count2 / len(candidates))
    log1.info(count1 - count2)
    log1.info((count1 - count2) / len(candidates))


def main(log):
    global log1
    log1 = log
    statistic_baseline()
    # involved_data()
    # candidate_statistic()


if __name__ == '__main__':
    init = Initiator(main)
