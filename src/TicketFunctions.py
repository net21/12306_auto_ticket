 # -*- coding: utf-8 -*-

import urllib2
import cookielib
import urllib
import json
import time
import TicketFunctions
import Cookie
import sys
import requests 
import random
import os
import pickle
import re
import base64

train_stations = []

def getTicketCount(yp_info):
    """
    从余票字符串中获得余票数据。
    余票信息字符串如下：
    1018053038405095000010180500003032150000
    O055300502M0933000989174800019
    返回的是一个余票字典，并不是很全面，只取了我需要的类型，如下
    ZY 一等座
    ZE 二等座
    WZ 无座
    YZ 硬座
    YW 硬卧
    RW 软卧   
    """
    ticketCountDesc = "";
    # 本次列车您选择的席别尚有余票94张
    seatTicket = 0; # 所选席别余票多少张
    # 无座179张
    withoutSeatTicket = 0; # 无座票多少张
    
    seat = {"WZ":0, "YZ":0, "YW":0, "RW":0, "ZY":0, "ZE":0}
 
    i = 0;
    while i in range(len(yp_info)):
        # 1*****3179
        group = yp_info[i:i+10];

        # 1(席别)
        seatType = group[:1];
        # 硬座: 1, 硬卧: 3, 软卧: 4, 二等座:O, 一等座:M
        # 3179
        count = group[6:10];
        while len(count) > 1 and count[0:1] == "0": # count为0000的情况, count最终等于0
            count = count[1:1+len(count)];
        # 3179
        count = int(count);
        if seatType == "1":
            if count < 3000:
                seat['YZ'] = count
            else:
                seat['WZ'] = count - 3000
        elif seatType == "3":
            seat['YW'] = count
        elif seatType == "4":
            seat['RW'] = count
        elif seatType == "M":
            seat['ZY'] = count
        elif seatType == "O":
            if count < 3000:
                seat['ZE'] = count
            else:
                seat['WZ'] = count - 3000
        i = i + 10
    return seat

# 火车站点数据库初始化
# 全部站点, 数据来自: https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
# 每个站的格式如下:
# @bji|北京|BJP|beijing|bj|2   ---> @拼音缩写三位|站点名称|编码|拼音|拼音缩写|序号
def stationsInit(localfile="stations.js", proxies=None):
    global train_stations
    train_stations = []
    stationsFilepath = localfile
    if not os.path.exists(stationsFilepath):
        url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
        res, data = requests.get(url)
        if res and data.status_code == 200:
            data = data.text.decode("utf-8","ignore")
            output = open(stationsFilepath, 'wb')
            output.write(data);
            output.close( )
        else:
            return train_stations
    # 存在
    input = open(stationsFilepath, 'r')
    data = input.read();
    input.close( )
    
    if data.find("'@") != -1:
        station_names = data[data.find("'@"):]
    else:
        print(u"读取站点信息失败")
        return {}
    station_list = station_names.split('@')
    station_list = station_list[1:] # The first one is empty, skip it

    for station in station_list:
        items = station.split('|') # bjb|北京北|VAP|beijingbei|bjb|0
        train_stations.append({'abbr':items[0], 'name':items[1], 'telecode':items[2], 'pinyin':items[4]})
    return train_stations

# Convert station object by name or abbr or pinyin
def getTelcodeFromName(name):
    matched_stations = []
    for station in train_stations:
        if station['name'] == name or station['abbr'].find(name.lower()) != -1 or station['pinyin'].find(name.lower()) != -1:
            return station['telecode']
    return ""