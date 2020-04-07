# -*- coding: utf-8 -*- 
"""
 @author: ‘ShawJoe‘
 @time: 2019/11/18 9:10
"""
from utils.common.init_func import Initiator
from utils.settings import experiment_path
import pickle
import json
import editdistance
import re
from remote.engineering.data_tools.SZTools import is_json


stopwords = ['the', 'at', 'in']


def affiliations_candidates():
    """所有的affiliation以及对应的候选集"""
    affiliation = pickle.load(open(experiment_path + "org/xlore/affiliation.dict", "rb"))
    n_gram = pickle.load(open(experiment_path + "org/xlore/n_gram.dict", "rb"))
    entity = pickle.load(open(experiment_path + "org/xlore/entity.dict", "rb"))
    uri = pickle.load(open(experiment_path + "org/xlore/uri.dict", "rb"))
    candidates = dict()
    count1 = 0
    set1 = set()
    for a in affiliation:
        candidates[a] = []
        if a in n_gram:
            for n in n_gram[a]:
                if n.strip() != "":
                    candidates[a].append({"Label": n})
                if n in entity:
                    if is_json(entity[n]):
                        obj1 = json.loads(entity[n])
                        if len(obj1["content"]) > 0:
                            for c in obj1["content"]:
                                if c["target"] == "instance":
                                    candidates[a].append(c)
                                elif c["target"] == "concept":
                                    candidates[a].append(c)
                                    for ins in c["Instances"]:
                                        candidates[a].append(ins)
                                    for h in c["Hyponymys"]:
                                        candidates[a].append(h)
    with open(experiment_path + "org/xlore/candidates.dict", 'wb') as f:
        pickle.dump(candidates, f, pickle.HIGHEST_PROTOCOL)


def lcs(str1, str2):
    """求两个字符串的最大公共子序列"""
    a = len(str1)
    b = len(str2)
    string_matrix = [[0 for _i in range(b+1)] for _j in range(a+1)]
    for i in range(1, a+1):
        for j in range(1, b+1):
            if i == 0 or j == 0:
                string_matrix[i][j] = 0
            elif str1[i-1] == str2[j-1]:
                string_matrix[i][j] = 1 + string_matrix[i-1][j-1]
            else:
                string_matrix[i][j] = max(string_matrix[i-1][j], string_matrix[i][j-1])
    index = string_matrix[a][b]
    res = [""] * index
    i = a
    j = b
    while i > 0 and j > 0:
        if str1[i-1] == str2[j-1]:
            res[index-1] = str1[i-1]
            i -= 1
            j -= 1
            index -= 1
        elif string_matrix[i-1][j] > string_matrix[i][j-1]:
            i -= 1
        else:
            j -= 1
    return ''.join(res)


def common_sub_string(str1, str2):
    """连续的最大子字符串"""
    len1 = len(str1)
    len2 = len(str2)
    record = [[0 for _i in range(len2 + 1)] for _j in range(len1 + 1)]  # 多一位
    max_mum = 0  # 最长匹配长度
    p = 0  # 匹配的起始位
    for i in range(len1):
        for j in range(len2):
            if str1[i] == str2[j]:  # 相同则累加
                record[i + 1][j + 1] = record[i][j] + 1
                if record[i + 1][j + 1] > max_mum:
                    max_mum = record[i + 1][j + 1]  # 获取最大匹配长度
                    p = i + 1  # 记录最大匹配长度的终止位置
    return str1[p - max_mum:p]


def str_clean(str1):
    """字符串的清洗操作"""
    r1 = u'[!"#$%&\'()*+,-./:;<=>?@]'
    str2 = re.sub(r1, '', str1.lower())
    str2 = re.sub(' +', '', str2.strip())
    return str2


def judge_logic(affiliation, candidate_list):
    lcs_list = []
    css_list = []
    # consequence = []
    list1 = []
    dict1 = dict()
    for u in candidate_list:
        if "Label" in u:
            entity = u["Label"].lower()
        elif "title" in u:
            entity = u["title"].lower()
        entity = normalize_org(entity)
        dict1[entity] = u
        aff = normalize_org(affiliation)
        list1.append(entity)
        s1 = lcs(entity, aff)
        lcs_list.append(s1)
        s2 = common_sub_string(aff, entity)
        css_list.append(s2)
    list3 = []
    for i in range(len(lcs_list)):
        if lcs_list[i] != "":
            # if lcs_list[i] == css_list[i]:
            #     consequence.append(lcs_list[i])
            list3.append((css_list[i], 1 - editdistance.eval(css_list[i], lcs_list[i]) / len(lcs_list[i])))
    list4 = sorted(list3, key=lambda k: k[1], reverse=True)
    # list2 = sorted(consequence, key=lambda k: len(k), reverse=True)
    max_score = list4[0][1]
    r = []
    for u in list4:
        if u[1] == max_score and u[0] in dict1:
            r.append(u[0])
    r = sorted(r, key=lambda k: len(k), reverse=True)
    if "title" in dict1[r[0]]:
        result = dict1[r[0]]["title"]
    else:
        result = dict1[r[0]]["Label"]
    return result


# def candidates_selection():
#     candidates = pickle.load(open(experiment_path + "org/xlore/candidates.dict", 'rb'))
#     count = 0
#     start = 30
#     dict1 = dict()
#     for c in candidates:
#         count += 1
#         if count % 10000 == 0:
#             log1.info(count)
#         result = judge_logic(c, candidates[c])
#         dict1[c] = result
#     with open(experiment_path + "org/xlore/result.dict", 'wb') as f:
#         pickle.dump(dict1, f, pickle.HIGHEST_PROTOCOL)


def candidates_selection():
    candidates = pickle.load(open(experiment_path + "org/xlore/candidates.dict", 'rb'))
    obj1 = json.load(open(experiment_path + "org/xlore/label_data.json"))
    dict1 = dict()
    for u in obj1:
        dict1[u["affiliation"]] = u
        if u["affiliation"] not in candidates:
            print(u["affiliation"])
    count = 0
    result_dict = dict()
    # for c in candidates:
    for c in dict1:
        result = judge_logic(c, candidates[c])
        result_dict[c] = result
        list1 = []
        for u in candidates[c]:
            if "title" in u:
                list1.append(u["title"])
            else:
                list1.append(u["Label"])
        if not organization_compare(result, dict1[c]["label"]):
            print(result, "####", dict1[c]["label"], "****", dict1[c]["affiliation"], "%%%%%", list1)
            count += 1
    log1.info(count)
    # with open(experiment_path + "org/xlore/result.dict", 'wb') as f:
    #     pickle.dump(result_dict, f, pickle.HIGHEST_PROTOCOL)


def normalize_org(org):
    r1 = u'[!"#$%&\'()*+,-./:;<=>?@]'
    str1 = re.sub(r1, ' ', org.lower())
    words = str1.split(" ")
    nw = []
    for w in words:
        if w not in stopwords:
            nw.append(w.strip())
    str1 = " ".join(nw)
    str1 = re.sub(' +', ' ', str1.strip())
    return str1.strip()


def organization_compare(org1, org2):
    """对机构进行比较"""
    str1 = normalize_org(org1)
    str2 = normalize_org(org2)
    # print(str1, "###########", str2)
    if str1 == str2:
        return True
    else:
        return False


def evaluate():
    """评价试验结果"""
    obj1 = json.load(open(experiment_path + "org/xlore/label_data.json"))
    result = pickle.load(open(experiment_path + "org/xlore/result.dict", 'rb'))
    count1 = 0
    for u in obj1:
        try:
            if str_clean(u["label"].lower()) == str_clean(result[u["affiliation"]].lower()):
                count1 += 1
            else:
                print(u["label"], "############", result[u["affiliation"]])
        except:
            print(u)
    log1.info(count1)
    log1.info(len(obj1))


def baseline_evaluate():
    """评价baseline的试验结果"""
    pass


def main(log):
    global log1
    log1 = log
    # affiliations_candidates()
    candidates_selection()
    # evaluate()
    a = organization_compare("UNIVERSITY OF CALIFORNIA SANTA BARBARE", "University of California, Santa Barbara")
    print(a)


if __name__ == '__main__':
    init = Initiator(main)
