# AI增强版录音机

一个集成了录音、转写、总结和聊天交互的AI应用。

## 功能特性

- 🎙️ 音频文件上传（MP3/WAV）
- 📝 高精度语音转写（AssemblyAI）
- 👥 说话人分离（Speaker Diarization）
- 💾 录音和转写文件存储
- 🤖 AI对话交互（基于转写内容）
- 📊 时间戳分段显示

## 快速开始

### 1. 安装依赖

```bash
# 使用uv（推荐）
uv sync

# 或使用pip
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入你的AssemblyAI API Key
```

### 3. 启动服务

```bash
uv run python main.py
```

访问 http://localhost:8000 使用应用。

## API文档

启动服务后访问 http://localhost:8000/docs 查看API文档。

## 项目结构

```
ai-recorder/
├── main.py                 # 主应用入口
├── app/
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   ├── services.py        # 核心业务逻辑
│   ├── api.py            # API路由
│   └── database.py       # 数据库操作
├── templates/            # HTML模板
├── static/              # 静态文件
├── uploads/             # 上传文件存储
└── transcripts/         # 转写结果存储
```