#coding: utf-8

import re
import time
import json
import urllib
import requests
from collections import OrderedDict

class Doctor:
    hi = ""
    dp = ""
    id = ""
    name = ""
    title = ""
    fee = 0
    num = 0
    url = ""
    skill = ""
    dutySourceId = ""

    def __init__(self,name,title,fee,num,url,skill,dutySourceId,hi,dp,id):
        self.name = name
        self.title = title
        self.fee = fee
        self.num = num
        self.url = url
        self.skill = skill
        self.dutySourceId = dutySourceId
        self.hi = hi
        self.dp = dp
        self.id = id

    def __repr__(self):
        return "%40s(%s)\t%s\t%s\t%s\t%s" % (self.name, self.title, self.skill, self.fee, self.num, self.url)

    def __str__(self):
        return self.__repr__()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}

def isLogin(s):
    url = "http://www.bjguahao.gov.cn/islogin.htm"
    data = {
        'isAjax': 'true',
    }
    r = s.post(url, data=data)
    ret = json.loads(r.text.encode('utf-8'))
    if ret['userid'] == '220138508':
        return True
    else:
        return False

with requests.Session() as s:
    """
        完成登陆
    """
    r = s.get("http://www.bjguahao.gov.cn/index.htm", headers=headers)
    data = {
        'mobileNo': '13021293541',
        'password': 'zrrnra12',
        'yzm': '',
        'isAjax': 'true',
    }
    headers.update({'Referer': 'http://www.bjguahao.gov.cn/index.htm'})
    r = s.post("http://www.bjguahao.gov.cn/quicklogin.htm", data=data, headers=headers)
    ret = json.loads(r.text)
    if ret['msg'] == 'OK':
        print "登陆成功!"
    else:
        print "登陆失败!"

    """
        查看指定医院对应科室
        以协和医院中医科门诊为例
        hospitalId:1 (医院编号)
        departmentId:200004109 (科室编号)
        dutyCode:2 (上午为1,下午为2)
        dutyDate:2017-07-06 (日期)
        isAjax:true
    """
    url = "http://www.bjguahao.gov.cn/dpt/partduty.htm"
    data = {
        'hospitalId': '1',
        'departmentId': '200004109',
        'dutyCode': '1',
        'dutyDate': '2017-07-06',
        'isAjax': 'true',
    }
    headers.update({'Referer': 'http://www.bjguahao.gov.cn/quicklogin.htm'})
    r = s.post(url, data=data, headers=headers)
    ret = json.loads(r.text)
    doctorList = []
    if ret['msg'] == 'OK':
        for item in ret['data']:
            doctorName = item['doctorName'].encode('utf-8')
            titleName = item['doctorTitleName'].encode('utf-8')
            id = item['doctorId']
            dutyId= item['dutySourceId']
            hi = item['hospitalId']
            dp = item['departmentId']
            num = item['remainAvailableNumber']
            skill = item['skill'].encode('utf-8')
            fee = item['totalFee']
            dutySourceId = item['dutySourceId']
            bookUrl = "http://www.bjguahao.gov.cn/order/confirm/{0}-{1}-{2}-{3}.htm".format(hi, dp, id, dutyId)
            if int(num) > 0:
                doctor = Doctor(doctorName,titleName,fee,num,bookUrl,skill,dutySourceId,hi,dp,id)
                doctorList.append(doctor)
        print "获取值班列表成功!"
    else:
        print "获取值班列表失败!"

    doctorList = sorted(doctorList, cmp=lambda x, y: cmp(x.fee,y.fee), reverse=1)
    for k, item in enumerate(doctorList):
        print (k + 1), item

    choice = raw_input("Please input your choice: (1~"+str(len(doctorList))+"):")
    doctor = doctorList[int(choice)-1]

    """
        发送验证码
    """
    while True:
        url = "http://www.bjguahao.gov.cn/v/sendorder.htm"
        headers.update({'Referer': 'http://www.bjguahao.gov.cn/dpt/partduty.htm'})
        r = s.post(url, headers=headers)
        ret = json.loads(r.text)
        if re.findall("OK", ret['msg']):
            print "获取预约验证码成功!"
            break
        else:
            print "获取预约验证码失败!"
            time.sleep(1)

    while True:
        smsCode = raw_input("Please input your smsCode:")
        """
            开始预约
        """
        url = "http://www.bjguahao.gov.cn/order/confirm.htm"
        data = OrderedDict([
            ('dutySourceId', str(doctor.dutySourceId)),
            ('hospitalId', str(doctor.hi)),
            ('departmentId', str(doctor.dp)),
            ('doctorId', str(doctor.id)),
            ('patientId', '232991828'), #father
            ('hospitalCardId', ''),
            ('medicareCardId', ''),
            ("reimbursementType", '-1'),
            ('smsVerifyCode', str(smsCode)),
            ('childrenBirthday', ''),
            ('isAjax', 'true')
        ])
        headers = {
            'Host': 'www.bjguahao.gov.cn',
            'Connection': 'keep-alive',
            'Origin': 'http://www.bjguahao.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://www.bjguahao.gov.cn/v/sendorder.htm',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Content-Length': str(len(urllib.urlencode(data))),
        }
        #print headers, data, urllib.urlencode(data)
        r = s.post(url, data=data, headers=headers, allow_redirects=False)
        #print r.text
        #print r.status_code
        try:
            ret = json.loads(r.text)
            if ret["msg"] == "OK":
                print "挂号成功!"
                break
        except:
            print "挂号失败!"
            time.sleep(1)
