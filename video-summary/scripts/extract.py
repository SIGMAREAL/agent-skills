#!/usr/bin/env python3
"""
Content Extractor - 视频/文章提取 + AI 中文提炼总结
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def detect_content_type(url: str) -> str:
    """检测内容类型"""
    url_lower = url.lower()
    if any(p in url_lower for p in ['bilibili.com', 'youtube.com', 'youtu.be', 'douyin.com']):
        return "video"
    return "article"

def extract_video(url: str) -> dict:
    """提取视频"""
    from src.async_transcriber import submit_task
    task_id = submit_task(url, model="small")
    return {"type": "video", "task_id": task_id, "message": f"视频转录任务已提交: {task_id}"}

def extract_article(url: str) -> dict:
    """提取文章并自动生成中文总结"""
    from src.article_extractor import ArticleExtractor

    extractor = ArticleExtractor()
    result = extractor.extract(url)

    if not result['success']:
        return result

    # 保存原始内容（中文总结由 Claude Code 生成）
    output_path = extractor.save_raw(result)

    return {
        "success": True,
        "type": "article",
        "title": result['title'],
        "output_path": str(output_path),
        "content": result['content'][:500]
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python extract.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    content_type = detect_content_type(url)

    print(f"检测类型: {content_type}")
    print(f"URL: {url}")
    print("-" * 40)

    if content_type == "video":
        result = extract_video(url)
        print(f"✅ {result['message']}")
    else:
        result = extract_article(url)
        if result['success']:
            print(f"✅ 文章提取完成")
            print(f"📁 保存到: {result['output_path']}")
            print(f"\n标题: {result['title']}")
        else:
            print(f"❌ 错误: {result.get('error')}")

if __name__ == "__main__":
    main()
