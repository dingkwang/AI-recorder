"""
FastAPI路由定义
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import Transcript, TranscriptRequest, ChatMessage, ChatResponse
from .services import TranscriptService, AudioService
from .database import Database

# 初始化FastAPI应用
app = FastAPI(
    title="AI增强版录音机",
    description="录音转写总结聊天应用",
    version="0.1.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化模板
templates = Jinja2Templates(directory="templates")

# 初始化服务
transcript_service = TranscriptService()
audio_service = AudioService()
db = Database()

# 确保上传目录存在
os.makedirs("uploads", exist_ok=True)
os.makedirs("transcripts", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/api/upload")
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    enable_speaker_diarization: bool = Form(True),
    speakers_expected: Optional[int] = Form(None),
    model: str = Form("universal")
):
    """
    上传音频文件并开始转写
    """
    try:
        # 验证文件类型（演示模式跳过验证）
        if not transcript_service.demo_mode:
            if not audio_service.validate_audio_file(file.filename):
                raise HTTPException(status_code=400, detail="不支持的音频格式")
        
        # 生成唯一ID
        recording_id = str(uuid.uuid4())
        transcript_id = str(uuid.uuid4())
        
        # 保存上传的文件
        file_path = f"uploads/{recording_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = len(content)
        
        # 保存录音记录到数据库
        db.save_recording(recording_id, file.filename, file_path, file_size)
        
        # 后台执行转写
        background_tasks.add_task(
            process_transcription,
            recording_id,
            transcript_id,
            file_path,
            enable_speaker_diarization,
            speakers_expected,
            model
        )
        
        return JSONResponse({
            "recording_id": recording_id,
            "transcript_id": transcript_id,
            "status": "uploaded",
            "message": "文件上传成功，正在转写中..."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


async def process_transcription(
    recording_id: str,
    transcript_id: str,
    file_path: str,
    enable_speaker_diarization: bool,
    speakers_expected: Optional[int],
    model: str
):
    """后台处理转写任务"""
    try:
        # 执行转写
        transcript = transcript_service.transcribe_audio(
            file_path,
            enable_speaker_diarization,
            speakers_expected,
            model
        )
        
        # 保存转写结果
        transcript_path = f"transcripts/{transcript_id}.json"
        transcript_service.save_transcript(transcript, transcript_path)
        
        # 保存到数据库
        db.save_transcript(transcript_id, recording_id, transcript)
        
        print(f"转写完成: {transcript_id}")
        
    except Exception as e:
        print(f"转写失败: {str(e)}")


@app.get("/api/transcripts")
async def get_transcripts():
    """获取所有转写记录"""
    try:
        transcripts = db.get_all_transcripts()
        return JSONResponse({"transcripts": transcripts})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取转写记录失败: {str(e)}")


@app.get("/api/transcripts/{transcript_id}")
async def get_transcript(transcript_id: str):
    """获取特定转写记录"""
    try:
        transcript_data = db.get_transcript(transcript_id)
        if not transcript_data:
            raise HTTPException(status_code=404, detail="转写记录不存在")
        
        return JSONResponse(transcript_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取转写记录失败: {str(e)}")


@app.get("/api/recordings")
async def get_recordings():
    """获取所有录音记录"""
    try:
        recordings = db.get_all_recordings()
        return JSONResponse({"recordings": recordings})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取录音记录失败: {str(e)}")


@app.get("/api/transcripts/{transcript_id}/summary")
async def get_transcript_summary(transcript_id: str):
    """获取转写摘要"""
    try:
        transcript_data = db.get_transcript(transcript_id)
        if not transcript_data:
            raise HTTPException(status_code=404, detail="转写记录不存在")
        
        # 重构Transcript对象
        from .models import Utterance
        utterances = [Utterance(**utt) for utt in transcript_data['utterances']]
        transcript = Transcript(
            id=transcript_data['id'],
            audio_file_path="",  # 不需要
            text=transcript_data['text'],
            utterances=utterances,
            duration=transcript_data['duration'],
            language=transcript_data['language'],
            created_at=datetime.fromisoformat(transcript_data['created_at']) if transcript_data.get('created_at') else None,
            status=transcript_data['status']
        )
        
        summary = transcript_service.get_transcript_summary(transcript)
        return JSONResponse({"summary": summary})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取摘要失败: {str(e)}")


@app.post("/api/chat")
async def chat_with_transcript(chat_message: ChatMessage):
    """
    与转写内容进行聊天交互
    注意：这里只是基础实现，实际需要集成LLM
    """
    try:
        # 获取转写记录
        transcript_data = db.get_transcript(chat_message.transcript_id)
        if not transcript_data:
            raise HTTPException(status_code=404, detail="转写记录不存在")
        
        # 简单的关键词匹配（实际应用中需要集成LLM）
        response_text = f"收到您的消息: {chat_message.message}\n\n"
        response_text += f"转写内容长度: {len(transcript_data['text'])} 字符\n"
        response_text += f"说话人数量: {len(set(utt['speaker'] for utt in transcript_data['utterances']))}\n\n"
        response_text += "这是基础版本，后续会集成LLM进行智能问答。"
        
        # 查找相关片段（简单实现）
        relevant_segments = []
        if "预算" in chat_message.message:
            for utt in transcript_data['utterances']:
                if "预算" in utt['text']:
                    relevant_segments.append(utt)
        
        return JSONResponse({
            "response": response_text,
            "relevant_segments": relevant_segments[:3],  # 最多返回3个相关片段
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天交互失败: {str(e)}")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return JSONResponse({"status": "healthy", "timestamp": datetime.now().isoformat()})