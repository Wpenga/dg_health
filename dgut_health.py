import os
import re
import time
import requests
import json
import sys
#通知参数（选填）教程 https://no.wpeng.cf/f59e28f9aeac425b8c7baa5cab4b7534#f9e7ddf1622b4b4aab5135af627e9bd6
QYWX_AM=''
#账户参数 
#格式 学号,密码   学号1,密码1@学号2,密码2
# local_student=""
#获取token
def login_start():
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'LogStatistic',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://yqfk-daka.dgut.edu.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    url = 'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/yqfkdaka/state/%2Fhome.html'
    reposed = requests.get(url=url, headers=headers)
    reposed_token = str(reposed.content)
    reposed_cookies = reposed.cookies.get_dict()
    # print(reposed_cookies)
    token = re.findall(r'var token = "(.+?)";', reposed_token)
    print('获取到token：' + token[0])
    return token[0],reposed_cookies

#登录 获取token2
def login(token, cookies,user, password):
    token1 = token
    url = 'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/yqfkdaka/state/%2Fhome.html'
    headers = {
        'Host': 'cas.dgut.edu.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'LogStatistic',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://cas.dgut.edu.cn',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/yqfkdaka/state/%2Fhome.html',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    data = {
        'username': user,
        'password': password,
        '__token__': token1,
        'wechat_verify': '',
    }
    reposed = str(requests.post(url=url, headers=headers, data=data, cookies=cookies).content)
    token2 = re.findall(r'token=(.+?)&', reposed)
    msg = re.findall(r'message...(.+?)...code', reposed)
    # print("msg： ",msg)
    if msg[0] == '\\xe9\\xaa\\x8c\\xe8\\xaf\\x81\\xe9\\x80\\x9a\\xe8\\xbf\\x87':
        msg = '验证通过'
    else:
        msg = 'msg错误'
    # print(reposed)
    # print(token2)
    print('获取到token2：' + token2[0])
    print(msg)
    return token2[0], msg

#获取accestoken
def login_end(token2,cookies):
    url = 'https://yqfk-daka-api.dgut.edu.cn/auth'
    headers = {    
        'Connection': 'keep-alive',
        'sec-ch-ua':'" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile':'?1',
        'User-Agent': 'LogStatistic',
        'Content-Type': 'application/json',
        'Origin': 'https://yqfk-daka.dgut.edu.cn',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://yqfk-daka.dgut.edu.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    data = {
        'token': token2,
        'state': "home",    
    }
    access_url = str(requests.post(url=url, headers=headers, cookies=cookies,data=json.dumps(data)).content)
    
    access_token = re.findall(r'(?<=access_token..").+(?=")', access_url)
    print('获取到accesstoken：' + access_token[0])
    return access_token[0]
    # return access_url

#获取提交的数据
def get_data(access_token):
    headers = {
        'Host':'yqfk-daka-api.dgut.edu.cn',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium"v="91"',
        'Accept': 'application/json, text/plain, */*',
        'Authorization':f'Bearer {access_token}',
        'Sec-Fetch-User': '?1',
        'User-Agent': 'LogStatistic',
        'Origin':'https://yqfk-daka.dgut.edu.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': '',
        'Referer': 'https://yqfk-daka.dgut.edu.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    url = 'https://yqfk-daka-api.dgut.edu.cn/record/'
    reposed = requests.get(url=url, headers=headers)
    reposed_data = str(reposed.content)
    # reposed_cookies = reposed.cookies.get_dict()
    # print(reposed_data)
    # print(reposed_cookies)
    # user_data = re.findall(r'"user_data":(.+)(?=})', reposed_data)

    data=reposed.json()
    user_data=data['user_data']
    # print('获取的数据：\n',user_data)
    return user_data,data

#提交签到，返回推送字符串
def qiandao(access_token):
    user_data,all_data=get_data(access_token)
    #更新提交时间
    datatimenow = time.strftime("%Y-%m-%d", time.localtime())
    user_data['submit_time']=datatimenow
    data={"data":user_data}
    # print('提交的数据:\n',data)
    url = 'https://yqfk-daka-api.dgut.edu.cn/record/'
    headers = {
        'Host':'yqfk-daka-api.dgut.edu.cn',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium"v="91"',
        'Accept': 'application/json, text/plain, */*',
        'Authorization':f'Bearer {access_token}',
        'Sec-Fetch-User': '?1',
        'User-Agent': 'LogStatistic',
        'Origin':'https://yqfk-daka.dgut.edu.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': '',
        'Referer': 'https://yqfk-daka.dgut.edu.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    data_json = json.dumps(data)
    reposed = requests.post(url=url, headers=headers, data=data_json).json()
    # print(reposed['message'])
    datatimenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    msg="【"+ user_data['name'] + "】"+ "当前打卡信息：\n" + all_data['message']+"\n出校机会:"+all_data['school_perms']+"\n此次打卡："+reposed['message']+ '\n' + datatimenow
    return msg
##################################################################################################################
# 通知
# 企业微信 APP 推送
def wecom_app(title, content):
    try:
        if not QYWX_AM:
            print("QYWX_AM 并未设置！！\n取消推送")
            return
        QYWX_AM_AY = re.split(',', QYWX_AM)
        if 4 < len(QYWX_AM_AY) > 5:
            print("QYWX_AM 设置错误！！\n取消推送")
            return
        corpid = QYWX_AM_AY[0]
        corpsecret = QYWX_AM_AY[1]
        touser = QYWX_AM_AY[2]
        agentid = QYWX_AM_AY[3]
        try:
            media_id = QYWX_AM_AY[4]
        except:
            media_id = ''
        wx = WeCom(corpid, corpsecret, agentid)
        # 如果没有配置 media_id 默认就以 text 方式发送
        if not media_id:
            message = title + '\n\n' + content
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)
        if response == 'ok':
            print('推送成功！')
        else:
            print('推送失败！错误信息如下：\n', response)
    except Exception as e:
        print(e)

class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0"
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "₯㎕。鵬。",
                        "content_source_url": "",
                        "content": message.replace('\n', '<br/>'),
                        "digest": message
                    }
                ]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

def send(title, content):
    if QYWX_AM:
        wecom_app(title=title, content=content)
    else:
        print('未启用企业微信应用消息推送')
##################################################################################################################
# 通知
class WXPusher:
    def __init__(self, usr, msg):
        self.base_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?'
        self.req_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token='
        self.corpid = 'ww6ebe8d89c498594e'  # 上面提到的你的企业ID
        self.corpsecret = '-bU_VUM7Jur8cwVVFBQe6Prl4Sd2kxUIheU6HZdNigw'  # 上图的Secret
        self.agentid = 1000002  # 填写你的企业ID，不加引号，是个整型常数,就是上图的AgentId
        self.usr = usr
        self.msg = msg
#export QYWX_AM="ww6ebe8d89c498594e,5WxdnPvY87xeF1JZQpIfo83jbIFjxtWPApqq4MU8TD8,WuZePeng,1000004,277_geDe-WxfAE30DD6MrnePtLiHVg-TQPJOudP6PhK_kO0zBGqbLrBliLUHkocZO"
    def get_access_token(self):
        urls = self.base_url + 'corpid=' + self.corpid + '&corpsecret=' + self.corpsecret
        resp = requests.get(urls).json()
        access_token = resp['access_token']
        return access_token

    def send_message(self):
        data = self.get_message()
        req_urls = self.req_url + self.get_access_token()
        res = requests.post(url=req_urls, data=data)
        print('通知发送成功！！')
        # print(res.text)

    def get_message(self):
        data = {
            "touser": "WuZePeng",
            "toparty": "@all",
            "totag": "@all",
            "msgtype": "mpnews",
            "agentid": self.agentid,
            "mpnews": {
                'articles': [
                    {
                        'title': '健康打卡',
                        'author': '₯㎕。鵬。',
                        'thumb_media_id': '2aLM4MplMcxPA8GSMtyxx7lAUqITQbVgtzfp3k5975YKJZ5Ps4RXslqh7nTCySLJ2',
                        'content_source_url': 'https://yqfk-daka.dgut.edu.cn/',
                        'content': f'{self.msg}'.replace('\n', '<br/>'),
                        'digest': f'{self.msg}'
                    }
                ]
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        data = json.dumps(data)
        return data

#开始
def start(user, password):
    ##使用sendnotify.py
    # loadSend()
    
    token, cookies = login_start()
    token2, msg = login(token, cookies, user, password)
    access_token = login_end(token2, cookies)
    message = qiandao(access_token)
    # datatimenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # push = WXPusher(usr="无", msg=message)
    # push.send_message()
    print('发送通知')
    print(message)

    send("莞工健康打卡",message)

"""
需要添加：学号，密码
"""
def main_handler():
    num=1
    if(os.environ['student']):
        print("从环境变量获取变量")
        student=os.environ['student']
    else:
        print("从本文件获取变量")
        student=local_student
    # student='学号1,密码1@学号2,密码2'
    students=student.split('@')
    num=len(students)
    print(f"一共有{num}个账号")
    for i in students:
        studentA=i.split(',')
        user=studentA[0]
        password=studentA[1]    
        start(user, password)
##新增        
def loadSend():
    print("\n加载推送功能")
    global send
    send = None
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/sendNotify.py"):
        try:
            from sendNotify import send
        except Exception as e:
            send = None
            print("加载通知服务失败~",e)

if __name__ == '__main__':
    main_handler()
