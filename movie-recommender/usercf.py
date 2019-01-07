#coding = utf-8
'''
user cf main algo
author:walter
date:20190106
'''
from __future__ import division

import sys
sys.path.append('../utils')
import utils.reader as reader
import math
import operator

def base_contribution_score():
    return 1

def update_contribution_score(item_user_click_count):
    '''
    user cf user contribution score update v1
    :param item_user_click_count:
    :return:
    '''
    return 1/math.log10(1+item_user_click_count)

def update_two_contribution_score(click_time_one,click_time_two):
    '''
    user cf user contribution score update v2
    :param click_time_one:
    :param click_time_two:
    :return:
    '''
    delta_time = abs(click_time_one-click_time_two)
    norm_num = 60*60*24
    delta_time = delta_time/norm_num

    return 1/(1+delta_time)

def transfer_user_click(user_click):
    '''
    get item by user_click
    :param user_click: key userid,value:[itemid1,itemid2...]
    :return: dict,key itemid,value:[userid1,userid2...]
    '''
    item_click_by_user = {}
    for user in user_click.keys():
        item_list = user_click[user]
        for itemid in item_list:
            item_click_by_user.setdefault(itemid,[])
            item_click_by_user[itemid].append(user)

    return item_click_by_user

def cal_user_sim(item_click_by_user,user_click_time):
    '''
    get user cf sim info
    :param item_click_by_user: dict,key:itemid,value:[itemid1,itemid2...]
    :return: dict ,key itemid,value dict,value_key itemid_j,value_value simscore
    '''
    co_apppear = {}
    user_click_count = {}
    for itemid,user_list in item_click_by_user.items():
        for index_i in range(0,len(user_list)):
            user_i = user_list[index_i]
            user_click_count.setdefault(user_i,0)
            user_click_count[user_i] += 1

            if user_i+"_"+itemid not in user_click_time:
                click_time_one = 0
            else:
                click_time_one = user_click_time[user_i+"_"+itemid]

            for index_j in range(index_i+1,len(user_list)):
                user_j = user_list[index_j]

                if user_j + "_" + itemid not in user_click_time:
                    click_time_two = 0
                else:
                    click_time_two = user_click_time[user_j + "_" + itemid]

                co_apppear.setdefault(user_i,{})
                co_apppear[user_i].setdefault(user_j,0)
                #co_apppear[user_i][user_j] += base_contribution_score()
                #co_apppear[user_i][user_j] += update_contribution_score(len(user_list))
                co_apppear[user_i][user_j] += update_two_contribution_score(click_time_one,click_time_two)

                co_apppear.setdefault(user_j, {})
                co_apppear[user_j].setdefault(user_i, 0)
                #co_apppear[user_j][user_i] += base_contribution_score()
                #co_apppear[user_j][user_i] += update_contribution_score(len(user_list))
                co_apppear[user_j][user_i] += update_two_contribution_score(click_time_one,click_time_two)

    user_sim_info = {}
    user_sim_info_sorted = {}
    for user_i,relate_user in co_apppear.items():
        user_sim_info.setdefault(user_i,{})
        for user_j,cotime in relate_user.items():
            user_sim_info[user_i].setdefault(user_j,0)
            user_sim_info[user_i][user_j] = cotime/math.sqrt(user_click_count[user_i]*user_click_count
                                                             [user_j])

    for user in user_sim_info:
        user_sim_info_sorted[user] = sorted(user_sim_info[user].items(),key=operator.itemgetter(1),reverse=True)

    return user_sim_info_sorted


def cal_recom_result(user_click,user_sim):
    '''
    recom by usercf algo
    :param user_click: dict,key userid,value[itemid1,itemid2]
    :param user_sim: key userid,value [(itemid1,score),(itemid2,score)...]
    :return: key userid,value:dict,value_key itemid,value_value recom_score
    '''
    recom_result = {}
    topk_user = 3
    item_num = 5
    for user,item_list in user_click.items():
        tmp_dict = {}
        for item_id in item_list:
            tmp_dict.setdefault(item_id,1)
        recom_result.setdefault(user,{})
        for zuhe in user_sim[user][:topk_user]:
            userid_j,sim_score = zuhe
            if userid_j not in user_click:
                continue
            for itemid_j in user_click[userid_j][:item_num]:
                recom_result[user].setdefault(itemid_j,sim_score)

    return recom_result

def debug_user_sim(user_sim):
    '''
    print user sim result
    :param user_sim: key userid,value [(userid1,score),(userid2)...]
    :return:
    '''
    topk = 5
    fix_user= '1'
    if fix_user not in user_sim:
        print("invalid user")
        return

    for zuhe in user_sim[fix_user][:topk]:
        userid,score = zuhe
        print(fix_user+'\tsim_user'+userid+'\t'+str(score))

def debug_recom_result(item_info,recom_result):
    '''
    print recom result for user
    :param item_info: key itemid,value (title,genres)
    :param recom_result: key userid,value dict,value key itemidid,value value score
    :return:
    '''
    fix_user = '1'
    if fix_user not in recom_result:
        print("invalid user for recom result")
        return
    for itemid in recom_result['1']:
        if itemid not in item_info:
            continue
        recom_score = recom_result['1'][itemid]
        print('recom result'+','.join(item_info[itemid])+'\t'+str(recom_score))

def main_flow():
    user_click,user_click_time = reader.get_user_click('ml-latest-small/ratings.csv')
    item_info = reader.get_item_info('ml-latest-small/movies.csv')
    item_click_by_user = transfer_user_click(user_click)
    user_sim = cal_user_sim(item_click_by_user,user_click_time)
    debug_user_sim(user_sim)
    #print(user_sim['1'])
    recom_result = cal_recom_result(user_click,user_sim)
    debug_recom_result(item_info,recom_result)
    #print(recom_result["2"])


if __name__ == '__main__':
    main_flow()