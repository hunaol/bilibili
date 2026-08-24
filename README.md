# Bilibili 视频下载工具
## 运行方式py main，自动下载观看记录最新的一条视频
一个基于 Python 的 Bilibili 视频下载工具，支持扫码登录、Cookie 持久化、历史记录拉取和视频下载。

## 功能

- 扫码登录（生成二维码，手机 Bilibili App 扫码确认）
- Cookie 持久化（登录一次，下次自动使用，无需重复扫码）
- 拉取观看历史记录
- 下载视频（自动选择最高画质，音视频分离下载后 ffmpeg 合并）

## 项目结构

```
bilibili_test/
├── main.py           # 入口文件
├── client.py         # httpx Client 管理 + Cookie 存取
├── login.py          # 二维码生成 + 扫码轮询
├── video.py          # 视频信息获取 + 下载 + ffmpeg 合并
├── requirements.txt  # Python 依赖清单
├── README.md         # 本文件
├── bili_cookie.json  # 登录凭据（自动生成，勿提交）
├── data/             # 历史记录缓存（自动生成）
│   └── recent.json
└── downloads/        # 下载的视频（自动创建）
```

## 环境要求

- Python 3.8+
- ffmpeg（用于合并音视频流）

## 安装

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 ffmpeg

```bash
# Windows（winget）
winget install ffmpeg

# macOS（brew）
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

安装后**重启终端**，确保 `ffmpeg` 命令可用。

## 使用

```bash
# 首次运行：会生成二维码，手机扫码登录
py main.py

# 再次运行：自动加载 Cookie，跳过扫码
py main.py
```

## 工作流程

```
启动
  │
  ├─ 有 Cookie → 加载 → 跳过登录
  │
  └─ 无 Cookie → 生成二维码 → 手机扫码 → 轮询状态 → 保存 Cookie
                                                      │
                                              拉取历史记录 → 下载视频
                                                            │
                                                  下载视频流 + 音频流
                                                            │
                                                      ffmpeg 合并
                                                            │
                                                         .mp4 文件
```

## API 接口说明

| 接口 | 用途 |
|---|---|
| `passport.bilibili.com/x/passport-login/web/qrcode/generate` | 生成登录二维码 |
| `passport.bilibili.com/x/passport-login/web/qrcode/poll` | 轮询扫码状态 |
| `api.bilibili.com/x/web-interface/history/cursor` | 获取观看历史 |
| `api.bilibili.com/x/player/playurl` | 获取视频播放地址 |

## 注意事项

- Cookie 有效期约一个月，过期后删除 `bili_cookie.json` 重新扫码
- 下载的视频仅供个人学习使用，请勿用于商业用途
- 仅支持免费视频和你的账号有权限观看的内容
- 番剧、电影等 DRM 加密内容无法下载

## License

MIT
