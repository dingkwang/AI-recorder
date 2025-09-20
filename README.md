## AI 增强版录音机 · Transcript MVP

使用 AssemblyAI 完成「录音转写 +（可选）说话人分离」，并将结果导出为 TXT/JSON/SRT/VTT。项目使用 uv 管理 Python 环境与依赖。

### 环境准备（uv）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# 重新打开终端或执行 eval 以加载 uv 到 PATH

# 安装依赖（会自动创建 .venv）
uv sync
```

### 配置 API Key

```bash
cp .env.example .env
${EDITOR:-vi} .env
# 将 ASSEMBLYAI_API_KEY 填入你的密钥
```

### 命令行使用

```bash
# 查看帮助
uv run ai-recorder --help

# 本地文件转写（默认启用说话人分离，使用 universal 模型）
uv run ai-recorder transcribe ./path/to/audio.mp3 \
  --out-dir outputs \
  --format txt --format json --format srt

# 远程 URL 音频
uv run ai-recorder transcribe "https://example.com/audio.wav" \
  --speakers-expected 3

# 关闭说话人分离
uv run ai-recorder transcribe ./audio.mp3 --no-diarization
```

输出文件：
- TXT：纯文本转写
- JSON：包含全文、分段（含 speaker/start/end）等元数据
- SRT/VTT：基于分段导出字幕（建议在启用 diarization 时使用）

### 开发结构

```
src/
  ai_recorder/
    cli.py          # Typer CLI
    config.py       # 读取 .env / 环境变量
    transcriber.py  # AssemblyAI 转写与字幕生成
```

### 环境变量

```
ASSEMBLYAI_API_KEY=your_api_key_here
```

### 备注

- 默认使用 AssemblyAI `universal` 模型，适合嘈杂环境与口音鲁棒性需求。
- SRT/VTT 导出基于 `utterances`（说话人分段）。未启用 diarization 时，可能无法生成理想的时间轴字幕。
- 你可以将导出的 JSON 直接用于后续聊天检索与时间戳跳转。

