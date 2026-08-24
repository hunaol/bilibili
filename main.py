import json

from client import create_client, save_cookie, load_cookie
from login import get_qrcode, check_login
from video import get_user_video, download_video

# 创建 client
client = create_client()

# 尝试加载旧 Cookie
has_cookie = load_cookie(client)

if not has_cookie:
    print("没有 Cookie，需要扫码登录")
    key = get_qrcode(client)
    success = check_login(client, key)
    if success:
        save_cookie(client)
else:
    print("使用历史登录状态")

# 拉取历史记录
get_user_video(client)

# 从历史记录里读取第一个视频，下载它
with open("./data/recent.json", encoding="utf-8") as f:
    data = json.load(f)

first = data["data"]["list"][0]
h = first["history"]
download_video(client, h["bvid"], h["cid"], first["title"])