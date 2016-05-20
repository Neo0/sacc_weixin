# _*_ coding:utf-8 _*_

import hashlib
from xml.etree.ElementTree import fromstring
import time
import re
from flask import Flask, request, make_response
import sys
import urllib, httplib


URL_ZCCX = 'zccx.tyb.njupt.edu.cn'
TIME_SUM = r'<span class="badge">(\d+?)</span>'
TIME_DAY = r'(\d+?)年(\d+?)月(\d+?)日</td>'



app = Flask(__name__)
# app.debug = True


reload(sys)
sys.setdefaultencoding('utf-8')


def getcp(url, name, id):
    postp = {'name': name, 'number': id}
    params = urllib.urlencode(postp)
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    conn = httplib.HTTPConnection(url)
    conn.request("POST", '/student', params, headers)
    res = conn.getresponse().read()
    conn.close()
    # soup = BeautifulSoup(res)
    time_sum_re = re.compile(TIME_SUM)
    time_sum = time_sum_re.findall(res)[0]
    # print soup
    return time_sum



@app.route('/', methods=['GET', 'POST'])
def weixinoauth():
    if request.method == 'GET':
        token = 'weixin'
        query = request.args
        sig = query.get('signature', '')
        timesamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        echostr = query.get('echostr', '')
        s = [timesamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if hashlib.sha1(s).hexdigest() == sig:
            return make_response(echostr)
    else:
        request.setCharacterEncoding("UTF-8")
        recv = request.stream.read()
        xml_recv = fromstring(recv)
        ToUserName = xml_recv.find('ToUserName').text
        FromUserName = xml_recv.find('FromUserName').text
        key = xml_recv.find("Content").text
        zccx = key.split(' ')
        res = getcp(URL_ZCCX, zccx[0], zccx[1])
        reply = '''<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'''
        response = make_response(reply % (FromUserName, ToUserName, str(int(time.time())), res))
        response.content_type = 'application/xml'
        response.setCharacterEncoding("UTF-8")
        return response


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=7070)
