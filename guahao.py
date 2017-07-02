#coding: utf-8

import re
import time
import json
import requests
import BeautifulSoup

class Doctor:
    name = ""
    title = ""
    fee = 0
    num = 0
    url = ""
    skill = ""
    def __init__(self,name,title,fee,num,url,skill):
        self.name = name
        self.title = title
        self.fee = fee
        self.num = num
        self.url = url
        self.skill = skill
    def __repr__(self):
        return "%40s(%s)\t%s\t%s\t%s\t%s" % (self.name, self.title, self.skill, self.fee, self.num, self.url)
    def __str__(self):
        return self.__repr__()

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

def getCookie(s):
    cookies = {
        'Hm_lvt_bc7eaca5ef5a22b54dd6ca44a23988fa': '1498636887,1498810318',
        'Hm_lpvt_bc7eaca5ef5a22b54dd6ca44a23988fa': str(time.time()).split(".")[0],
    }
    requests.utils.add_dict_to_cookiejar(s.cookies, cookies)
    Cookie = ""
    for k, v in requests.utils.dict_from_cookiejar(s.cookies).items():
        Cookie += k + '=' + v + ';'

    return Cookie[:-1], requests.utils.dict_from_cookiejar(s.cookies)
    
with requests.Session() as s:
    """
        完成登陆
    """
    r = s.get("http://www.bjguahao.gov.cn/index.htm")
    data = {
        'mobileNo': '13021293541',
        'password': 'zrrnra12',
        'yzm': '',
        'isAjax': 'true',
    }
    r = s.post("http://www.bjguahao.gov.cn/quicklogin.htm", data=data)
    ret = json.loads(r.text)
    if isLogin(s):
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
    r = s.post(url, data=data)
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
            bookUrl = "http://www.bjguahao.gov.cn/order/confirm/{0}-{1}-{2}-{3}.htm".format(hi, dp, id, dutyId)
            doctor = Doctor(doctorName,titleName,fee,num,bookUrl,skill)
            doctorList.append(doctor)
        print "获取值班列表成功!"
    else:
        print "获取值班列表失败!"
    print r.cookies

    doctorList = sorted(doctorList, cmp=lambda x, y: cmp(x.fee,y.fee), reverse=1)
    for k, item in enumerate(doctorList):
        print (k + 1), item

    choice = raw_input("Please input your choice: (1~"+str(len(doctorList))+"):")
    urlBook = doctorList[int(choice)-1].url

    """
        发送验证码
    """
    url = "http://www.bjguahao.gov.cn/v/sendorder.htm"
    cookieInfo = getCookie(s)
    headers = {
        'Host': 'www.bjguahao.gov.cn',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Origin': 'http://www.bjguahao.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://www.bjguahao.gov.cn/dpt/partduty.htm', 
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cookie': cookieInfo[0], 
    }
    r = s.post(url, headers=headers, cookies=cookieInfo[1])
    f = open("test.html", "w")
    f.write(r.text.encode('utf-8'))
    f.close()
    
    r = s.post(url, headers=headers, cookies=cookieInfo[1])
    ret = json.loads(r.text)
    if re.findall("OK", ret['msg']):
        print "获取预约验证码成功!"
    else:
        print "获取预约验证码失败!"
