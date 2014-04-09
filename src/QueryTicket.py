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

class QueryTicket:

    def __init__(self, proxies=None):

        self.host_ips=['219.145.161.13',
        '121.205.7.44',
        'kyfw.12306.cn',
        '113.207.63.142',
        '219.145.161.11',
        '42.202.148.46',
        '163.177.242.54'
        ]

        self.host_ip_index = 0

        self.proxies = proxies
        self.session = requests.Session()
        self.User_Agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48 Safari/537.36'
        self.headers = {'User-Agent':self.User_Agent, 
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Connection': 'keep-alive',
                'Host':'kyfw.12306.cn',
                'Referer':'https://kyfw.12306.cn/otn/leftTicket/init'}


    def getUrl(self, url, timeout=8):
        try:
            return 1, self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False, timeout=timeout )
        except requests.exceptions.RequestException, e:
            print 'HTTPError = ', e
        except requests.exceptions.ConnectionError, e:
            print 'URLError = '
        except requests.exceptions.HTTPError, e:
            print 'URLError = '
            return 0, e.response
        except requests.exceptions.TooManyRedirects, e:
            print 'URLError = '
        except:
            print '\nSome error/exception occurred.(%s)' % url 
        return 0,""

    def query_ticket_info(self, train_date, from_station_telecode, to_station_telecode):
        self.host_ip_index += 1
        if self.host_ip_index >= len(self.host_ips):
            self.host_ip_index = 0
        qurl = 'https://%s/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (self.host_ips[self.host_ip_index], train_date, from_station_telecode, to_station_telecode)

        rs,res = self.getUrl(qurl, timeout=3)
        
        res_json = ""
        if rs:
            if res.status_code == 200:
                try:
                    res_json = json.loads(res.text)
                    if type(res_json) == type(1):
                        return 0, res_json
                    elif res_json.has_key('data'):
                        return 1, res_json
                    else:
                        if res_json.has_key('messages'):
                            print res_json['messages'][0]
                        return 0, res_json
                except:
                    return 0, "余票 json 解析错误"
     
        return 0, "其它错误"

    def checkTicket(seat_filter, train_filter)
        for seat in seat_filter:
            for train in train_filter:
                rs, ticket, tCount = client.testHasTicket(ticket_info_json, train, seat)
                if rs:
                    print "找到余票并尝试订票(车次：%s 席别:%s)" % (ticket['queryLeftNewDTO']['station_train_code'], seat)
                    
                    client.updatePassengerStr(seat, passengerList, tCount)

                    if client.processTicket(ticket, randCode, ifUseAutoRandCode):
                        # 订票成功
                        print "订票成功"
                        exit()
                    else:
                        # 休息防止被踢
                        print "订票失败休息"
                        time.sleep(2)


