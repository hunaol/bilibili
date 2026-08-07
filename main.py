from client import create_client, save_cookie, load_cookie
from login import get_qrcode, check_login
from video import get_user_video, download_history_videos, download_video, get_video_info

# 创建 client
client = create_client()

# 尝试加载旧 Cookie
has_cookie = load_cookie(client)

if not has_cookie:
    # 没有 Cookie，扫码登录
    print("没有 Cookie，需要扫码登录")
    key = get_qrcode(client)
    success = check_login(client, key)
    if success:
        save_cookie(client)
else:
    print("使用历史登录状态")

# 拉取历史记录
get_user_video(client)

# 下载历史记录里的视频
download_video(client, "BV16YRLB7Exd", 38034146197, "5分钟安装ClaudeCode并接入DeepSeek")
# get_video_info(client,"BV16YRLB7Exd", 38034146197)