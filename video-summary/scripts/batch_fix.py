#!/usr/bin/env python3
"""
批量修正视频/文章文件的输出格式

根据 OUTPUT_FORMAT.md 规范，修正所有现有文件的格式：
1. 更新文件名格式
2. 补充/更新元数据
3. 重新组织内容结构
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 导入质量评分器
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
from quality_scorer import calculate_quality_score

# 预定义类型
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

# 平台映射
PLATFORM_MAP = {
    "youtube": "YouTube",
    "bilibili": "B站",
    "b站": "B站",
    "weixin": "公众号",
    "mp.weixin": "公众号",
    "twitter": "Twitter",
    "x.com": "Twitter",
    "zhihu": "知乎",
    "juejin": "掘金",
    "medium": "Medium",
}

# 标签关键词映射
TAG_KEYWORDS = {
    "AI/机器学习": ["AI", "人工智能", "machine learning", "deep learning", "神经网络", "ML", "LLM", "GPT"],
    "编程/开发": ["编程", "开发", "code", "python", "javascript", "react", "api", "代码"],
    "产品/设计": ["产品", "UI", "UX", "设计", "design", "user", "product"],
    "商业/创业": ["创业", "商业", "business", "entrepreneur", "盈利", "收入", "赚钱"],
    "金融/投资": ["投资", "金融", "理财", "股票", "money", "invest", "finance"],
    "科技/数码": ["科技", "数码", "手机", "电脑", "tech", "phone", "computer"],
    "生活/健康": ["生活", "健康", "health", "life", "健身", "养生"],
    "心理/成长": ["心理", "成长", "心态", "思维", "mindset", "psychology", "个人成长"],
    "时事/新闻": ["新闻", "时事", "事件", "news", "报道"],
}


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """清理文件名"""
    if not text:
        return ""
    # 替换不安全字符
    text = re.sub(r'[/\\:*?"<>|]', '-', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-{2,}', '-', text)
    text = text.strip('-')
    # 截断
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]
    return text or "未命名"


def detect_platform(filename: str, content: str) -> str:
    """检测平台"""
    filename_lower = filename.lower()
    content_lower = content.lower()

    # 从文件名检测
    for keyword, platform in PLATFORM_MAP.items():
        if keyword in filename_lower:
            return platform

    # 从内容检测
    if "youtube.com" in content_lower or "youtu.be" in content_lower:
        return "YouTube"
    if "bilibili.com" in content_lower or "b23.tv" in content_lower:
        return "B站"
    if "weixin.qq.com" in content_lower or "mp.weixin.qq.com" in content_lower:
        return "公众号"
    if "twitter.com" in content_lower or "x.com" in content_lower:
        return "Twitter"

    return "其他"


def detect_type(content: str, title: str = "") -> str:
    """根据内容检测类型"""
    text = (title + " " + content).lower()

    # 教程类
    if any(k in text for k in ["教程", "教学", "入门", "tutorial", "how to", "guide", "入门指南", "从零开始", "初学者"]):
        return "tutorial"
    # 新闻类
    if any(k in text for k in ["新闻", "资讯", "news", "报道", "周报", "日报", "weekly", "daily"]):
        return "news"
    # 分析类
    if any(k in text for k in ["分析", "深度", "analysis", "研究", "解读", "趋势", "深度"]):
        return "analysis"
    # 采访类
    if any(k in text for k in ["采访", "对话", "interview", "访谈", "对话", "问答"]):
        return "interview"
    # 评测类
    if any(k in text for k in ["评测", "review", "测评", "体验", "测评", "评测", "对比"]):
        return "review"
    # 观点类
    if any(k in text for k in ["观点", "opinion", "评论", "思考", "看法", "建议", "观点"]):
        return "opinion"

    return "other"


def extract_tags(content: str) -> List[str]:
    """根据内容提取标签"""
    content_lower = content.lower()
    tags = []

    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw.lower() in content_lower for kw in keywords):
            tags.append(tag)
            if len(tags) >= 3:
                break

    if not tags:
        tags = ["其他"]

    return tags


def extract_author(content: str) -> str:
    """从内容中提取作者"""
    # 尝试从 frontmatter 或内容中提取作者
    patterns = [
        r'^作者[：:]\s*(\S+)',
        r'^#\s+\S+[^\n]*by\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
        r'(?:Channel|channel)[：:]\s*(\S+)',
        r'(?:Uploader|uploader)[：:]\s*(\S+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            author = match.group(1).strip()
            # 过滤掉太短或太长的作者名
            if 2 <= len(author) <= 30:
                # 清理作者名
                author = re.sub(r'[^\w\s-]', '', author)
                return author.strip()

    return ""


def extract_date(filename: str) -> str:
    """从文件名提取日期"""
    # 尝试从文件名提取日期
    patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{4})(\d{2})(\d{2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            if len(match.group(1)) == 10:
                return match.group(1)
            elif len(match.group(1)) == 8:
                return f"{match.group(1)[:4]}-{match.group(1)[4:6]}-{match.group(1)[6:8]}"

    return datetime.now().strftime("%Y-%m-%d")


def parse_existing_frontmatter(content: str) -> Tuple[Dict, str]:
    """解析现有的 frontmatter"""
    frontmatter = {}

    # 匹配 YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        fm_content = match.group(1)
        body = match.group(2)

        # 解析字段
        for line in fm_content.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                frontmatter[key] = value
    else:
        body = content

    return frontmatter, body


def generate_frontmatter(data: Dict) -> str:
    """生成 YAML frontmatter"""
    lines = ["---"]

    for key, value in data.items():
        if isinstance(value, list):
            if value:
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


def generate_new_filename(title: str, author: str, type_zh: str, platform: str, date: str) -> str:
    """生成新文件名"""
    title_clean = sanitize_filename(title, max_length=50)
    author_clean = sanitize_filename(author, max_length=20) if author else ""

    if author_clean:
        return f"{title_clean}_{author_clean}_【{type_zh}】{platform}-{date}.md"
    else:
        return f"{title_clean}_【{type_zh}】{platform}-{date}.md"


def fix_file(filepath: Path) -> Tuple[str, str]:
    """
    修正单个文件
    返回: (新文件名, 状态)
    """
    try:
        content = filepath.read_text(encoding='utf-8')

        # 解析现有 frontmatter
        frontmatter, body = parse_existing_frontmatter(content)

        # 提取信息
        title = frontmatter.get('title', filepath.stem)
        author = frontmatter.get('author', '') or extract_author(body)
        platform = detect_platform(filepath.name, body)
        date = extract_date(filepath.name)

        # 检测类型
        content_type = frontmatter.get('type', detect_type(body))
        type_zh = CONTENT_TYPES.get(content_type, "其他")

        # 提取标签
        tags = extract_tags(body)
        if frontmatter.get('tags'):
            # 解析现有标签
            existing_tags = re.findall(r'"([^"]+)"', frontmatter['tags'])
            if existing_tags:
                tags = existing_tags[:3]

        # 计算信息质量分
        word_count = len(body)
        quality_result = calculate_quality_score(body)
        quality_score = quality_result.get('score', 0)

        # 检测语言
        language = frontmatter.get('language', 'en')
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', body))
        total_chars = len(body)
        if total_chars > 0 and chinese_chars / total_chars > 0.3:
            language = 'zh'

        # 生成新 frontmatter
        new_frontmatter = {
            "title": title,
            "title_zh": frontmatter.get('title_zh', ''),
            "author": author,
            "platform": platform,
            "source": frontmatter.get('source', platform),
            "url": frontmatter.get('url', ''),
            "publish_date": frontmatter.get('publish_date', date),
            "extracted_date": frontmatter.get('extracted_date', date),
            "type": content_type,
            "language": language,
            "duration": frontmatter.get('duration', ''),
            "word_count": word_count,
            "quality_score": quality_score,
            "tags": tags,
        }

        # 生成新文件名
        new_filename = generate_new_filename(
            title=new_frontmatter.get('title_zh', title) or title,
            author=author,
            type_zh=type_zh,
            platform=platform,
            date=new_frontmatter.get('publish_date', date)
        )

        return new_filename, "fixed"

    except Exception as e:
        return "", f"error: {str(e)}"


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python batch_fix.py <目录路径>")
        print("示例: python batch_fix.py ~/Documents/video-transcribe")
        sys.exit(1)

    root_dir = Path(sys.argv[1]).expanduser()

    if not root_dir.exists():
        print(f"目录不存在: {root_dir}")
        sys.exit(1)

    # 查找所有 md 文件
    md_files = list(root_dir.rglob("*.md"))

    print(f"找到 {len(md_files)} 个 Markdown 文件")

    fixed_count = 0
    error_count = 0

    for i, filepath in enumerate(md_files):
        new_filename, status = fix_file(filepath)

        if status == "fixed" and new_filename:
            new_filepath = filepath.parent / new_filename

            # 如果文件名变了，重命名文件
            if new_filepath != filepath:
                try:
                    filepath.rename(new_filepath)
                    print(f"✅ [{i+1}/{len(md_files)}] {filepath.name} -> {new_filename}")
                except Exception as e:
                    print(f"❌ [{i+1}/{len(md_files)}] 重命名失败: {filepath.name} - {e}")
                    error_count += 1
            else:
                print(f"✅ [{i+1}/{len(md_files)}] {filepath.name} (无需修改)")
            fixed_count += 1
        else:
            print(f"❌ [{i+1}/{len(md_files)}] {filepath.name} - {status}")
            error_count += 1

    print(f"\n完成: {fixed_count} 成功, {error_count} 失败")


if __name__ == "__main__":
    main()
