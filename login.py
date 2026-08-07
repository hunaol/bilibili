import qrcode
import time


def get_qrcode(client):
    """获取登录二维码，返回 qrcode_key"""
    url = (
        "https://passport.bilibili.com"
        "/x/passport-login/web/qrcode/generate"
    )
    response = client.get(url)
    data = response.json()
    qrcode_key = data["data"]["qrcode_key"]
    qr_url = data["data"]["url"]

    img = qrcode.make(qr_url)
    img.save("./qrcode.jpg")
    print("二维码已生成 (qrcode.jpg)，请用 Bilibili App 扫码登录")
    return qrcode_key


def check_login(client, qrcode_key):
    """轮询扫码状态，登录成功返回 True，二维码过期返回 False"""
    url = (
        "https://passport.bilibili.com"
        "/x/passport-login/web/qrcode/poll"
    )
    while True:
        res = client.get(url, params={"qrcode_key": qrcode_key})
        data = res.json()
        code = data["data"]["code"]

        if code == 0:
            print("登录成功！")
            return True
        elif code == 86038:
            print("二维码已过期，请重新运行程序")
            return False
        elif code == 86101:
            print("等待扫码...")
        elif code == 86090:
            print("已扫码，请在手机上点击确认")
        else:
            print(f"未知状态码: {code}")
        time.sleep(2)
