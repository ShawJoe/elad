# -*- coding: utf-8 -*-
"""
 @author: ‘ShawJoe‘
 @time: 2019/11/14 17:21
"""
from utils.common.init_func import Initiator
from utils.data_base_tools.database_connection import connect_org_na_db
from remote.engineering.data_tools.SZTools import normalize_affiliation_string
from remote.engineering.apis.geo_query.geo_tools.institution_detection import InstitutionDetection
from remote.engineering.data_tools.SZTools import check_contain_chinese, check_other_language
from utils.settings import experiment_path
import pickle
import re


org_na_db = connect_org_na_db()
papers_springer = org_na_db["papers_springer"]


def query_papers():
    """获取原始的affiliation数据，并统计其结果"""
    dict1 = dict()
    for paper in papers_springer.find({}).limit(100000):
        if "authors" in paper:
            for author in paper["authors"]:
                if "org" in author:
                    if not check_other_language(author["org"]):
                        key = normalize_affiliation_string(author["org"])
                        if key not in dict1:
                            dict1[key] = 0
                        else:
                            dict1[key] += 1
    with open(experiment_path + "org/xlore/affiliation.dict", 'wb') as f:
        pickle.dump(dict1, f, pickle.HIGHEST_PROTOCOL)


def affiliation_ngram():
    """对获得的affiliation做n-gram模型，只管英文的，为了对比试验公平"""
    dict1 = pickle.load(open(experiment_path + "org/xlore/affiliation.dict", 'rb'))
    dict2 = dict()
    idt = InstitutionDetection()
    for u in dict1.keys():
        if not check_other_language(u):  # 只含有英文的时候才进行n-gram抽取
            a = idt.find_inst(u)
            dict2[u] = get_ngrams(a[1], 3, "multiple")
    with open(experiment_path + "org/xlore/n_gram.dict", 'wb') as f:
        pickle.dump(dict2, f, pickle.HIGHEST_PROTOCOL)


def get_ngrams(query, n, gram_type="single"):
    """根据拆分获得的数据，确定是N就只取N个词"""
    ngrams = []
    if gram_type == "multiple":  # 除了取ngram之外还取n+1, n+2……
        if check_contain_chinese(query):  # 中文直接进行按字符处理
            query = str(query)
            for j in range(n, len(query) + 1):
                for i in range(0, len(query) - j + 1):
                    ngrams.append(query[i: i + j])
        else:
            list1 = re.split("""[:\s,"']""", query)  # 通过空格等进行分割
            for u in list1:
                if u.strip() == "":  # 去掉空格字符
                    list1.remove(u)
            if len(list1) < n:
                ngrams.append(query)
            else:
                for j in range(n, len(query) + 1):
                    for i in range(0, len(list1) - j + 1):
                        gram = ""
                        for u in list1[i: i + j]:
                            gram += " " + u
                        ngrams.append(gram.strip())
    else:  # 只取ngram和其本身，如果完全取不到则进行拆分
        if check_contain_chinese(query):  # 中文直接进行按字符处理
            query = str(query)
            for i in range(0, len(query) - n + 1):
                ngrams.append(query[i: i + n])
        else:
            list1 = re.split("""[:\s,"']""", query)  # 通过空格等进行分割
            if len(list1) < n:
                ngrams.append(query)
            else:
                for u in list1:
                    if u.strip() == "":  # 去掉空格字符
                        list1.remove(u)
                for i in range(0, len(list1) - n + 1):
                    gram = ""
                    for u in list1[i: i + n]:
                        gram += " " + u
                    ngrams.append(gram.strip())
        if query not in ngrams:
            ngrams.append(query)
    return ngrams


def test():
    dict1 = pickle.load(open(experiment_path + "org/xlore/n_gram.dict", 'rb'))
    log1.info(len(dict1))
    for u in dict1:
        print(u, dict1[u])
        break


def main(log):
    global log1
    log1 = log
    # query_papers()
    affiliation_ngram()
    # test()


if __name__ == '__main__':
    init = Initiator(main)
