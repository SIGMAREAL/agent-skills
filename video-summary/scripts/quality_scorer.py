#!/usr/bin/env python3
"""
信息质量评分计算器

无需大模型，基于统计学和信息论方法计算文本信息质量。

用法:
    python quality_scorer.py "文本内容"
    echo "文本内容" | python quality_scorer.py -
    python quality_scorer.py file.txt
"""

import sys
import re
from pathlib import Path
from typing import Dict, Tuple


def detect_language(text: str) -> str:
    """检测文本主要语言"""
    # 简单检测：中文字符比例
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


def tokenize(text: str, language: str = "mixed") -> list:
    """分词"""
    if language in ["zh", "mixed"]:
        # 中文按字符/词组混合，英文按单词
        # 提取中文连续词语（2字以上）和英文单词
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        english_words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        return chinese_words + english_words
    else:
        # 英文按单词
        return re.findall(r'[a-zA-Z]{3,}', text.lower())


def calculate_ttr(text: str) -> float:
    """计算 Type-Token Ratio (词汇丰富度)"""
    words = tokenize(text, detect_language(text))
    if len(words) == 0:
        return 0
    unique_words = set(words)
    return len(unique_words) / len(words)


def density_score(ttr: float) -> int:
    """信息密度分 (40%)"""
    if ttr > 0.5:
        return 95
    elif ttr > 0.4:
        return 82
    elif ttr > 0.3:
        return 67
    elif ttr > 0.2:
        return 50
    else:
        return 20


def has_conclusion(text: str) -> bool:
    """检测是否有明确结论"""
    conclusion_patterns = [
        r'(总结|总之|综上|因此|所以|最终|结论|归纳)',
        r'(in conclusion|to sum up|therefore|thus|finally)',
        r'(结论|总结).{0,50}',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in conclusion_patterns)


def has_data(text: str) -> bool:
    """检测是否包含数据/统计"""
    data_patterns = [
        r'\d+%',  # 百分比
        r'\d+\s*(万|亿|千|million|billion|k)',
        r'(数据|统计|研究|调查显示|according to)',
        r'(数据|研究).{0,30}(显示|表明|发现)',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in data_patterns)


def has_example(text: str) -> bool:
    """检测是否包含案例/示例"""
    example_patterns = [
        r'(例如|比如|举例|例如|for example|for instance|e\.g\.)',
        r'(案例|例子|示例)',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in example_patterns)


def has_technical_terms(text: str) -> bool:
    """检测是否包含专业术语"""
    # 常见技术术语模式
    tech_patterns = [
        r'\b[A-Z]{2,}\b',  # 大写缩写 (API, AI, ML)
        r'[a-z]+[A-Z]',  # 驼峰命名
        r'(函数|变量|算法|模型|神经网络|api|sdk)',
    ]
    return sum(1 for p in tech_patterns if re.search(p, text)) >= 2


def avg_sentence_length(text: str) -> float:
    """计算平均句子长度（字数）"""
    # 按句号、问号、感叹号分割
    sentences = re.split(r'[。！？.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0

    lengths = [len(s) for s in sentences]
    return sum(lengths) / len(lengths)


def has_structure(text: str) -> bool:
    """检测是否有章节结构"""
    # 检测标题、列表等结构标记
    structure_patterns = [
        r'^#{1,3}\s',  # Markdown 标题
        r'^\s*[-*+]\s',  # 列表
        r'^\s*\d+\.\s',  # 数字列表
        r'(第[一二三四五六七八九十]+[章节部分]|chapter|part)',
    ]
    multiline = text.split('\n')
    return sum(1 for line in multiline if any(re.search(p, line) for p in structure_patterns)) >= 3


def completeness_score(text: str) -> int:
    """完整性分 (30%)"""
    score = 0

    if has_conclusion(text):
        score += 25
    if has_data(text):
        score += 20
    if has_structure(text):
        score += 15
    if has_example(text):
        score += 15

    # 有开头引入
    lines = text.split('\n')[:5]
    intro_patterns = [r'(本文|今天|最近|近年来|in this article)']
    if any(re.search(p, ' '.join(lines), re.IGNORECASE) for p in intro_patterns):
        score += 10

    # 有结尾总结
    lines = text.split('\n')[-5:]
    if has_conclusion(' '.join(lines)):
        score += 10

    return min(score, 100)


def complexity_score(text: str) -> int:
    """复杂度分 (30%)"""
    score = 0

    if has_technical_terms(text):
        score += 20

    if avg_sentence_length(text) > 15:
        score += 15

    # 检测对比/因果
    contrast_patterns = [r'(但是|然而|相反|对比|however|conversely|in contrast)',
                         r'(因为|由于|导致|because|due to|leads to)']
    if any(re.search(p, text, re.IGNORECASE) for p in contrast_patterns):
        score += 15

    # 检测时间线/流程
    flow_patterns = [r'(首先|然后|最后|第一步|next|finally|step)',
                     r'(第一|第二|第三|first|second|third)']
    if any(re.search(p, text, re.IGNORECASE) for p in flow_patterns):
        score += 15

    return min(score, 100)


def calculate_quality_score(text: str) -> Dict:
    """
    计算信息质量分

    返回格式:
    {
        "score": 78,           # 总分 0-100
        "density": 82,         # 信息密度分
        "completeness": 65,    # 完整性分
        "complexity": 85,      # 复杂度分
        "ttr": 0.45,           # 词汇丰富度
        "word_count": 2500,    # 字数
        "language": "zh"       # 语言
    }
    """
    if not text or len(text.strip()) == 0:
        return {
            "score": 0,
            "density": 0,
            "completeness": 0,
            "complexity": 0,
            "ttr": 0,
            "word_count": 0,
            "language": "unknown"
        }

    # 清理文本
    text = text.strip()

    # 基本信息
    language = detect_language(text)
    word_count = len(text)
    ttr = calculate_ttr(text)

    # 各项得分
    density = density_score(ttr)
    complete = completeness_score(text)
    complex = complexity_score(text)

    # 总分 = 密度×40% + 完整性×30% + 复杂度×30%
    total = int(density * 0.4 + complete * 0.3 + complex * 0.3)

    return {
        "score": min(100, max(0, total)),
        "density": density,
        "completeness": complete,
        "complexity": complex,
        "ttr": round(ttr, 3),
        "word_count": word_count,
        "language": language
    }


def main():
    if len(sys.argv) < 1:
        print("用法: python quality_scorer.py <文本|文件路径|->")
        sys.exit(1)

    input_arg = sys.argv[1]

    # 读取输入
    if input_arg == '-':
        # 从 stdin 读取
        text = sys.stdin.read()
    elif Path(input_arg).exists():
        # 从文件读取
        text = Path(input_arg).read_text(encoding='utf-8')
    else:
        # 直接使用输入作为文本
        text = input_arg

    result = calculate_quality_score(text)

    # 输出 JSON 格式
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
