import time
from solders.keypair import Keypair  # type: ignore
import requests
from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)


def login(proxy, private_key: str):
    try:
        keypair = Keypair.from_base58_string(private_key)
        pubkey = keypair.pubkey()
        dateTime = int(time.time()*1000)
        signature = keypair.sign_message(f'Sign in to pump.fun: {dateTime}'.encode())
        data = {
            "address": str(pubkey),
            "signature": str(signature),
            "timestamp": dateTime
        }
        response = requests.post("https://client-api-2-74b1891ee9f9.herokuapp.com/auth/login", json=data, proxies=proxy)
        print("login", response.status_code)
        token = response.json()["access_token"]
        return token
    except:
        return


def reply(proxy, token: str, mint: str, text: str, fileUri: str, gtoken: str):
    try:
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Authorization": "Bearer "+token,
            "Content-Type": "application/json",
            "Origin": "https://www.pump.fun",
            "Referer": "https://www.pump.fun/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }
        url = "https://client-api-2-74b1891ee9f9.herokuapp.com/replies"
        data = {
            "fileUri": fileUri,
            "text": text,
            "mint": mint,
            "token": gtoken
        }
        response = requests.post(url, headers=headers, json=data, proxies=proxy)
        print("reply", response.status_code)
        return response.status_code == 201
    except:
        return


def getGtoken(mint: str, appid: str):
    try:
        # 打码
        url = "http://xxx.com/recaptcha/getTokenV3"
        data = {
            "appid": appid,
            "host": "https://www.pump.fun/"+mint,
            "sitekey": "6LcmKsYpAAAAABAANpgK3LDxDlxfDCoPQUYm3NZI",
            "pageAction": "submit"
        }
        response = requests.post(url, json=data)
        print("getGtoken", response.json()["code"])
        gtoken = response.json()["data"]
        return gtoken
    except:
        return


def getIP(iplink):
    try:
        ip = requests.get(iplink).text.strip()
        if "whitelist" in ip:
            return "error: 白名单未添加"+ip
        if ":" not in ip:
            return "error: ip 获取失败"+ip
        print("getIP", ip)
        return ip
    except:
        return


@app.route('/')
def home():
    return render_template('index.html')


@app.post("/action")
@cross_origin(methods=['POST'])
def action():
    reqdata = request.get_json()
    privateKey = reqdata["privateKey"]
    appid = reqdata["appid"]
    mint = reqdata["mint"]
    text = reqdata["text"]
    fileUri = reqdata["fileUri"]
    iplink = reqdata["iplink"]

    ip = getIP(iplink)
    if ip is None:
        return "error: ip is None"
    if "error" in ip:
        return ip
    proxy = {"http": "http://"+ip, "https": "http://"+ip}

    token = login(proxy, privateKey)
    if token is None:
        return "error: token is None"
    gtoken = getGtoken(mint, appid)
    if gtoken is None:
        return "error: gtoken is None"
    restatus = reply(proxy, token, mint, text, fileUri, gtoken)
    if restatus is None:
        return "error: restatus is None"
    if restatus:
        return "success"
    else:
        return "error: reply failed"


if __name__ == '__main__':
    app.run("0.0.0.0", 31156)
