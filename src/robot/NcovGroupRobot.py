import json
import re
import time

import requests

from src.robot.IdentifyNews import get_identify_result
from src.util.constant import USER_FOCUS_GROUP, SEND_SPLIT, USER_FOCUS_GROUP_NAME
from urllib import parse
from src.util.log import LogSupport

"""
针对微信群的功能函数
"""
ls = LogSupport()

def check_whether_identify(text):
    return re.match('^辟谣.+', text) != None

def check_whether_unidentify(text):
    return re.match('^停止辟谣.+', text) != None

def add_identify_group(conn, itchat, group):
    group_name = group.replace("辟谣", '')
    target_chatroom = itchat.search_chatrooms(group_name)
    succ = []
    failed = []
    if len(target_chatroom) > 0:
        chatroom_name = target_chatroom[0]['UserName']
        conn.sadd(USER_FOCUS_GROUP, chatroom_name)
        conn.sadd(USER_FOCUS_GROUP_NAME, group_name)
        succ.append(group_name)
    else:
        failed.append(group_name)
    return succ, failed

def cancel_identify_group(conn, itchat, group):
    group_name = group.replace("停止辟谣", '')
    target_chatroom = itchat.search_chatrooms(group_name)
    succ = []
    failed = []
    if len(target_chatroom) > 0:
        chatroom_name = target_chatroom[0]['UserName']
        conn.srem(USER_FOCUS_GROUP, chatroom_name)
        conn.srem(USER_FOCUS_GROUP_NAME, group_name)
        succ.append(group_name)
    else:
        failed.append(group_name)
    return succ, failed

def identify_news(text_list, itchat, group_name):
    reply = get_identify_result(text_list)
    if reply != None:
        itchat.send(reply, group_name)
        time.sleep(SEND_SPLIT)

def parse_identify_res(text, source):
    reply_text = '这个{}是{}，真实情况是: {}。不信的话你可以点这里看详情:{}'.format(text[0:15], source['result'], source['abstract'], source['oriurl'])
    return reply_text

def restore_group(conn, itchat):
    conn.delete(USER_FOCUS_GROUP)
    group_name = conn.smembers(USER_FOCUS_GROUP_NAME)
    succ_list = []
    failed_list = []
    for name in group_name:
        succ, failed = add_identify_group(conn, itchat, name)
        succ_list.extend(succ)
        failed_list.extend(failed)

    ls.logging.info("成功恢复的辟谣群聊:{},失败的:{}".format("，".join(succ_list), "，".join(failed_list)))