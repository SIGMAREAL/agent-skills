# 提取方法详解

## Jina Reader

通用网页内容提取，返回 Markdown 格式。

```bash
curl "https://r.jina.ai/<url>"
```

**适用：** Twitter/X、技术博客、通用网页
**不适用：** 微信公众号（有验证码）

## browser-use + eval

需要 JS 渲染或反爬的网站。

```bash
browser-use open "<url>"
sleep 5
browser-use eval "document.body.innerText"
```

**选择器：**
- 通用：`document.body.innerText`
- 微信公众号：`document.getElementById('js_content').innerText`
- Twitter/X：`document.querySelector('article').innerText`

## YouTube 字幕 API

```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript(video_id)
```

## B站字幕 API（需 SESSDATA）

### 获取 SESSDATA

1. 浏览器登录 B站
2. F12 → Application → Cookies → bilibili.com
3. 找到 SESSDATA，复制 Value（约 200+ 字符）

**SESSDATA 有效期：** ~6 个月，或直到退出登录

### 保存 SESSDATA

```bash
mkdir -p ~/.cache/bilibili
cat > ~/.cache/bilibili/cookie.json << 'EOF'
{
  "SESSDATA": "你的SESSDATA值"
}
EOF
```

### 字幕提取脚本

```bash
# 单个视频
python3 ~/.claude/skills/video-summary/scripts/bilibili_subtitle.py "<B站URL>"

# 批量提取
python3 bilibili_subtitle.py batch urls.txt
```

**输出：** 纯文本字幕文件（371条字幕，约 8000+ 字符）

### API 原理

```
1. 获取视频 CID
   GET https://api.bilibili.com/x/web-interface/view?bvid={bvid}

2. 获取字幕列表
   GET https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}

3. 下载字幕
   GET https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod/{id}
```

## Whisper 语音转录

无字幕时使用，异步处理。

```bash
# 提交任务
python3 scripts/extract.py "<video_url>"

# 检查状态
python3 scripts/async_transcriber.py --status <task_id>
```
