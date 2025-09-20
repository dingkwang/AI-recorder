"""
数据模型定义
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Utterance(BaseModel):
    """说话片段"""
    speaker: str
    start: int  # 开始时间（毫秒）
    end: int    # 结束时间（毫秒）
    text: str   # 转写文本
    confidence: Optional[float] = None  # 置信度


class Transcript(BaseModel):
    """转写结果"""
    id: Optional[str] = None
    audio_file_path: str
    text: str  # 完整转写文本
    utterances: List[Utterance]  # 分段说话内容
    duration: Optional[float] = None  # 音频时长（秒）
    language: Optional[str] = None
    created_at: Optional[datetime] = None
    status: str = "completed"  # completed, processing, failed


class AudioUpload(BaseModel):
    """音频上传请求"""
    filename: str
    content_type: str
    size: int


class TranscriptRequest(BaseModel):
    """转写请求"""
    audio_file_path: str
    enable_speaker_diarization: bool = True
    speakers_expected: Optional[int] = None
    model: str = "universal"  # universal, best


class ChatMessage(BaseModel):
    """聊天消息"""
    transcript_id: str
    message: str
    timestamp: Optional[datetime] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    relevant_segments: List[Utterance] = []  # 相关的转写片段
    timestamp: Optional[datetime] = None