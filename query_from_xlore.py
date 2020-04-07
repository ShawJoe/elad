# -*- coding: utf-8 -*-
"""
 @author: ‘ShawJoe‘
 @time: 2019/11/14 17:21
"""
from utils.common.init_func import Initiator
from utils.settings import experiment_path
import requests
import traceback
import pickle
import os
import time
import json
import threading
from remote.engineering.data_tools.SZTools import is_json, read_files_from_dirctory
from remote.engineering.data_tools.SZTools import check_other_language


"""
========================================================================================================================
xlore的接口部分
========================================================================================================================
"""


def query_xlore_entity(term):
    """获取基本的实体信息"""
    url = "http://xxx.xx.xxx.xx:xxxx/query?searchTmp=" + term
    headers = {
        'contentType': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    result = ''
    try:
        req = requests.get(url, headers=headers)
        result = req.text
    except:
        log1.info(traceback.format_exc())
    return result


def query_xlore_uri(uri):
    """获取实体的uri信息"""
    url = "https://api.xlore.org/query?uri=" + uri
    headers = {
        'contentType': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    result = ''
    try:
        req = requests.get(url, headers=headers)
        result = req.text
    except:
        log1.info(traceback.format_exc())
    return result


"""
========================================================================================================================
下面是entity的查询
========================================================================================================================
"""


def combine_entities():
    """将上述的分别获取的entities数据进行合并"""
    list1 = read_files_from_dirctory(experiment_path + "org/xlore/entities/")
    dict1 = dict()
    log1.info(str(len(list1)) + "  entities files!")
    for path in list1:
        dict2 = pickle.load(open(path, "rb"))
        for u in dict2:
            if ("当天访问次数到达上限" not in dict2[u]) and (is_json(dict2[u])):
                dict1[u] = dict2[u]
    log1.info(str(len(dict1)) + "   entities included in cache file!")
    with open(experiment_path + "org/xlore/entity.dict", 'wb') as f:
        pickle.dump(dict1, f, pickle.HIGHEST_PROTOCOL)


def save_one_entity(uri, thread_name, number):
    """保存多线程下每完成n个的结果，包括最后一次完成不超过n个的结果"""
    name = "-" + thread_name + "-" + number + "-"
    filename1 = experiment_path + "org/xlore/entities/entity" + name + ".dict"
    count1 = 0
    while os.path.exists(filename1):  # 当这个文件路径存在的时候，就继续循环，直到给定的文件路径不存在
        count1 += 1
        name += str(count1)
        filename1 = experiment_path + "org/xlore/entities/entity" + name + ".dict"
    with open(filename1, 'wb') as f:  # 最终找到的这个是不存在的，直接保存
        pickle.dump(uri, f, pickle.HIGHEST_PROTOCOL)


def multithreading_query_entities(list1, thread_name):
    """查询的流程，尤其是注意查询中保存的文件名"""
    entity = dict()
    count1 = 0
    for u in list1:
        result = query_xlore_entity(u)
        if result != "":
            log1.info(thread_name + "  " + result)
            entity[u] = result
        count1 += 1
        n = 100  # 这里这么处理不容易出错！
        if count1 % n == 0:
            log1.info(count1)
            save_one_entity(entity, thread_name, str(int(count1 / n)))
            entity = dict()
    save_one_entity(entity, thread_name, str(int(count1 / n) + 1))
    log1.info(thread_name + "   End!")


def multi_query_entity():
    """多线程查找entity"""
    combine_entities()  # 先把已经抓取的数据合并到一个文件
    dict1 = pickle.load(open(experiment_path + "org/xlore/n_gram.dict", 'rb'))
    filename1 = experiment_path + "org/xlore/entity.dict"
    entity = dict()
    if os.path.exists(filename1):
        entity = pickle.load(open(filename1, "rb"))
        log1.info(len(entity))
    set1 = set()
    for key in dict1:
        for u in dict1[key]:
            if u not in entity:  # 只管不在的时候
                set1.add(u)
    log1.info(str(len(set1)) + "    entities need information!")
    list1 = list(set1)
    n = 10000  # 每组多少条
    threads = []
    for i in range(0, len(list1), n):
        log1.info(i)
        list2 = list1[i: i + n]
        t = threading.Thread(target=multithreading_query_entities, args=(list2, str(int(i / n))))
        threads.append(t)
    log1.info(len(threads))
    for t in threads:
        t.start()
        log1.info(str(t) + "    start!")


"""
========================================================================================================================
下面是uri的查询
========================================================================================================================
"""


def combine_uris():
    """将上述的分别获取的uri数据进行合并"""
    list1 = read_files_from_dirctory(experiment_path + "org/xlore/uris/")
    dict1 = dict()
    log1.info(str(len(list1)) + "  uri files!")
    for path in list1:
        dict2 = pickle.load(open(path, "rb"))
        for u in dict2:
            if ("当天访问次数到达上限" not in dict2[u]) and (is_json(dict2[u])):
                dict1[u] = dict2[u]
    log1.info(str(len(dict1)) + "   uris included in cache file!")
    with open(experiment_path + "org/xlore/uri.dict", 'wb') as f:
        pickle.dump(dict1, f, pickle.HIGHEST_PROTOCOL)


def save_one_uri(uri, thread_name, number):
    """保存多线程下每完成n个的结果，包括最后一次完成不超过n个的结果"""
    name = "-" + thread_name + "-" + number + "-"
    filename1 = experiment_path + "org/xlore/uris/uri" + name + ".dict"
    count1 = 0
    while os.path.exists(filename1):  # 当这个文件路径存在的时候，就继续循环，直到给定的文件路径不存在
        count1 += 1
        name += str(count1)
        filename1 = experiment_path + "org/xlore/uris/uri" + name + ".dict"
    with open(filename1, 'wb') as f:  # 最终找到的这个是不存在的，直接保存
        pickle.dump(uri, f, pickle.HIGHEST_PROTOCOL)


def multithreading_query_uris(list1, thread_name):
    """查询的流程，尤其是注意查询中保存的文件名"""
    uri = dict()
    count1 = 0
    for u in list1:
        result = query_xlore_uri(u)
        if result != "":
            log1.info(thread_name + "  " + result)
            uri[u] = result
        count1 += 1
        n = 100  # 这里这么处理不容易出错！
        if count1 % n == 0:
            log1.info(count1)
            save_one_uri(uri, thread_name, str(int(count1 / n)))
            uri = dict()
    save_one_uri(uri, thread_name, str(int(count1 / n) + 1))
    log1.info(thread_name + "   End!")


uri_set = set()   # uri的集合


def traverse_all_uris(obj1):
    """遍历属性对象中的所有的uri"""
    for u in obj1:
        if type(obj1[u]) is dict:
            traverse_all_uris(obj1[u])
        elif type(obj1[u]) is list:
            for m in obj1[u]:
                if type(m) is str:
                    uri_set.add('http://xlore.org/instance/'+m)
                elif type(m) is dict:
                    traverse_all_uris(m)
                else:
                    log1.info(m)
        elif type(obj1[u]) is str:
            if u.lower().strip() == "uri":
                uri_set.add(obj1[u])
        else:
            log1.info(u)
            log1.info(obj1[u])
    return uri_set


def multi_query_uri():
    """多线程查询，将任务分配到各个多线程，然后进行查询，并保存为文件"""
    combine_uris()  # 先执行一下合并数据，保证uri的数据是最新的
    entity = pickle.load(open(experiment_path + "org/xlore/entity.dict", 'rb'))
    uri = pickle.load(open(experiment_path + "org/xlore/uri.dict", "rb"))
    for key in entity:
        if not check_other_language(key):  # 只有英语的才去查询，其他语言的不管
            if is_json(entity[key]):
                traverse_all_uris(json.loads(entity[key]))
    log1.info(str(len(uri_set)) + "   uri_set length!")
    list1 = []
    for u in uri_set:
        if u not in uri:
            list1.append(u)
    print(len(list1))
    n = 400  # 每组多少条
    threads = []
    for i in range(0, len(list1), n):
        log1.info(i)
        list2 = list1[i: i + n]
        t = threading.Thread(target=multithreading_query_uris, args=(list2, str(int(i / n))))
        threads.append(t)
    log1.info(len(threads))
    for t in threads:
        t.start()
        log1.info(str(t) + "    start!")
        # t.join()


def check_null_affilations():
    """检查并补充affiliation完全找不到对应的entity的"""
    affiliation = pickle.load(open(experiment_path + "org/xlore/affiliation.dict", 'rb'))
    n_gram = pickle.load(open(experiment_path + "org/xlore/n_gram.dict", 'rb'))
    entity = pickle.load(open(experiment_path + "org/xlore/entity.dict", "rb"))
    list1 = []
    count1 = 0
    for a in affiliation:
        if a in n_gram:
            count1 += 1
            flag = False
            for n in n_gram[a]:
                if n in entity:
                    obj1 = json.loads(entity[n])
                    if len(obj1["content"]) != 0:
                        flag = True
                        break
            if not flag:
                # print(a, n_gram[a])
                list1.append(a)
    log1.info(count1)
    log1.info(len(list1))
    with open(experiment_path + "org/xlore/affiliations_re_ngram.dict", 'wb') as f:
        pickle.dump(list1, f, pickle.HIGHEST_PROTOCOL)


def main(log):
    global log1
    log1 = log
    # multi_query_entity()
    # combine_entities()
    # multi_query_uri()
    # combine_uris()
    check_null_affilations()


if __name__ == '__main__':
    init = Initiator(main)
