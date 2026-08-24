'''
curl ^"https://api.bilibili.com/x/web-interface/history/cursor?max=0^&view_at=0^&business=^&ps=20^&type=all^&web_location=333.1391^" ^
  -H ^"accept: */*^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9^" ^
  -b ^"buvid3=C95D69A4-7EDD-991F-3FDF-03743852660D20921infoc; b_nut=1783514420; _uuid=3756DC103-C89A-9758-BBE4-10831049DED8CC21148infoc; buvid_fp=81c320cdf9f3583f71e88a0091ad9d31; buvid4=1B8D5215-BF98-ED16-6C50-3E2306D2F40022031-026070820-Lfypf7tBgXvmuN9aicni3A^%^3D^%^3D; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; rpdid=^|(J~R)u)luRY0J'u~)JluRlJ~; CURRENT_QUALITY=80; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODYzMzQyOTQsImlhdCI6MTc4NjA3NTAzNCwicGx0IjotMX0.aIF1wYpTS-EHSC2P-BuuYzeeGMOI61BHdgklhGNymnc; bili_ticket_expires=1786334234; theme-switch-show=SHOWED; CURRENT_FNVAL=2000; SESSDATA=c45096a0^%^2C1801632454^%^2C995ab^%^2A82CjDtiJkFvUec8p5gcSAHz-u-jnncQoWOMLlmGdGGX3-i3eLCm7oWjYxG2FsYMSzQjE4SVkMxa09IejlBMlRiOXIwMHp6cktIY0V2YlNiYlUwZ183OTFvMjlDd2RWeXpmUks5c3lkQkxmYzI1cE1FSjdHVTNkb3loOGtWQlpucnVQekhkd0RTSEp3IIEC; bili_jct=627e2829128a7d035233a215ebb11a4e; DedeUserID=3546700482349598; DedeUserID__ckMd5=002743c5dd701b7c; sid=fx6a154d; home_feed_column=4; browser_resolution=1200-932; bp_t_offset_3546700482349598=1233695494253838336; b_lsid=FF14AA88_19FDAB266A3^" ^
  -H ^"origin: https://www.bilibili.com^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://www.bilibili.com/^" ^
  -H ^"sec-ch-ua: ^\^"Not;A=Brand^\^";v=^\^"8^\^", ^\^"Chromium^\^";v=^\^"150^\^", ^\^"Google Chrome^\^";v=^\^"150^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-site^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36^"
'''
import json
import os
# ──────────────────────────── 获取播放地址 ────────────────────────────

def get_video_info(client, bvid, cid):
    """
    根据 bvid / cid 获取视频和音频流的下载地址。
    fnval=4048 → 返回 DASH 格式（音视频分离，最高画质）。
    """
    url = "https://api.bilibili.com/x/player/playurl"
    params = {
        "bvid": bvid,
        "cid": cid,
        "fnval": "4048",
        "fnver": "0",
        "fourk": "1",
    }
    res = client.get(url, params=params)
    data = res.json()
    with open("./data/videomsg.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    if data.get("code") != 0:
        print(f"  API 错误: code={data.get('code')}, message={data.get('message')}")
        return {}
    return data["data"]


# ──────────────────────────── 下载单个文件 ────────────────────────────

def download_file(url, filepath, client):
    """
    流式下载文件，写入 filepath。
    用 stream 方式避免大文件撑爆内存。
    """
    headers = {"Referer": "https://www.bilibili.com/"}
    with client.stream("GET", url, headers=headers) as resp:
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(filepath, "wb") as f:
            for chunk in resp.iter_bytes(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(f"\r  下载中... {pct}% ({downloaded}/{total})", end="", flush=True)
        print()  # 换行


# ──────────────────────────── 下载视频 ────────────────────────────

def download_video(client, bvid, cid, title):
    """
    下载单个视频：拉取播放地址 → 下载视频流 + 音频流 → ffmpeg 合并。
    """
    os.makedirs("./downloads", exist_ok=True)

    # 1. 获取音视频流地址
    print(f"获取播放地址: {title}")
    info = get_video_info(client, bvid, cid)

    if not info:
        print("  跳过：视频不存在或无法获取")
        return

    # DASH 格式下，video 和 audio 是分开的列表
    dash = info.get("dash") or info
    videos = dash.get("video", [])
    audios = dash.get("audio", [])

    if not videos:
        print("  未找到视频流，可能是番剧/电影，暂不支持")
        return

    # 2. 选最高画质（列表已从高到低排好）
    video_stream = videos[0]
    audio_stream = audios[0]
    video_url = video_stream["base_url"] or video_stream["baseUrl"]
    audio_url = audio_stream["base_url"] or audio_stream["baseUrl"]

    # 安全文件名（去掉非法字符）
    safe_title = title.replace("/", "_").replace("\\", "_").replace(":", "_")[:80]
    video_path = f"./downloads/{safe_title}_video.m4s"
    audio_path = f"./downloads/{safe_title}_audio.m4s"
    output_path = f"./downloads/{safe_title}.mp4"

    # 3. 下载视频流
    print(f"  下载视频流 ({video_stream.get('codecs', '')})")
    download_file(video_url, video_path, client)

    # 4. 下载音频流
    print(f"  下载音频流 ({audio_stream.get('codecs', '')})")
    download_file(audio_url, audio_path, client)

    # 5. ffmpeg 合并
    print(f"  合并中...")
    ret = os.system(
        f'ffmpeg -y -i "{video_path}" -i "{audio_path}" '
        f'-c copy "{output_path}" -loglevel quiet'
    )
    if ret == 0:
        # 合并成功，删掉临时文件
        os.remove(video_path)
        os.remove(audio_path)
        print(f"  完成 → {output_path}")
    else:
        print(f"  ffmpeg 合并失败！请确认已安装 ffmpeg 并添加到 PATH")
        print(f"  临时文件保留: {video_path}, {audio_path}")


# ──────────────────────────── 历史记录 → 下载 ────────────────────────────

def get_user_video(client):
    """拉取历史记录并保存"""
    url = "https://api.bilibili.com/x/web-interface/history/cursor"
    params = {
        "max": 0,
        "view_at": 0,
        "business": "",
        "ps": 20,
        "type": "all",
        "web_location": "333.1391",
    }
    response = client.get(url, params=params)
    os.makedirs("./data", exist_ok=True)
    with open(
        "./data/recent.json", "w", encoding="utf-8"
    ) as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)


def download_history_videos(client):
    """从 recent.json 中读取历史记录，提取 bvid/cid 并下载视频"""
    with open("./data/recent.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("data", {}).get("list", [])
    print(f"共 {len(items)} 个历史记录\n")

    for i, v in enumerate(items, 1):
        history = v.get("history", {})
        bvid = history.get("bvid", "")
        cid = history.get("cid", 0)
        title = v.get("title", f"video_{i}")

        if not bvid or not cid:
            print(f"[{i}] 跳过（无 bvid/cid）: {title}")
            continue

        print(f"\n[{i}/{len(items)}] {title}")
        download_video(client, bvid, cid, title)