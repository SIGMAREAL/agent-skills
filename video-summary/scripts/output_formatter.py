#!/usr/bin/env python3
"""
输出格式化模块

按照 OUTPUT_FORMAT.md 规范生成统一的 Markdown 输出。
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# 导入质量评分器
sys.path.insert(0, str(Path(__file__).parent))
from quality_scorer import calculate_quality_score


# 预定义内容类型
CONTENT_TYPES = {
    "tutorial": "教程/教学",
    "news": "新闻/资讯",
    "analysis": "分析/深度报道",
    "interview": "采访/对话",
    "research": "研究/论文",
    "opinion": "观点/评论",
    "review": "产品/内容评测",
    "other": "其他",
}

# 预定义标签
PREDEFINED_TAGS = [
    "AI/机器学习",
    "编程/开发",
    "产品/设计",
    "商业/创业",
    "金融/投资",
    "科技/数码",
    "生活/健康",
    "心理/成长",
    "时事/新闻",
    "其他",
]

# 平台检测
PLATFORM_MAP = {
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "bilibili.com": "B站",
    "b23.tv": "B站",
    "twitter.com": "Twitter",
    "x.com": "Twitter",
    "weixin.qq.com": "公众号",
    "mp.weixin.qq.com": "公众号",
    "zhihu.com": "知乎",
    "juejin.cn": "掘金",
    "jianshu.com": "简书",
    "csdn.net": "CSDN",
    "medium.com": "Medium",
    "github.com": "GitHub",
}


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    清理文件名，移除不安全字符

    规则：
    - `/` `\` `:` `*` `?` `"` `<` `>` `|` → 替换为 `-`
    - 空格 → 替换为 `-`
    - 连续 `-` → 合并为一个
    - 限制长度
    """
    # 替换不安全字符
    text = re.sub(r'[/\\:*?"<>|]', '-', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-{2,}', '-', text)
    text = text.strip('-')

    # 截断
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]

    return text or "未命名"


def detect_platform(url: str) -> str:
    """检测平台"""
    url_lower = url.lower()
    for domain, platform in PLATFORM_MAP.items():
        if domain in url_lower:
            return platform
    return "其他"


def detect_language(text: str) -> str:
    """检测文本语言"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text)

    if total_chars == 0:
        return "unknown"

    chinese_ratio = chinese_chars / total_chars

    if chinese_ratio > 0.3:
        return "zh"
    elif chinese_ratio > 0.05:
        return "mixed"
    else:
        return "en"


def translate_title_to_zh(title: str) -> str:
    """
    翻译标题为中文

    注意：这是占位符函数，实际翻译由 Claude 完成
    这里只做简单处理：返回原标题，由 Claude 后续翻译
    """
    # 如果标题包含中文字符，认为已经是中文
    if re.search(r'[\u4e00-\u9fff]', title):
        return title

    # 否则返回原标题，等待 Claude 翻译
    return title


def generate_filename(
    title: str,
    author: str,
    type_zh: str,
    platform: str,
    date: str
) -> str:
    """
    生成文件名

    格式: {作者}_{中文标题}_【{类型}】{平台}-{日期}.md
    如果没有日期，格式为: {作者}_{中文标题}_【{类型}】{平台}.md
    """
    # 清理各部分
    title_clean = sanitize_filename(title, max_length=50)
    author_clean = sanitize_filename(author, max_length=20) if author else ""

    # 组装
    if author_clean:
        if date:
            filename = f"{author_clean}_{title_clean}_【{type_zh}】{platform}-{date}.md"
        else:
            filename = f"{author_clean}_{title_clean}_【{type_zh}】{platform}.md"
    else:
        if date:
            filename = f"{title_clean}_【{type_zh}】{platform}-{date}.md"
        else:
            filename = f"{title_clean}_【{type_zh}】{platform}.md"

    return filename


def generate_frontmatter(
    title: str,
    url: str,
    author: str,
    platform: str,
    source: str,
    publish_date: Optional[str],
    extracted_date: str,
    content_type: str,
    language: str,
    duration: Optional[str],
    transcript: str,
) -> Dict[str, Any]:
    """
    生成 YAML frontmatter 数据
    """
    # 计算信息质量分
    quality_result = calculate_quality_score(transcript)

    # ⚠️ 日期规则：绝不自动用 extracted_date 填充 publish_date
    # publish_date 必须从 API 或页面元数据获取
    # 如果获取不到，保持为 None 或空字符串

    # 语言检测
    if not language or language == "unknown":
        language = detect_language(transcript)

    frontmatter = {
        "title": title,
        "title_zh": "",  # 由 Claude 填充
        "author": author or "",
        "platform": platform,
        "source": source or platform,
        "url": url,
        "publish_date": publish_date or "",  # 保持为空，不自动填充
        "extracted_date": extracted_date,
        "type": content_type,
        "language": language,
        "duration": duration or "",
        "word_count": quality_result["word_count"],
        "quality_score": quality_result["score"],
        "tags": [],  # 由 Claude 选择
    }

    return frontmatter


def frontmatter_to_yaml(data: Dict[str, Any]) -> str:
    """将字典转换为 YAML frontmatter 格式"""
    lines = ["---"]

    for key, value in data.items():
        if isinstance(value, list):
            if value:
                # 列表格式
                items = ', '.join(f'"{v}"' for v in value)
                lines.append(f"{key}: [{items}]")
            else:
                lines.append(f"{key}: []")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif value is None or value == "":
            lines.append(f"{key}: ")
        else:
            lines.append(f"{key}: {value}")

    lines.append("---")
    return "\n".join(lines)


def generate_markdown(
    title: str,
    url: str,
    author: str,
    platform: str,
    source: str,
    publish_date: Optional[str],
    transcript: str,
    content_type: str = "other",
    language: str = "zh",
    duration: Optional[str] = None,
    description: str = "",
) -> tuple[str, Dict[str, Any]]:
    """
    生成完整的 Markdown 内容

    返回: (markdown_content, frontmatter_data)
    """
    now = datetime.now()
    extracted_date = now.strftime("%Y-%m-%d")

    # 生成 frontmatter
    frontmatter_data = generate_frontmatter(
        title=title,
        url=url,
        author=author,
        platform=platform,
        source=source,
        publish_date=publish_date,
        extracted_date=extracted_date,
        content_type=content_type,
        language=language,
        duration=duration,
        transcript=transcript,
    )

    # 类型中文
    type_zh = CONTENT_TYPES.get(content_type, "其他")

    # 生成文件名
    title_zh = frontmatter_data["title_zh"] or translate_title_to_zh(title)
    date_for_filename = frontmatter_data["publish_date"]

    filename = generate_filename(
        title=title_zh,
        author=author,
        type_zh=type_zh,
        platform=platform,
        date=date_for_filename,
    )

    # 信息质量分
    qs = frontmatter_data["quality_score"]

    # 生成内容
    yaml_str = frontmatter_to_yaml(frontmatter_data)

    content = f"""{yaml_str}

# {title}

## 📊 信息概览

| 属性 | 值 |
|------|-----|
| 类型 | {type_zh} |
| 平台 | {platform} |
| 作者 | {author or '-'} |
| 发布日期 | {frontmatter_data['publish_date']} |
| 信息质量 | {qs}/100 |

> [原始链接]({url})

---

## 📝 入门级总结（小白友好）

{{CLAUDE_BEGINNER_SUMMARY_PLACEHOLDER}}

---

## 📝 标准级总结

{{CLAUDE_STANDARD_SUMMARY_PLACEHOLDER}}

---

## 📝 深入级总结（专业版）

{{CLAUDE_EXPERT_SUMMARY_PLACEHOLDER}}

---

## 📄 中文全文

{{CLAUDE_FULLTEXT_PLACEHOLDER}}

---

## 📋 原始内容

{transcript}

---

*提取时间: {now.strftime("%Y-%m-%d %H:%M")} | 信息质量分: {qs}/100*
"""

    return content, frontmatter_data


def save_markdown(
    content: str,
    filename: str,
    output_dir: Path,
) -> Path:
    """保存 Markdown 文件"""
    output_path = output_dir / filename
    output_path.write_text(content, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    # 测试
    test_title = "Deep Learning Tutorial for Beginners"
    test_url = "https://youtube.com/watch?v=test"
    test_author = "AI Expert"
    test_transcript = "这是一个关于深度学习的教程。深度学习是人工智能的重要分支。神经网络是其核心。"

    content, fm = generate_markdown(
        title=test_title,
        url=test_url,
        author=test_author,
        platform="YouTube",
        source="YouTube",
        publish_date="2025-12-25",
        transcript=test_transcript,
        content_type="tutorial",
    )

    print(content)
    print("\n=== Filename ===")
    print(generate_filename(
        title="深度学习入门",
        author="李宏毅",
        type_zh="教程",
        platform="YouTube",
        date="2025-12-25",
    ))
