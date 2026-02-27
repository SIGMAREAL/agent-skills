#!/usr/bin/env python3
"""
YouTube 批量字幕提取器 - 防封锁版本
"""

import os
import json
import time
import random
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import sys

# 批量提取配置
BATCH_CONFIG = {
    "delay_between_videos": 10,  # 视频间等待秒数
    "max_retries": 3,
    "retry_delay": 60,  # 重试等待秒数
    "session_file": "~/.cache/youtube_extractor/session.json",
    "cookies_file": "~/.cache/youtube_extractor/cookies.json",
}

class YouTubeBatchExtractor:
    def __init__(self, output_dir: str = "~/Documents/video-transcribe"):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = Path("~/.cache/youtube_extractor").expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.cache_dir / "session.json"
        self.load_session()

    def load_session(self):
        """加载会话状态"""
        if self.session_file.exists():
            self.session = json.loads(self.session_file.read_text())
        else:
            self.session = {"last_extracted": None, "blocked": False, "block_until": None}

    def save_session(self):
        """保存会话状态"""
        self.session_file.write_text(json.dumps(self.session, indent=2))

    def is_blocked(self) -> bool:
        """检查是否被封锁"""
        if self.session.get("blocked") and self.session.get("block_until"):
            if datetime.now().timestamp() < self.session.get("block_until", 0):
                return True
        return False

    def set_blocked(self, duration: int = 300):
        """标记被封锁"""
        self.session["blocked"] = True
        self.session["block_until"] = datetime.now().timestamp() + duration
        self.save_session()

    def clear_block(self):
        """解除封锁状态"""
        self.session["blocked"] = False
        self.session["block_until"] = None
        self.save_session()

    def extract_with_browser(self, url: str) -> Optional[str]:
        """用 browser-use 提取字幕（防封锁）"""
        # 检查封锁状态
        if self.is_blocked():
            wait_time = self.session.get("block_until", 0) - datetime.now().timestamp()
            if wait_time > 0:
                print(f"⏳ 封锁中，等待 {wait_time:.0f} 秒...")
                time.sleep(min(wait_time, 300))  # 最多等 5 分钟
                self.clear_block()

        # 随机延迟
        delay = random.uniform(3, 8)
        time.sleep(delay)

        # 用 browser-use 提取
        result = subprocess.run(
            ["browser-use", "eval", "document.body.innerText"],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            self.clear_block()
            return result.stdout
        else:
            # 检查是否被封锁
            if "blocked" in result.stderr.lower() or "429" in result.stderr:
                self.set_blocked(duration=300)
                return None
            return None

    def extract_with_browser_session(self, url: str) -> Optional[str]:
        """用已登录浏览器会话提取"""
        # 随机延迟
        delay = random.uniform(5, 15)
        time.sleep(delay)

        # 用 real 浏览器（已登录状态）
        cmd = [
            "browser-use", "--browser", "real",
            "open", url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return None

        time.sleep(5)  # 等待页面加载

        # 提取字幕
        eval_result = subprocess.run(
            ["browser-use", "eval",
             "document.querySelector('ytd-transcript')?.innerText || document.body.innerText"],
            capture_output=True, text=True, timeout=30
        )

        return eval_result.stdout if eval_result.returncode == 0 else None

    def batch_extract(self, urls: List[str], use_session: bool = True) -> dict:
        """批量提取"""
        results = {}

        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] {url}")

            # 检查封锁
            if self.is_blocked():
                wait = self.session.get("block_until", 0) - datetime.now().timestamp()
                print(f"⏳ 等待 {wait/60:.0f} 分钟...")
                time.sleep(min(wait, 600))  # 最多等 10 分钟
                self.clear_block()

            # 提取
            if use_session:
                content = self.extract_with_browser_session(url)
            else:
                content = self.extract_with_browser(url)

            if content and len(content) > 100:
                results[url] = {
                    "success": True,
                    "content": content[:5000],
                    "extracted_at": datetime.now().isoformat()
                }
                print(f"  ✅ 成功 ({len(content)} 字符)")
            else:
                results[url] = {
                    "success": False,
                    "error": "提取失败或被封锁"
                }
                print(f"  ❌ 失败")

            # 保存进度
            self.save_session()

            # 视频间随机延迟（5-15 秒）
            if i < len(urls) - 1:
                delay = random.uniform(5, 15)
                print(f"⏳ 等待 {delay:.0f} 秒...")
                time.sleep(delay)

        return results

    def save_results(self, results: dict, filename: str = "batch_results.json"):
        """保存结果"""
        output = self.output_dir / filename
        output.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        return output


def batch_extract_from_file(input_file: str):
    """从文件批量提取"""
    extractor = YouTubeBatchExtractor()

    # 读取 URL 列表
    urls = [line.strip() for line in Path(input_file).read_text().split('\n') if line.strip()]

    print(f"📋 开始批量提取 {len(urls)} 个视频...")

    results = extractor.batch_extract(urls)
    output = extractor.save_results(results)
    print(f"💾 结果保存到: {output}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        batch_extract_from_file(sys.argv[1])
    else:
        print("用法: python batch_extractor.py <urls.txt>")
        print("或直接在代码中调用 extractor.batch_extract([urls])")
