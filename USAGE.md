# AI增强版录音机使用说明

## 🎯 项目概述

这是一个基于AssemblyAI的AI增强版录音机，具备以下核心功能：

- 🎙️ **音频上传**: 支持MP3、WAV、M4A、FLAC、OGG格式
- 📝 **语音转写**: 使用AssemblyAI Universal模型进行高精度转写
- 👥 **说话人分离**: 自动识别和分离不同说话人
- 💾 **数据存储**: SQLite数据库存储录音和转写记录
- 📊 **智能摘要**: 自动生成转写摘要和统计信息
- 🌐 **Web界面**: 现代化的用户界面
- 🔌 **REST API**: 完整的API接口

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install assemblyai fastapi uvicorn[standard] python-multipart python-dotenv pydantic sqlalchemy jinja2 aiofiles requests

# 设置AssemblyAI API密钥（可选，演示模式无需）
export ASSEMBLYAI_API_KEY="your_api_key_here"
```

### 2. 启动应用

```bash
# 启动服务
python3 main.py

# 服务将在 http://localhost:8002 启动
```

### 3. 访问应用

- **Web界面**: http://localhost:8002
- **API文档**: http://localhost:8002/docs
- **健康检查**: http://localhost:8002/api/health

## 📱 使用方式

### Web界面使用

1. 打开浏览器访问 http://localhost:8002
2. 点击"选择音频文件"上传音频
3. 配置转写选项：
   - 说话人分离：启用/禁用
   - 预期说话人数：1-10人
   - 转写模型：Universal（推荐）或Best
4. 点击"开始转写"
5. 等待转写完成，查看结果

### API使用

#### 上传音频文件

```bash
curl -X POST \
  -F "file=@your_audio.mp3" \
  -F "enable_speaker_diarization=true" \
  -F "speakers_expected=2" \
  -F "model=universal" \
  http://localhost:8002/api/upload
```

#### 获取转写记录

```bash
# 获取所有转写记录
curl http://localhost:8002/api/transcripts

# 获取特定转写记录
curl http://localhost:8002/api/transcripts/{transcript_id}
```

#### 获取转写摘要

```bash
curl http://localhost:8002/api/transcripts/{transcript_id}/summary
```

## 🔧 配置说明

### 环境变量

在 `.env` 文件中配置：

```env
# AssemblyAI API Key（可选）
ASSEMBLYAI_API_KEY=your_api_key_here

# 服务器配置
HOST=0.0.0.0
PORT=8002
DEBUG=True

# 文件存储
UPLOAD_DIR=uploads
TRANSCRIPT_DIR=transcripts
```

### 演示模式

如果没有设置 `ASSEMBLYAI_API_KEY`，应用会自动进入演示模式：
- 接受任何格式的文件上传
- 生成模拟的转写结果
- 用于测试和演示功能

## 📊 功能特性

### 转写功能

- **高精度转写**: 使用AssemblyAI Universal模型
- **说话人分离**: 自动识别不同说话人
- **时间戳**: 精确到毫秒的时间标记
- **置信度**: 转写质量评分
- **多语言支持**: 自动检测语言

### 数据管理

- **文件存储**: 原始音频文件保存
- **转写存储**: JSON格式存储转写结果
- **数据库**: SQLite数据库管理记录
- **元数据**: 完整的文件和信息记录

### Web界面

- **现代化设计**: 响应式界面设计
- **实时状态**: 上传和转写进度显示
- **交互式查看**: 转写结果可视化展示
- **摘要生成**: 一键生成转写摘要

## 🛠️ 开发说明

### 项目结构

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
├── transcripts/         # 转写结果存储
└── demo.py              # 演示脚本
```

### 核心组件

1. **TranscriptService**: 转写服务
   - AssemblyAI集成
   - 演示模式支持
   - 转写结果处理

2. **AudioService**: 音频文件服务
   - 文件格式验证
   - 文件大小检查

3. **Database**: 数据库服务
   - SQLite操作
   - 记录管理

4. **FastAPI**: Web框架
   - REST API
   - 文件上传
   - 后台任务

## 🔮 扩展功能

### 已实现

- ✅ 音频上传和转写
- ✅ 说话人分离
- ✅ 转写结果存储
- ✅ Web界面
- ✅ REST API
- ✅ 转写摘要

### 待扩展

- 🔄 LLM集成（聊天交互）
- 🔄 实时转写
- 🔄 多模态问答
- 🔄 角色识别优化
- 🔄 音频回放功能
- 🔄 批量处理
- 🔄 用户认证
- 🔄 云端部署

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 修改 .env 文件中的 PORT 设置
   PORT=8003
   ```

2. **文件上传失败**
   - 检查文件格式是否支持
   - 检查文件大小是否过大
   - 检查上传目录权限

3. **转写失败**
   - 检查AssemblyAI API密钥
   - 检查网络连接
   - 查看应用日志

4. **数据库错误**
   - 检查SQLite文件权限
   - 重新初始化数据库

### 日志查看

应用运行时会在控制台输出详细日志，包括：
- 转写进度
- 错误信息
- 调试信息

## 📄 许可证

本项目仅供学习和演示使用。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！