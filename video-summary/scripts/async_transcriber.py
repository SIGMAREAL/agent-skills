"""
异步视频转录服务 - 支持 Markdown 输出
"""

import os
import json
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

# 任务状态
class TaskStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"


class AsyncTranscriber:
    """异步转录器"""

    def __init__(
        self,
        output_dir: str = "~/Documents/video-transcribe",
        task_dir: str = "~/.cache/video-transcribe/tasks"
    ):
        self.output_dir = Path(output_dir).expanduser()
        self.task_dir = Path(task_dir).expanduser()

        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.task_dir.mkdir(parents=True, exist_ok=True)

    def _get_task_path(self, task_id: str) -> Path:
        return self.task_dir / task_id

    def create_task(self, url: str, platform: str = "auto") -> str:
        """创建转录任务，返回任务ID"""
        task_id = f"transcribe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task_path = self._get_task_path(task_id)
        task_path.mkdir(exist_ok=True)

        # 获取视频信息
        video_info = self._get_video_info(url)

        # 保存任务信息
        task_info = {
            "task_id": task_id,
            "url": url,
            "platform": platform,
            "video_info": video_info,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "message": "任务已创建",
            "output_path": None,
            "error": None
        }

        (task_path / "info.json").write_text(
            json.dumps(task_info, indent=2, ensure_ascii=False)
        )

        return task_id

    def _get_video_info(self, url: str) -> Dict[str, Any]:
        """获取视频基本信息"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-playlist', url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "title": data.get("title", ""),
                    "uploader": data.get("uploader", ""),
                    "uploader_id": data.get("uploader_id", ""),
                    "channel": data.get("channel", ""),
                    "duration": data.get("duration", 0),
                    "thumbnail": data.get("thumbnail", ""),
                    "description": data.get("description", "")[:500],
                    "upload_date": data.get("upload_date", ""),  # YYYYMMDD 格式
                }
        except Exception:
            pass
        return {}

    def _try_get_subtitles(self, url: str, language: str = "zh") -> Optional[str]:
        """尝试获取平台字幕，成功返回文本，失败返回 None"""
        url_lower = url.lower()

        # YouTube: 用 youtube-transcript-api
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return self._get_youtube_subtitles(url, language)

        # B站: 用 yt-dlp 提取字幕
        if "bilibili.com" in url_lower:
            return self._get_bilibili_subtitles(url, language)

        # 其他平台: 用 yt-dlp 通用字幕提取
        return self._get_ytdlp_subtitles(url, language)

    def _get_youtube_subtitles(self, url: str, language: str) -> Optional[str]:
        """YouTube 字幕提取"""
        try:
            import re
            # 提取 video_id
            match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
            if not match:
                return None
            video_id = match.group(1)

            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()

            # 尝试获取字幕，优先中文，然后英文，最后自动生成的
            lang_codes = [language, 'zh-Hans', 'zh-Hant', 'en']
            transcript = api.fetch(video_id, languages=lang_codes)

            lines = [entry.text for entry in transcript.snippets]
            text = '\n'.join(lines)
            return text if len(text) > 50 else None

        except Exception:
            return None

    def _get_bilibili_subtitles(self, url: str, language: str) -> Optional[str]:
        """B站字幕提取（通过 API）"""
        try:
            import re
            import requests

            # 提取 BV 号
            match = re.search(r'(BV[a-zA-Z0-9]+)', url)
            if not match:
                return None
            bvid = match.group(1)

            # 获取 cid
            resp = requests.get(
                f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}',
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=10
            )
            data = resp.json().get('data', {})
            cid = data.get('cid')
            aid = data.get('aid')
            if not cid or not aid:
                return None

            # 获取字幕列表
            resp = requests.get(
                f'https://api.bilibili.com/x/player/wbi/v2?aid={aid}&cid={cid}',
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=10
            )
            subtitle_info = resp.json().get('data', {}).get('subtitle', {})
            subtitles = subtitle_info.get('subtitles', [])

            if not subtitles:
                return None

            # 优先中文字幕
            sub_url = None
            for sub in subtitles:
                if 'zh' in sub.get('lan', ''):
                    sub_url = sub.get('subtitle_url')
                    break
            if not sub_url and subtitles:
                sub_url = subtitles[0].get('subtitle_url')

            if not sub_url:
                return None

            # 下载字幕内容
            if sub_url.startswith('//'):
                sub_url = 'https:' + sub_url
            resp = requests.get(sub_url, timeout=10)
            sub_data = resp.json()

            lines = [item['content'] for item in sub_data.get('body', [])]
            text = '\n'.join(lines)
            return text if len(text) > 50 else None

        except Exception:
            return None

    def _get_ytdlp_subtitles(self, url: str, language: str) -> Optional[str]:
        """通用 yt-dlp 字幕提取"""
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run([
                    'yt-dlp', '--write-sub', '--write-auto-sub',
                    '--sub-lang', f'{language},zh,en',
                    '--sub-format', 'vtt/srt/best',
                    '--skip-download',
                    '-o', os.path.join(tmpdir, 'sub'),
                    '--quiet', '--no-warnings',
                    url
                ], capture_output=True, text=True, timeout=60)

                # 查找生成的字幕文件
                import glob
                sub_files = glob.glob(os.path.join(tmpdir, 'sub*.vtt')) + \
                            glob.glob(os.path.join(tmpdir, 'sub*.srt'))

                if not sub_files:
                    return None

                content = Path(sub_files[0]).read_text(encoding='utf-8')
                # 简单清理 VTT/SRT 格式
                import re
                # 去掉时间戳行和序号行
                lines = content.split('\n')
                text_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if re.match(r'^\d+$', line):
                        continue
                    if re.match(r'^\d{2}:\d{2}', line):
                        continue
                    if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                        continue
                    if '<' in line:
                        line = re.sub(r'<[^>]+>', '', line)
                    text_lines.append(line)

                # 去重（VTT 经常有重复行）
                seen = set()
                unique_lines = []
                for line in text_lines:
                    if line not in seen:
                        seen.add(line)
                        unique_lines.append(line)

                text = '\n'.join(unique_lines)
                return text if len(text) > 50 else None

        except Exception:
            return None

    def start_task(
        self,
        task_id: str,
        model: str = "small",
        language: str = "zh",
        output_format: str = "markdown"  # markdown, txt, json, srt
    ):
        """后台启动任务"""
        def run():
            task_path = self._get_task_path(task_id)
            info_path = task_path / "info.json"

            try:
                # 读取任务信息
                info = json.loads(info_path.read_text())
                url = info["url"]
                video_info = info.get("video_info", {})

                # === 阶段0: 检查字幕 ===
                info["status"] = TaskStatus.DOWNLOADING.value
                info["message"] = "正在检查字幕..."
                info["progress"] = 5
                info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))

                subtitle_text = self._try_get_subtitles(url, language)

                if subtitle_text:
                    # 有字幕，直接用，跳过 Whisper
                    info["message"] = "已获取字幕，跳过语音识别"
                    info["progress"] = 80
                    info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))

                    txt_path = task_path / "subtitle.txt"
                    txt_path.write_text(subtitle_text, encoding='utf-8')
                else:
                    # 无字幕，走 Whisper 流程
                    # === 阶段1: 下载音频 ===
                    info["message"] = "无字幕，正在下载音频准备语音识别..."
                    info["progress"] = 10
                    info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))

                    audio_path = task_path / "audio.mp3"
                    result = subprocess.run([
                        'yt-dlp', '-x', '--audio-format', 'mp3',
                        '-o', str(audio_path),
                        '--quiet', '--no-warnings',
                        url
                    ], capture_output=True, text=True, timeout=600)

                    if result.returncode != 0 or not audio_path.exists():
                        raise Exception(f"下载失败: {result.stderr}")

                    # === 阶段2: Whisper 转录 ===
                    info["status"] = TaskStatus.TRANSCRIBING.value
                    info["message"] = "正在语音识别（Whisper）..."
                    info["progress"] = 30
                    info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))

                    txt_path = task_path / "audio.txt"
                    subprocess.run([
                        'whisper', str(audio_path),
                        '--model', model,
                        '--language', language,
                        '--output_format', 'txt',
                        '--output_dir', str(task_path)
                    ], capture_output=True, text=True, timeout=3600)

                # === 阶段3: 格式化输出 ===
                info["status"] = TaskStatus.FORMATTING.value
                info["message"] = "正在生成文档..."
                info["progress"] = 90
                info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))

                # 生成输出文件
                output_path = self._generate_output(
                    task_path, task_id, url, video_info, txt_path, output_format
                )

                # === 完成 ===
                info["status"] = TaskStatus.COMPLETED.value
                info["message"] = "转录完成" + ("（字幕）" if subtitle_text else "（Whisper）")
                info["progress"] = 100
                info["output_path"] = str(output_path)
                info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))

            except Exception as e:
                info["status"] = TaskStatus.FAILED.value
                info["message"] = f"失败: {str(e)}"
                info["error"] = str(e)
                info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False))

        # 后台线程执行
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return task_id

    def _generate_output(
        self,
        task_path: Path,
        task_id: str,
        url: str,
        video_info: Dict[str, Any],
        txt_path: Path,
        format: str
    ) -> Path:
        """生成输出文件"""

        # 读取原始转录
        if txt_path.exists():
            transcript = txt_path.read_text()
        else:
            transcript = ""

        # 生成日期文件夹
        date_folder = self.output_dir / datetime.now().strftime("%Y-%m-%d")
        date_folder.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        title = video_info.get("title", "untitled")[:50]
        # 清理文件名中的非法字符
        import re
        title = re.sub(r'[\\/:;*?"<>|]', '', title)
        title = title.strip().replace(' ', '-')

        platform = "unknown"
        if "bilibili" in url.lower():
            platform = "bilibili"
        elif "youtube" in url.lower():
            platform = "youtube"
        elif "douyin" in url.lower():
            platform = "douyin"

        filename = f"{datetime.now().strftime('%Y%m%d')}_{platform}_{title}"

        if format == "markdown":
            output_path = date_folder / f"{filename}.md"
            self._generate_markdown(output_path, task_id, url, video_info, transcript)
        elif format == "txt":
            output_path = date_folder / f"{filename}.txt"
            output_path.write_text(transcript)
        elif format == "json":
            output_path = date_folder / f"{filename}.json"
            self._generate_json(output_path, task_id, url, video_info, transcript)
        elif format == "srt" and txt_path.with_suffix(".srt").exists():
            output_path = txt_path.with_suffix(".srt")
        else:
            output_path = date_folder / f"{filename}.txt"
            output_path.write_text(transcript)

        return output_path

    def _generate_markdown(
        self,
        output_path: Path,
        task_id: str,
        url: str,
        video_info: Dict[str, Any],
        transcript: str
    ):
        """生成 Markdown 文件（使用新的输出格式规范）"""
        # 导入输出格式化模块
        from output_formatter import generate_markdown, save_markdown

        title = video_info.get("title", "Untitled")
        uploader = video_info.get("uploader", "")
        duration = video_info.get("duration", 0)

        # 格式化时长
        if duration:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = None

        # 检测平台
        from output_formatter import detect_platform
        platform = detect_platform(url)

        # 获取发布日期（如果有）
        upload_date = video_info.get("upload_date")  # yt-dlp 返回 YYYYMMDD 格式
        if upload_date and len(upload_date) >= 8:
            publish_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        else:
            publish_date = None  # 保持为 None，不使用 extracted_date

        # 生成 Markdown 内容
        content, frontmatter = generate_markdown(
            title=title,
            url=url,
            author=uploader,
            platform=platform,
            source=platform,
            publish_date=publish_date,
            transcript=transcript,
            content_type="other",  # 默认类型，由 Claude 后续判断
            language="zh",
            duration=duration_str,
        )

        # 生成新格式的文件名
        type_zh = "其他"  # 默认，由 Claude 后续更新
        # ⚠️ 只使用 publish_date，不使用 extracted_date
        date_for_filename = frontmatter.get("publish_date")  # 可能为 None

        from output_formatter import sanitize_filename, translate_title_to_zh
        title_zh = translate_title_to_zh(title)
        title_clean = sanitize_filename(title_zh, max_length=50)
        author_clean = sanitize_filename(uploader, max_length=20) if uploader else ""

        # 根据是否有日期决定文件名格式
        if author_clean:
            if date_for_filename:
                filename = f"{author_clean}_{title_clean}_【{type_zh}】{platform}-{date_for_filename}.md"
            else:
                filename = f"{author_clean}_{title_clean}_【{type_zh}】{platform}.md"
        else:
            filename = f"{title_clean}_【{type_zh}】{platform}-{date_for_filename}.md"

        # 使用新文件名保存
        new_output_path = output_path.parent / filename
        new_output_path.write_text(content, encoding="utf-8")

        # 如果旧文件名和新文件名不同，删除旧文件
        if output_path != new_output_path and output_path.exists():
            output_path.unlink()

        return new_output_path

    def _generate_json(
        self,
        output_path: Path,
        task_id: str,
        url: str,
        video_info: Dict[str, Any],
        transcript: str
    ):
        """生成 JSON 文件"""
        data = {
            "task_id": task_id,
            "url": url,
            "video_info": video_info,
            "transcript": transcript,
            "generated_at": datetime.now().isoformat()
        }
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def get_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        task_path = self._get_task_path(task_id)
        info_path = task_path / "info.json"

        if not info_path.exists():
            return None

        # 重试几次，防止后台线程写入时读到不完整的 JSON
        for _ in range(3):
            try:
                return json.loads(info_path.read_text())
            except (json.JSONDecodeError, OSError):
                time.sleep(0.5)

        return {"task_id": task_id, "status": "unknown", "message": "状态文件读取失败，可能正在写入"}

    def get_transcript(self, task_id: str) -> Optional[str]:
        """获取转录结果"""
        status = self.get_status(task_id)
        if status and status["status"] == TaskStatus.COMPLETED.value:
            output_path = status.get("output_path")
            if output_path and Path(output_path).exists():
                return Path(output_path).read_text()
        return None

    def list_tasks(self) -> list:
        """列出所有任务"""
        tasks = []
        for task_path in self.task_dir.iterdir():
            if task_path.is_dir():
                status = self.get_status(task_path.name)
                if status:
                    tasks.append({
                        "task_id": status["task_id"],
                        "url": status["url"],
                        "status": status["status"],
                        "message": status["message"],
                        "created_at": status["created_at"],
                        "output_path": status.get("output_path")
                    })
        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)


# 全局实例
transcriber = AsyncTranscriber()


def submit_task(
    url: str,
    platform: str = "auto",
    model: str = "small",
    language: str = "zh",
    output_format: str = "markdown"
) -> str:
    """提交转录任务"""
    task_id = transcriber.create_task(url, platform)
    transcriber.start_task(task_id, model, language, output_format)
    return task_id


def check_task(task_id: str) -> Dict:
    """检查任务状态"""
    status = transcriber.get_status(task_id)
    if not status:
        return {"error": "任务不存在"}

    return {
        "task_id": task_id,
        "status": status["status"],
        "message": status["message"],
        "progress": status.get("progress", 0),
        "output_path": status.get("output_path"),
        "error": status.get("error")
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python async_transcriber.py <video_url>           # 提交任务")
        print("  python async_transcriber.py --status <task_id>    # 检查状态")
        print("  python async_transcriber.py --list               # 列出任务")
        print("  python async_transcriber.py --cat <task_id>     # 查看结果")
        sys.exit(1)

    if sys.argv[1] == "--status" and len(sys.argv) > 2:
        result = check_task(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif sys.argv[1] == "--list":
        for task in transcriber.list_tasks():
            status_icon = "✅" if task["status"] == "completed" else "🔄" if task["status"] != "failed" else "❌"
            print(f"{status_icon} {task['task_id']} | {task['status']} | {task['message']}")
    elif sys.argv[1] == "--cat" and len(sys.argv) > 2:
        transcript = transcriber.get_transcript(sys.argv[2])
        if transcript:
            print(transcript)
        else:
            print("结果未完成或不存在")
    else:
        task_id = submit_task(sys.argv[1])
        print(f"✅ 任务已提交: {task_id}")
        print(f"   输出位置: ~/Documents/video-transcribe/")
        print(f"   格式: Markdown")
