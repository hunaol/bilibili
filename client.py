import json
import os

import httpx

COOKIE_FILE = "bili_cookie.json"
def create_client():
    """创建带统一 headers 的 httpx Client"""
    client = httpx.Client(
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.bilibili.com/",
        },
        follow_redirects=True,
    )
    return client


def save_cookie(client):
    """保存 client 中的 cookie 到本地文件"""
    cookies = dict(client.cookies)
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)
    print("Cookie 保存成功")


def load_cookie(client):
    """从本地文件加载 cookie 到 client，文件不存在则返回 False"""
    if not os.path.exists(COOKIE_FILE):
        return False
    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    client.cookies.update(cookies)
    print("Cookie 加载成功")
    return True
