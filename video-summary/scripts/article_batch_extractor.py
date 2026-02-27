#!/usr/bin/env python3
"""
文章批量提取器 - 防封锁版本
支持 Jina Reader 和 browser-use 双模式
"""

import os
import json
import re
import time
import random
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import sys
import requests

# 批量提取配置
BATCH_CONFIG = {
    "delay_between_requests": 3,  # 请求间等待秒数
    "max_retries": 3,
    "retry_delay": 30,  # 重试等待秒数
    "session_file": "~/.cache/article_extractor/session.json",
}

class ArticleBatchExtractor:
    def __init__(self, output_dir: str = "~/Documents/articles"):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = Path("~/.cache/article_extractor").expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.cache_dir / "session.json"
        self.load_session()

        # Jina Reader 配置
        self.jina_base = "https://r.jina.ai/"

        # 请求头（模拟浏览器）
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def load_session(self):
        """加载会话状态"""
        if self.session_file.exists():
            self.session = json.loads(self.session_file.read_text())
        else:
            self.session = {
                "last_extracted": None,
                "blocked": False,
                "block_until": None,
                "rate_limit_count": 0,
            }

    def save_session(self):
        """保存会话状态"""
        self.session_file.write_text(json.dumps(self.session, indent=2))

    def is_blocked(self) -> bool:
        """检查是否被封锁"""
        if self.session.get("blocked") and self.session.get("block_until"):
            if datetime.now().timestamp() < self.session.get("block_until", 0):
                return True
        return False

    def set_blocked(self, duration: int = 180):
        """标记被封锁（默认 3 分钟）"""
        self.session["blocked"] = True
        self.session["block_until"] = datetime.now().timestamp() + duration
        self.session["rate_limit_count"] = self.session.get("rate_limit_count", 0) + 1
        self.save_session()

    def clear_block(self):
        """解除封锁状态"""
        self.session["blocked"] = False
        self.session["block_until"] = None
        self.save_session()

    def extract_jina(self, url: str) -> Optional[str]:
        """用 Jina Reader 提取"""
        # 检查封锁状态
        if self.is_blocked():
            wait_time = self.session.get("block_until", 0) - datetime.now().timestamp()
            if wait_time > 0:
                print(f"⏳ 限流中，等待 {wait_time:.0f} 秒...")
                time.sleep(min(wait_time, 180))
                self.clear_block()

        # 随机延迟（2-5 秒）
        delay = random.uniform(2, 5)
        time.sleep(delay)

        try:
            response = requests.get(f"{self.jina_base}{url}", headers=self.headers, timeout=30)

            # 检查限流
            if response.status_code == 429:
                print(f"⚠️ 触发限流 (429)")
                self.set_blocked(duration=60)
                return None

            if response.status_code == 503:
                print(f"⚠️ 服务不可用 (503)")
                self.set_blocked(duration=30)
                return None

            if response.status_code == 200:
                self.clear_block()
                content = response.text

                # 检查是否是验证码页面
                if "captcha" in content.lower() or "cloudflare" in content.lower():
                    print(f"⚠️ 检测到验证码")
                    self.set_blocked(duration=120)
                    return None

                return content

            return None

        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None

    def extract_browser_use(self, url: str) -> Optional[str]:
        """用 browser-use 提取（反爬网站备用方案）"""
        try:
            # 打开页面
            result = subprocess.run(
                ["browser-use", "open", url],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                return None

            # 等待加载
            time.sleep(random.uniform(3, 6))

            # 提取内容（针对不同网站选择不同选择器）
            selectors = [
                "document.body.innerText",  # 通用
                "document.getElementById('js_content')?.innerText",  # 微信公众号
                "document.querySelector('article')?.innerText",  # Twitter/X
            ]

            for selector in selectors:
                eval_result = subprocess.run(
                    ["browser-use", "eval", selector],
                    capture_output=True, text=True, timeout=30
                )
                if eval_result.returncode == 0 and eval_result.stdout:
                    return eval_result.stdout

            return None

        except Exception as e:
            print(f"❌ browser-use 失败: {e}")
            return None

    def detect_domain(self, url: str) -> str:
        """检测域名类型"""
        url_lower = url.lower()

        if "twitter.com" in url_lower or "x.com" in url_lower:
            return "twitter"
        elif "mp.weixin.qq.com" in url_lower:
            return "wechat"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "bilibili.com" in url_lower:
            return "bilibili"
        else:
            return "general"

    def extract(self, url: str, method: str = "auto") -> Optional[str]:
        """提取单篇文章"""
        domain = self.detect_domain(url)

        # 自动选择方法
        if method == "auto":
            if domain == "wechat":
                # 微信公众号必须用 browser-use
                method = "browser"
            elif domain in ["twitter", "general"]:
                # Twitter 和通用网页优先 Jina Reader
                method = "jina"
            else:
                method = "jina"

        # 执行提取
        if method == "jina":
            content = self.extract_jina(url)
            # 如果 Jina 失败，降级到 browser-use
            if not content:
                print(f"🔄 Jina 失败，尝试 browser-use...")
                content = self.extract_browser_use(url)
        else:
            content = self.extract_browser_use(url)

        return content

    def batch_extract(self, urls: List[str], method: str = "auto") -> dict:
        """批量提取"""
        results = {}
        today = datetime.now().strftime("%Y-%m-%d")
        output_subdir = self.output_dir / today
        output_subdir.mkdir(parents=True, exist_ok=True)

        for i, url in enumerate(urls):
            print(f"\n[{i+1}/{len(urls)}] {url}")

            # 检查封锁
            if self.is_blocked() and method == "jina":
                wait = self.session.get("block_until", 0) - datetime.now().timestamp()
                print(f"⏳ 等待 {wait:.0f} 秒...")
                time.sleep(min(wait, 300))
                self.clear_block()

            # 提取
            content = self.extract(url, method=method)

            if content and len(content) > 100:
                # 生成文件名
                domain = self.detect_domain(url)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{domain}_{random.randint(1000, 9999)}.md"
                filepath = output_subdir / filename

                # 生成正确格式的 Markdown（带 frontmatter 和占位符）
                title = url.split('/')[-1].replace('-', ' ').title()
                safe_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)[:50].replace(' ', '-')

                # 提取第一行作为标题（如果 content 以 # 开头）
                content_lines = content.split('\n')
                if content_lines and content_lines[0].startswith('#'):
                    extracted_title = content_lines[0].lstrip('#').strip()
                else:
                    extracted_title = title

                safe_title = re.sub(r'[^a-zA-Z0-9\-]', '', extracted_title)[:50]
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                now_date = datetime.now().strftime("%Y-%m-%d")

                full_content = f'''---
title: {extracted_title}
source: letters.thedankoe.com
url: {url}
date: {now_date}
type: article
language: original
---

# {extracted_title}

> **来源**: [letters.thedankoe.com]({url})
> **提取日期**: {now_str}

---

## 📝 中文提炼总结

{{CLAUDE_SUMMARY_PLACEHOLDER}}

---

## 中文全文

{{CLAUDE_FULLTEXT_PLACEHOLDER}}

---

## 原始内容

{content}

---

*Claude Content Extractor 提取 | {now_str}*
'''

                filepath.write_text(full_content, encoding='utf-8')

                results[url] = {
                    "success": True,
                    "file": str(filepath),
                    "content_length": len(content),
                    "extracted_at": datetime.now().isoformat()
                }
                print(f"  ✅ 成功 ({len(content)} 字符) → {filename}")
            else:
                results[url] = {
                    "success": False,
                    "error": "提取失败或内容过短"
                }
                print(f"  ❌ 失败")

            # 保存进度
            self.save_session()

            # 请求间随机延迟（2-5 秒）
            if i < len(urls) - 1:
                delay = random.uniform(2, 5)
                print(f"⏳ 等待 {delay:.0f} 秒...")
                time.sleep(delay)

        # 保存批量结果摘要
        summary_file = output_subdir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))

        print(f"\n💾 批量摘要保存到: {summary_file}")

        return results


def batch_extract_from_file(input_file: str, method: str = "auto"):
    """从文件批量提取"""
    extractor = ArticleBatchExtractor()

    # 读取 URL 列表
    urls = [line.strip() for line in Path(input_file).read_text().split('\n') if line.strip()]

    print(f"📋 开始批量提取 {len(urls)} 个文章...")
    print(f"📁 输出目录: {extractor.output_dir}")
    print(f"🔧 提取方法: {method}")

    results = extractor.batch_extract(urls, method=method)

    # 统计
    success_count = sum(1 for r in results.values() if r.get("success"))
    print(f"\n📊 完成: {success_count}/{len(urls)} 成功")

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        method = sys.argv[2] if len(sys.argv) > 2 else "auto"
        batch_extract_from_file(sys.argv[1], method=method)
    else:
        print("用法: python article_batch_extractor.py <urls.txt> [method]")
        print("method: auto (默认), jina, browser")
        print("")
        print("示例:")
        print("  python article_batch_extractor.py urls.txt")
        print("  python article_batch_extractor.py urls.txt jina")
        print("  python article_batch_extractor.py urls.txt browser")
