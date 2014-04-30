# -*- coding: utf-8 -*-

import InputRandCode
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
import TicketFunctions

from email.mime.text import MIMEText

requests.adapters.DEFAULT_RETRIES = 5

reload(sys)
sys.setdefaultencoding('utf-8')

class TicketClient:
    """docstring for Ticket"""

    def __init__(self, config, session, proxy=None):
        '''
        self.proxies = {'http':'http://192.168.108.237:8888', 
            'https':'http://192.168.108.237:8888'
        }
        
        self.proxies = {'http':'http://127.0.0.1:8888', 
            'https':'http://127.0.0.1:8888'
        }
        '''

        self.stations = []


        self.orderInfo = {
        'byDate':'2014-01-31',
        'secretStr':'',
        'station_train_code':'',
        'train_no':'',
        'from_station_name':'',
        'from_station_telecode':'',
        'to_station_name':'',
        'to_station_telecode':'',

        'location_code':'',
        'key_check_ischange':'',
        'leftTicketStr':'',
        'isAsync':''
        }

        self.host_ips=['219.145.161.13',
        '121.205.7.44',
        'kyfw.12306.cn',
        '113.207.63.142',
        '219.145.161.11',
        '42.202.148.46',
        '163.177.242.54'
        ]

        self.randCodePath = 'login.png'

        self.host_ip_index = 0

        self.passengerTicketStr = ""
        self.oldPassengerStr = ''


        self.base_url = "https://kyfw.12306.cn/otn/"
        self.login_url = "https://kyfw.12306.cn/otn/login/loginAysnSuggest"

        self.getPassenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        self.initDc_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

        self.autoSubmitOrderRequest_url = "https://kyfw.12306.cn/otn/confirmPassenger/autoSubmitOrderRequest"
        self.confirmSingleForQueueAsys_url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueueAsys'
        self.getQueueCountAsync_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCountAsync'
        self.checkRandCodeAnsyn_url = 'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'
        self.AsynSugguestUrl = "https://kyfw.12306.cn/otn/login/loginAysnSuggest";
        self.loginRandRequestUrl = "https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew.do?module=login&rand=sjrand"
        self.orderRandRequestUrl = "https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew.do?module=login&rand=sjrand&0.5445713368916163"

        self.User_Agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48 Safari/537.36'
        self.cookie_filepath = 'cookie.txt' 

        self.headers = {'User-Agent':self.User_Agent, 
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Connection': 'keep-alive',
                'Host':'kyfw.12306.cn',
                'Referer':'https://kyfw.12306.cn/otn/leftTicket/init'}
                
        self.headers_img = {'User-Agent':self.User_Agent, 
                'Accept': 'image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                'Connection': 'keep-alive',
                'Referer':'https://kyfw.12306.cn/otn/leftTicket/init'}

        self.stationInit()


        self.session = session
        self.username = config['username']
        self.password = config['password']
        self.ifUseAutoRandCode = config['ifUseAutoRandCode']
        if config['ifUseAutoRandCode'] == "yes":
            self.ifUseAutoRandCode = True
        else:
            self.ifUseAutoRandCode = False

        # train_filter_type 和   train_filter二选一
        # 如果train_filter为空，则通过train_filter_type过滤
        #train_filter_type = ['G', 'T', 'K', 'D']
        self.train_filter_type = config['train_filter_type']
        self.train_filter = config['train_filter']
        self.seat_filter = config['seat_filter']
        self.date_filter = config['date_filter']
        self.current_date_index = 0



        self.orderInfo['from_station_name'] = config['from_station_name']
        self.orderInfo['to_station_name'] = config['to_station_name']
        self.orderInfo['from_station_telecode'] = TicketFunctions.getTelcodeFromName(self.orderInfo['from_station_name'])
        self.orderInfo['to_station_telecode'] = TicketFunctions.getTelcodeFromName(self.orderInfo['to_station_name'])
        self.idList = config['idList']

        self.updateTrainDate()


        self.newPassengers = config['newPassengers']
        for p in self.newPassengers:
            if not p['id'] in self.idList:
                self.idList.append(p['id'])

        self.minTicketSubmit = len(self.idList)


        self.passengerList = []


    def updatePassengerInfos(self):
        self.passengerList = self.getPassengerList()
        #print passengerList

        #添加旅客
        for p in self.newPassengers:
            self.passengerList = self.addPassenger(self.passengerList, p['name'], p['id'], p['ticket_type'], p['id_type'])
 

    def setCookie(self):
        self.session.cookies['_jc_save_fromStation'] = self.convertCookieString(self.orderInfo['from_station_name'] +' ' +self.orderInfo['from_station_telecode'])#'%u4E0A%u6D77%2CSHH'
        self.session.cookies['_jc_save_toStation'] = self.convertCookieString(self.orderInfo['to_station_name'] +' ' +self.orderInfo['to_station_telecode'])#'%u897F%u5B89%2CXAY'
        self.session.cookies['_jc_save_fromDate'] = self.orderInfo['byDate']
        self.session.cookies['_jc_save_toDate'] = self.orderInfo['byDate']
        self.session.cookies['_jc_save_wfdc_flag'] = 'dc'



    def convertCookieString(self, name):
        return name.encode('unicode_escape').upper().replace('\U','%u').replace(' ','%2C')

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

    
    def getUrlWithCustomHeader(self, url, headers):
        try:
            return 1, self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False )
        except requests.exceptions.RequestException, e:
            print 'HTTPError = '
        except requests.exceptions.ConnectionError, e:
            print 'URLError = '
        except requests.exceptions.HTTPError, e:
            print 'URLError = '
            return 0, e.response
        except requests.exceptions.TooManyRedirects, e:
            print 'URLError = '
        except:
            print '\nSome error/exception occurred.'
        return 0,""
    
    def postUrl(self, url, data=None):
        try:
            return 1, self.session.post(url, data=data, headers=self.headers, proxies=self.proxies, verify=False )
        except requests.exceptions.RequestException, e:
            print 'HTTPError = ' , e
        except requests.exceptions.ConnectionError, e:
            print 'URLError = ' , e
        except requests.exceptions.HTTPError, e:
            print 'URLError = ' , e
            return 0, e.response
        except requests.exceptions.TooManyRedirects, e:
            print 'URLError = ' , e
        except:
            print '\nSome error/exception occurred.'
        return 0,""

    def postFileUrl(self, url, files=None, data=None, headers=None):
        try:
            return 1, requests.post(url, files=files, data=data, proxies=self.proxies, headers=headers, verify=False )
        except requests.exceptions.RequestException, e:
            print 'HTTPError = ' , e
        except requests.exceptions.ConnectionError, e:
            print 'URLError = ' , e
        except requests.exceptions.HTTPError, e:
            print 'URLError = ' , e
            return 0, e.response
        except requests.exceptions.TooManyRedirects, e:
            print 'URLError = ' , e
        except:
            print '\nSome error/exception occurred.'
        return 0,""
    
    def GetImage(self, url, path):
        r, res = self.getUrlWithCustomHeader(url, self.headers_img)
        if r and res.status_code == 200:
            data = res.content
            output = open(path, 'wb')
            output.write(data);
            output.close( )
            return res.status_code
        

    
    def Login(self, inputWindow):
        # 获得验证码
        randCode = self.getNewRandCode(self.loginRandRequestUrl, inputWindow)

        errorMsg = ""
        data = {"loginUserDTO.user_name":self.username, "userDTO.password":self.password, "randCode": randCode}
        r,res = self.postUrl(self.login_url, data)
        if r and res.status_code == 200:
            html = res
            res_json = json.loads(res.text)
            if res_json.has_key('data'):
                if res_json['data'].has_key('loginCheck') and res_json['data']['loginCheck'] == 'Y':
                    return True,""
                else:
                    print res_json['messages'][0]
                    return False, res_json['messages'][0]
            
        return False, errorMsg


    def query_ticket_info(self, train_date):
        self.host_ip_index += 1
        if self.host_ip_index >= len(self.host_ips):
            self.host_ip_index = 0
        qurl = 'https://%s/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (self.host_ips[self.host_ip_index], train_date, self.orderInfo['from_station_telecode'], self.orderInfo['to_station_telecode'])

        rs,res = self.getUrl(qurl, timeout=3)
        
        res_json = ""
        if rs:
               if res.status_code == 200:
                    res_json = json.loads(res.text)
                    if type(res_json) == type(1):
                        return 0, res_json
                    elif res_json.has_key('data'):
                        return 1, res_json
                    else:
                        if res_json.has_key('messages'):
                            print res_json['messages'][0]
                        return 0, res_json
     
        return 0, "其它错误"
    
    # 获得所有旅客列表
    def getPassengerList(self):
        passengerList = {}
        rs = 0
        res_json = ""
        res,data = self.getUrl(self.getPassenger_url)
        if res and data.status_code == 200:
            res_json = json.loads(data.text)
            if res_json.has_key('data') and res_json['data']['isExist'] == True:
                for p in res_json['data']['normal_passengers']:
                    pp = {}
                    pp['id_no'] = p['passenger_id_no']
                    pp['id_type_code'] = p['passenger_id_type_code']
                    pp['id_type_name'] = p['passenger_id_type_name']
                    pp['name'] = p['passenger_name']
                    pp['type'] = p['passenger_type']
                    pp['type_name'] = p['passenger_type_name']
                    pp['mobile_no'] = p['mobile_no']
                    passengerList[pp['id_no']] = pp
        return passengerList

    
    def convertFormData(self, parameters):
        postData = ''
        length = len(parameters);
        for i in range(0, length):
            postData += parameters[i][0] + '=' + parameters[i][1]
            if i < (length - 1):
                postData += '&' 
        return postData
    
    def convertFormData2(self, parameters):
        postData = ''
        length = len(parameters);
        for i in range(0, length):
            postData += urllib.quote_plus(parameters[i][0].encode('utf8'),'()') + '=' + urllib.quote_plus(parameters[i][1].encode('utf8'), '()')
            if i < (length - 1):
                postData += '&' 
        return postData
    
    def getOtnInitPage(self):
        r, res = self.getUrl('https://kyfw.12306.cn/otn/leftTicket/init')
        if r and res.status_code == 200:
            return 1
        return 0


    
   
    def checkRandCodeAnsyn(self, randCode):
        #return True
        res_json = ""
       
        formdata =[("randCode",randCode), 
        ("rand", "sjrand"), 
        ("_json_att", "")
        ]
        formdata = urllib.urlencode(formdata)
        r, res = self.postUrl(self.checkRandCodeAnsyn_url, formdata)
        if r and res.status_code == 200:
            res_json = json.loads(res.text)
            if res_json['data'] == 'Y':
                return True
        return False
    
    def getQueueCountAsync(self):
        rs = 0
        res_json = ""
        
        formdata =(("train_date","Fri Jan 31 2014 12:35:06 GMT+0800 (China Standard Time)"), 
        ("train_no", self.orderInfo['train_no']), 
        ("stationTrainCode", self.orderInfo['station_train_code']), 
        ("seatType", "1"), 
        ("fromStationTelecode", self.orderInfo['from_station_telecode']), 
        ("toStationTelecode", self.orderInfo['to_station_telecode']) ,
        ("leftTicket", self.orderInfo['leftTicketStr']),
        ("purpose_codes", "ADULT"),
        ("_json_att", "")
        )
        formdata = self.convertFormData2(formdata)
        r, res = self.postUrl(self.getQueueCountAsync_url, formdata)
        if r and res.status_code == 200:
            res_json = json.loads(res.text)
            if res_json['status'] == True:
                return 1, res_json['data']
        return 0, ""

    
    def confirmSingleForQueueAsys(self, randCode):
        rs = 0
        res_json = ""

        formdata =(("passengerTicketStr",self.passengerTicketStr), 
        ("oldPassengerStr", self.oldPassengerStr), 
        ("randCode", self.randCode), 
        ("purpose_codes", "ADULT"), 
        ("key_check_isChange", self.self.orderInfo['key_check_ischange']), 
        ("leftTicketStr", self.orderInfo['leftTicketStr']) ,
        ("train_location", self.orderInfo['location_code']),
        ("_json_att", "")
        )
        
        formdata = urllib.urlencode(formdata)
        
        r, res = self.postUrl(self.confirmSingleForQueueAsys_url, formdata)
        if r and res.status_code == 200:
            res_json = json.loads(res.text)
            print res_json
            if res_json['status'] == True:
                if res_json.has_key('data'):
                    if res_json['data']['submitStatus'] == True:
                        return 1, res_json['data']
                    else:
                        return 0, res_json['data']['errMsg']

        return 0, ""

    def queryOrderWaitTime(self):
        finished = 0
        info = ""
        while not finished:
            url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=%13d&tourFlag=dc&_json_att='%(random.randint(1000000000000,1999999999999))
            r, res = self.getUrl(url)
            if r and res.status_code == 200:
                res_json = json.loads(res.text)
                info = res.text
                if res_json.has_key('data'):
                    wait_time = res_json['data']['waitTime']
                    if wait_time == -1:
                        return 1, res_json['data']['orderId']
                    elif wait_time < 0:
                        print res_json['data']['msg']
                        return 0, res_json['data']['msg']
                    elif wait_time > 0:
                        time.sleep(wait_time)
                else:
                    finished = 1
        return 0, info

    # 检查是否登陆
    def checkIfLogined(self):
        #return False
        finished = 0
        info = ""
        res, data = self.getUrl(self.getPassenger_url)
        if res and data.status_code == 200:
            res_json = json.loads(data.text)
            if res_json.has_key('data') and res_json['data']['isExist'] == True:
                return True
        return False
        
    def autoSubmitOrderRequest(self):
        rs = 0
        res_json = ""
        formdata1 =(("secretStr",self.orderInfo['secretStr']), 
            ("train_date", self.orderInfo['byDate']), 
            ("tour_flag", "dc"), 
            ("purpose_codes", "ADULT"), 
            ("query_from_station_name", self.orderInfo['from_station_name']), 
            ("query_to_station_name", self.orderInfo['to_station_name'])
        )
        formdata2 =(
            ("cancel_flag", "2"),
            ("bed_level_order_num", "000000000000000000000000000000"),
            ("passengerTicketStr", self.passengerTicketStr),
            ("oldPassengerStr", self.oldPassengerStr)
        )

        formdata = self.convertFormData(formdata1) + "&&" + self.convertFormData(formdata2)
        formdata = bytes(formdata)
        r, res = self.postUrl(self.autoSubmitOrderRequest_url, formdata)
        if r and res.status_code == 200:
            res_json = json.loads(res.text)
            if res_json['status'] == True:
                dlist = res_json['data']['result'].split('#')
                orderInfo['location_code'] = dlist[0];
                orderInfo['key_check_ischange'] = dlist[1];
                orderInfo['leftTicketStr'] = dlist[2];
                orderInfo['isAsync'] = dlist[3];
                return 1, dlist
            else:
                return 0, res_json['messages'][0]

        return 0, ""
    
    
    def testHasTicket(self, ticket_json, train, seat_type):
        if not ticket_json.has_key('data'):
            return 0,""

        for w in ticket_json['data']:
            if w['queryLeftNewDTO']['station_train_code'] == train:
                seat = TicketFunctions.getTicketCount(w['queryLeftNewDTO']['yp_info'])
                if seat[seat_type] >= self.minTicketSubmit:
                    # 如果有票就返回这趟车的余票数据
                    return 1, w, seat[seat_type]
                    
        return 0,"", 0
    
    def checkTicketSecretStr(self, ticket_json, train, seat_type):
        if not ticket_json.has_key('data'):
            return 0,""

        for w in ticket_json['data']:
            if w['queryLeftNewDTO']['station_train_code'] == train:
                seat = TicketFunctions.getTicketCount(w['queryLeftNewDTO']['yp_info'])
                if seat[seat_type] != 0:
                    # 如果有票就返回这趟车的余票数据
                    return 1, w['secretStr']
                    
        return 0,""
    
    def getNewOrderRandCode(self, inputWindow):
        return self.getNewRandCode(self.orderRandRequestUrl, inputWindow)

    # orderRandRequestUrl    
    def getNewRandCode(self, url, inputWindow):
        recongizeEngine = "UU"
        codeIsOk = False
        getTimeCount = 0
        needUpdateImg = True
        recongizeCount = 0
        while needUpdateImg:
            if needUpdateImg:
                while needUpdateImg:
                    print "请求验证码图片"
                    rs = self.GetImage(url, self.randCodePath)
                    getTimeCount += 1
                    if rs == 200:
                        #请求成功
                        needUpdateImg = False
                    elif getTimeCount > 5:
                        print "无法获得验证码，请检查网络状况！"
                        return ""
            # 向用户请求输入验证码
            recongizeCount = 0
            while not needUpdateImg and not codeIsOk:
                code = ''
                rcode = ''
                r = False
                codeId = ''
                if self.ifUseAutoRandCode:
                    code = '0000'
                    if recongizeEngine == "UU":
                        r, rcode, codeId = self.onlineUURecongizeRandCode(self.randCodePath,username='username',password='passworld',softid='0',softkey='0')
                    else:
                        r, rcode, codeId = self.onlineRecongizeRandCode(self.randCodePath,username='username',password='password',softid='0',softkey='0')
                    if r:
                        code = rcode
                        recongizeCount += 1
                else:
                    inputWindow.setImage(self.randCodePath)
                    print "Please input the randCode"
                    code = inputWindow.getRandCode()
                if code == '':
                    # 需要更新图片
                    needUpdateImg = True
                    continue
                # 检查是否正确
                print code
                if self.checkRandCodeAnsyn(code):
                    print "验证码输入正确"
                    codeIsOk = True
                    return code
                elif self.ifUseAutoRandCode:
                    print "验证码输入错误并进行错误报告"
                    # 报告识别错误
                    if recongizeEngine == "UU" and codeId != "":
                        self.onlineUUReportErrorRandCode(codeId,username='username',password='password',softid='0',softkey='0')
                        # 退出测试
                if self.ifUseAutoRandCode and recongizeCount > 2:
                    #机器识别错误超过两次说明验证码比较复杂就更新验证码
                    needUpdateImg = True
        return ""    
    

    def getSeatTypeCode(self, seat_name):
        seatTypeCodes = {'WZ':'1','YZ':'1','YW':'3','RW':'4','ZY':'M','ZE':'O'}
        if seatTypeCodes.has_key(seat_name):
            return seatTypeCodes[seat_name]
        return ""

    def addPassenger(self, passengerList, name, id, ticket_type='1', id_type='1'):  
        ticket_type_list = {
        '1':"成人票",
        '2':"儿童票",
        '3':"学生票",
        '4':"残军票"
        }
        cardTypeCodes = {
          '1': "二代身份证",
          '2': "一代身份证",
          'C': "港澳通行证",
          'G': "台湾通行证",
          'B': "护照"
        }    
        pp = {}
        pp['id_no'] = id
        pp['id_type_code'] = id_type
        pp['id_type_name'] = cardTypeCodes[id_type]
        pp['name'] = name
        pp['type'] = ticket_type
        pp['type_name'] = ticket_type_list[ticket_type]
        pp['mobile_no'] = ''
        passengerList[pp['id_no']] = pp
        return passengerList
    
    # 票种    
    # '1':u"成人票",
    # '2':u"儿童票",
    # '3':u"学生票",
    # '4':u"残军票"    
    # passengerTicketStr:1,0,票种,姓名,1,身份证号码,手机号码,N
    # oldPassengerStr:姓名,1,身份证号码,1_
    # seat_name : 'YZ', 'YW'
    def updatePassengerStr(self, seat_name, passengerList, tCount):
        seat_code = self.getSeatTypeCode(seat_name)
        self.passengerTicketStr = ''
        self.oldPassengerStr = ''
        passenger_seat_detail = "0" # [0->随机][1->下铺][2->中铺][3->上铺]
        count = 0
        for id in idList:
            if count != 0:
                self.passengerTicketStr += 'N_'
                self.oldPassengerStr += '1_'
            if self.passengerList.has_key(id):
                p = self.passengerList[id]
                self.passengerTicketStr += '%s,%s,%s,%s,%s,%s,%s,'%(seat_code,passenger_seat_detail,p['type'],p['name'],p['id_type_code'],p['id_no'],p['mobile_no'])
                self.oldPassengerStr += '%s,%s,%s,'%(p['name'],p['id_type_code'],p['id_no'])
                count += 1
                if count >= tCount:
                    break;
            else:
                print "!!!Not find the passenger:%s" % p
        self.passengerTicketStr += 'N'
        self.oldPassengerStr += '1_'

    
    # 进入订票流程
    def processTicket(self, ticket, randCode, useAutoRandcode):
        self.orderInfo['secretStr'] = ticket['secretStr']
        self.orderInfo['station_train_code'] = ticket['queryLeftNewDTO']['station_train_code']
        self.orderInfo['train_no'] = ticket['queryLeftNewDTO']['train_no']
        self.orderInfo['from_station_name'] = ticket['queryLeftNewDTO']['from_station_name']
        self.orderInfo['from_station_telecode'] = ticket['queryLeftNewDTO']['from_station_telecode']
        self.orderInfo['to_station_name'] = ticket['queryLeftNewDTO']['to_station_name']
        self.orderInfo['to_station_telecode'] = ticket['queryLeftNewDTO']['to_station_telecode']
        self.setCookie()
        # 尝试请求订单
        rs, info = self.autoSubmitOrderRequest()
        if rs:
            self.getQueueCountAsync()
            
            # 校验验证码
            if not self.checkRandCodeAnsyn(randCode):
                # 需要重新确认验证码
                # 请求并由用户输入验证码
                randCode = self.getNewRandCode(self.orderRandRequestUrl, inputWindow)  
            # 提交认单
            print "confirmSingleForQueueAsys"
            rs, msg = self.confirmSingleForQueueAsys(randCode)
            if rs:
                print "订单已经提交到队列"
            else:
                print "订单提交失败：%s" % msg
                return False
            # 确认是否成功
            rs, msg = self.queryOrderWaitTime()
            if rs:
                # 成功
                print msg
                self.notifyMail(msg, "New Ticket")
                return True
        else:
            print info
        return False
    
    
    # 在线识别验证码
    def notifyMail(self, info, subject="12306 ticket notify", mail='test@mail.com'):   
        body = MIMEText(info,_subtype='plain',_charset='utf-8').as_string()
        formdata = {'type':'send', 
        'mail':mail,
        'msg':body,
        'subject':subject,
        'key':'test'
        }

        r,data = self.postFileUrl('http://demo/notify.php',data = formdata, files = None)
        if r and data.status_code == 200:
            d = data.text.split('|')
            if int(d[0]) == 1:
                return True, d[1]
            else:
                print d[1]
        return False, ''
        



    # 在线识别验证码
    def onlineRecongizeRandCode(self, filepath, username='test', password='123456', softid='',softkey=''):   
        formdata = {'type':'recognize', 
        'softID':softid,
        'softKey':softkey,
        'userName':username,
        'passWord':password,
        'codeType':'1040',
        'timeout':'5'

        }
        files = {'imagePath': (open(filepath, 'rb'))}

        r,data = self.postFileUrl('http://demo/code_check.php',data = formdata, files = files)
        if r and data.status_code == 200:
            d = data.text.split('|')
            if int(d[0]) == 1:
                return True, d[1], d[1]
            else:
                print d[1]
        return False, '', ''
    


    def onlineUURecongizeRandCode(self, filepath, username='test', password='123456', softid='', softkey=''):   
        formdata = {'type':'recognize', 
        'softID':softid,
        'softKey':softkey,
        'userName':username,
        'passWord':password,
        'codeType':'1004'

        }
        files = {'imagePath': ('aa.png', open(filepath, 'rb'), 'image/png')}

        r,data = self.postFileUrl('http://demo/code_check.php',files = files, data = formdata)
        if r and data.status_code == 200:
            d = data.text.split('|')
            print d
            if int(d[0]) == 1:
                return True, d[1], d[2]
            else:
                print d[1]
        return False, '', ''
    
    def onlineUUReportErrorRandCode(self, codeID, username='test', password='123456', softid='', softkey=''):   
        formdata = {'type':'reportError', 
        'softID':softid,
        'softKey':softkey,
        'userName':username,
        'passWord':password,
        'codeID':codeID
        }
        r,data = self.postUrl('http://demo/code_check.php',data = formdata)
        if r and data.status_code == 200:
            d = data.text.split('|')
            if int(d[0]) == 1:
                return True, d[1]
            else:
                print d[1]
        return False, ''

    # 获得列车代码列表
    # train_filter_type: ['G', 'T', 'K', 'D']
    def getTrainListFromTicketJson(self, ticket_json, train_filter_type):
        train_List = []
        if not ticket_json.has_key('data'):
            return train_List

        for w in ticket_json['data']:
            train_code = w['queryLeftNewDTO']['station_train_code']
            if train_code[0] in train_filter_type:
                train_List.append(train_code)
        return train_List

    # 自动跳到下一个日期
    def setTrainDate(self):
        self.current_date_index += 1
        if self.current_date_index >= len(self.date_filter):
            self.current_date_index = 0
        self.orderInfo['byDate'] = self.date_filter[self.current_date_index]
        
        self.setCookie()

