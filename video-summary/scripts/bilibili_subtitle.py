#!/usr/bin/env python3
"""
B站字幕批量提取器 + 用户视频列表
使用 B站官方 API + SESSDATA
"""

import os
import sys
import json
import time
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Cookie 配置
SESSDATA = ""


def get_sessdata() -> str:
    """获取 SESSDATA"""
    global SESSDATA

    # 优先从参数读取
    for arg in sys.argv[1:]:
        if arg.startswith("--cookie="):
            SESSDATA = arg.replace("--cookie=", "")
            return SESSDATA

    # 其次从文件读取
    cookie_file = Path("~/.cache/bilibili/cookie.json").expanduser()
    if cookie_file.exists():
        data = json.loads(cookie_file.read_text())
        if data.get("SESSDATA"):
            SESSDATA = data["SESSDATA"]
            return SESSDATA

    return SESSDATA


def get_headers() -> dict:
    """获取请求头"""
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com/",
        "Cookie": f"SESSDATA={SESSDATA}"
    }


def extract_bvid(url: str) -> Optional[str]:
    """从 URL 提取 BV 号"""
    patterns = [
        r'bilibili\.com/video/(BV[a-zA-Z0-9]+)',
        r'(BV[a-zA-Z0-9]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_user_videos(mid: str, limit: int = 30) -> list:
    """获取用户投稿视频列表"""
    url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={mid}&pn=1&ps={limit}&order=pubdate&jsonp=jsonp"

    resp = requests.get(url, headers=get_headers())
    data = resp.json()

    if data.get("code") != 0:
        print(f"❌ 获取视频列表失败: {data.get('message')}")
        return []

    videos = data.get("data", {}).get("list", {}).get("vlist", [])
    return videos


def get_video_info(bvid: str) -> dict:
    """获取视频信息"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    resp = requests.get(url, headers=get_headers())
    data = resp.json()

    if data.get("code") == 0:
        return data.get("data", {})
    return {}


def get_cid(bvid: str) -> Optional[int]:
    """获取视频 CID"""
    info = get_video_info(bvid)
    return info.get("cid")


def get_subtitle_url(bvid: str, cid: int) -> tuple:
    """获取字幕下载 URL 和语言"""
    url = f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}"
    resp = requests.get(url, headers=get_headers())
    data = resp.json()

    if data.get("code") != 0:
        return None, None

    subtitles = data.get("data", {}).get("subtitle", {}).get("subtitles", [])
    if not subtitles:
        return None, None

    sub = subtitles[0]
    return sub.get("subtitle_url"), sub.get("lan")


def download_subtitles(sub_url: str, bvid: str = "", title: str = "") -> list:
    """下载字幕内容"""
    if not sub_url:
        return []

    if sub_url.startswith("//"):
        sub_url = "https:" + sub_url

    resp = requests.get(sub_url)
    data = resp.json()

    lines = []
    for line in data.get("body", []):
        content = line.get("content", "").strip()
        if content:
            lines.append(content)

    # 保存字幕文件
    if lines and bvid:
        output_dir = Path("~/Documents/video-transcribe/bilibili").expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_title = (title[:30] if title else "unknown").replace("/", "_").replace("\\", "_")
        output_file = output_dir / f"{bvid}_{safe_title}.txt"
        output_file.write_text("\n".join(lines))
        print(f"   💾 保存到: {output_file.name}")

    return lines


def extract_single(bvid: str) -> dict:
    """提取单个视频字幕"""
    print(f"\n📺 处理: {bvid}")

    # 获取视频信息
    info = get_video_info(bvid)
    if not info:
        print(f"   ❌ 无法获取视频信息")
        return {"bvid": bvid, "success": False}

    title = info.get("title", "未知标题")
    pubdate = info.get("pubdate", 0)
    pubdate_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d") if pubdate else "未知"

    print(f"   标题: {title}")
    print(f"   发布: {pubdate_str}")

    # 获取字幕
    cid = info.get("cid")
    if not cid:
        print(f"   ❌ 无 CID")
        return {"bvid": bvid, "success": False}

    sub_url, lan = get_subtitle_url(bvid, cid)
    if not sub_url:
        print(f"   ❌ 无字幕")
        return {"bvid": bvid, "success": False, "title": title, "pubdate": pubdate_str}

    print(f"   ✅ 找到 {lan} 字幕")

    lines = download_subtitles(sub_url, bvid, title)
    print(f"   📥 {len(lines)} 条字幕")

    return {
        "bvid": bvid,
        "success": bool(lines),
        "title": title,
        "pubdate": pubdate_str,
        "lines": len(lines)
    }


def list_user_videos(mid: str, after_date: str = "2025-08-01"):
    """列出用户视频（筛选指定日期后）"""
    after_ts = datetime.strptime(after_date, "%Y-%m-%d").timestamp()

    print(f"\n📋 获取用户 {mid} 的视频列表...")
    print(f"   筛选: {after_date} 之后\n")

    videos = get_user_videos(mid, limit=100)

    filtered = []
    for v in videos:
        pubdate = v.get("created", 0)
        pubdate_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d") if pubdate else "未知"

        if pubdate >= after_ts:
            filtered.append({
                "bvid": v.get("bvid"),
                "title": v.get("title"),
                "pubdate": pubdate_str,
                "pic": v.get("pic"),
            })

    # 按日期倒序
    filtered.sort(key=lambda x: datetime.strptime(x["pubdate"], "%Y-%m-%d"), reverse=True)

    print(f"找到 {len(filtered)} 个 {after_date} 之后的视频：\n")
    for i, v in enumerate(filtered[:20], 1):
        print(f"{i:2}. [{v['pubdate']}] {v['title'][:40]}")

    if len(filtered) > 20:
        print(f"   ... 共 {len(filtered)} 个")

    return filtered


def main():
    if len(sys.argv) < 2:
        print("""
用法:
  # 列出用户视频
  python bilibili_subtitle.py list <mid> [--after=2025-08-01]

  # 提取单个视频字幕
  python bilibili_subtitle.py get <B站URL或BV号>

  # 批量提取字幕
  python bilibili_subtitle.py batch <bvid清单文件>

需要设置 SESSDATA:
1. 浏览器 F12 → Application → Cookies → bilibili.com
2. 找到 SESSDATA，复制 Value
3. 保存到 ~/.cache/bilibili/cookie.json
""")
        sys.exit(1)

    # 获取 SESSDATA
    sessdata = get_sessdata()
    if not sessdata:
        print("❌ 需要 SESSDATA")
        print("运行: python bilibili_subtitle.py <命令> --cookie=你的SESSDATA")
        sys.exit(1)

    print(f"✅ SESSDATA 已加载")

    cmd = sys.argv[1]

    if cmd == "list":
        # 列出用户视频
        mid = sys.argv[2] if len(sys.argv) > 2 else input("请输入用户 MID: ")
        after = "2025-08-01"
        for arg in sys.argv:
            if arg.startswith("--after="):
                after = arg.replace("--after=", "")
        list_user_videos(mid, after)

    elif cmd == "get":
        # 提取单个视频
        url = sys.argv[2] if len(sys.argv) > 2 else input("请输入视频 URL: ")
        bvid = extract_bvid(url)
        if not bvid:
            print(f"❌ 无法解析 BV号")
            sys.exit(1)
        extract_single(bvid)

    elif cmd == "batch":
        # 批量提取
        if len(sys.argv) > 2:
            bvids_file = sys.argv[2]
            bvids = Path(bvids_file).read_text().strip().split("\n")
            bvids = [b.strip() for b in bvids if b.strip()]
        else:
            bvids = []
            print("输入 BV号（空行结束）:")
            while True:
                line = input()
                if not line.strip():
                    break
                bvids.append(line.strip())

        print(f"\n📋 批量提取 {len(bvids)} 个视频")

        results = []
        for i, bvid in enumerate(bvids):
            print(f"\n[{i+1}/{len(bvids)}]")
            result = extract_single(bvid)
            results.append(result)
            time.sleep(2)  # 避免请求过快

        success = sum(1 for r in results if r.get("success"))
        print(f"\n✅ 完成: {success}/{len(results)} 成功")

    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
