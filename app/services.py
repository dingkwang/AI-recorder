"""
核心业务逻辑服务
"""
import assemblyai as aai
import os
import json
from typing import Optional, List
from datetime import datetime
import logging

from .models import Transcript, Utterance, TranscriptRequest

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptService:
    """转写服务"""
    
    def __init__(self):
        """初始化AssemblyAI客户端"""
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            logger.warning("ASSEMBLYAI_API_KEY not set, using demo mode")
            self.demo_mode = True
            self.transcriber = None
        else:
            aai.settings.api_key = api_key
            self.transcriber = aai.Transcriber()
            self.demo_mode = False
            logger.info("AssemblyAI transcriber initialized")
    
    def transcribe_audio(
        self, 
        audio_file_path: str, 
        enable_speaker_diarization: bool = True,
        speakers_expected: Optional[int] = None,
        model: str = "universal"
    ) -> Transcript:
        """
        转写音频文件
        
        Args:
            audio_file_path: 音频文件路径
            enable_speaker_diarization: 是否启用说话人分离
            speakers_expected: 预期说话人数量
            model: 使用的模型 (universal, best)
        
        Returns:
            Transcript: 转写结果
        """
        try:
            logger.info(f"Starting transcription for: {audio_file_path}")
            
            # 演示模式
            if self.demo_mode:
                logger.info("Running in demo mode - generating mock transcript")
                return self._generate_demo_transcript(audio_file_path, enable_speaker_diarization)
            
            # 配置转写参数
            config = aai.TranscriptionConfig(
                speaker_labels=enable_speaker_diarization,
                speakers_expected=speakers_expected,
                model=model
            )
            
            # 执行转写
            transcript_result = self.transcriber.transcribe(audio_file_path, config=config)
            
            # 处理转写结果
            utterances = []
            if transcript_result.utterances:
                for utt in transcript_result.utterances:
                    utterances.append(Utterance(
                        speaker=utt.speaker,
                        start=utt.start,
                        end=utt.end,
                        text=utt.text,
                        confidence=getattr(utt, 'confidence', None)
                    ))
            
            # 创建Transcript对象
            transcript = Transcript(
                audio_file_path=audio_file_path,
                text=transcript_result.text,
                utterances=utterances,
                duration=getattr(transcript_result, 'audio_duration', None),
                language=getattr(transcript_result, 'language_code', None),
                created_at=datetime.now(),
                status="completed"
            )
            
            logger.info(f"Transcription completed successfully. Duration: {transcript.duration}s")
            return transcript
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise Exception(f"转写失败: {str(e)}")
    
    def _generate_demo_transcript(self, audio_file_path: str, enable_speaker_diarization: bool) -> Transcript:
        """生成演示用的转写结果"""
        import time
        time.sleep(2)  # 模拟转写时间
        
        demo_text = "这是一个演示转写结果。在实际使用中，这里会显示真实的语音转写内容。"
        
        if enable_speaker_diarization:
            utterances = [
                Utterance(speaker="A", start=0, end=3000, text="这是一个演示转写结果。", confidence=0.95),
                Utterance(speaker="B", start=3000, end=6000, text="在实际使用中，这里会显示真实的语音转写内容。", confidence=0.92)
            ]
        else:
            utterances = [
                Utterance(speaker="Speaker", start=0, end=6000, text=demo_text, confidence=0.93)
            ]
        
        return Transcript(
            audio_file_path=audio_file_path,
            text=demo_text,
            utterances=utterances,
            duration=6.0,
            language="zh-CN",
            created_at=datetime.now(),
            status="completed"
        )
    
    def save_transcript(self, transcript: Transcript, output_path: str) -> str:
        """
        保存转写结果到文件
        
        Args:
            transcript: 转写结果
            output_path: 输出文件路径
        
        Returns:
            str: 保存的文件路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存为JSON格式
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript.dict(), f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Transcript saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save transcript: {str(e)}")
            raise Exception(f"保存转写结果失败: {str(e)}")
    
    def load_transcript(self, transcript_path: str) -> Transcript:
        """
        从文件加载转写结果
        
        Args:
            transcript_path: 转写文件路径
        
        Returns:
            Transcript: 转写结果
        """
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换utterances
            utterances = [Utterance(**utt) for utt in data.get('utterances', [])]
            
            transcript = Transcript(
                id=data.get('id'),
                audio_file_path=data['audio_file_path'],
                text=data['text'],
                utterances=utterances,
                duration=data.get('duration'),
                language=data.get('language'),
                created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
                status=data.get('status', 'completed')
            )
            
            return transcript
            
        except Exception as e:
            logger.error(f"Failed to load transcript: {str(e)}")
            raise Exception(f"加载转写结果失败: {str(e)}")
    
    def get_transcript_summary(self, transcript: Transcript) -> str:
        """
        生成转写摘要
        
        Args:
            transcript: 转写结果
        
        Returns:
            str: 摘要文本
        """
        summary_parts = []
        
        # 基本信息
        summary_parts.append(f"📝 转写摘要")
        summary_parts.append(f"⏱️ 时长: {transcript.duration:.1f}秒" if transcript.duration else "⏱️ 时长: 未知")
        summary_parts.append(f"🗣️ 说话人数: {len(set(utt.speaker for utt in transcript.utterances))}")
        summary_parts.append(f"📄 总字数: {len(transcript.text)}")
        
        # 说话人统计
        speaker_counts = {}
        for utt in transcript.utterances:
            speaker_counts[utt.speaker] = speaker_counts.get(utt.speaker, 0) + len(utt.text)
        
        summary_parts.append("\n🗣️ 说话人统计:")
        for speaker, char_count in sorted(speaker_counts.items()):
            summary_parts.append(f"  {speaker}: {char_count} 字符")
        
        return "\n".join(summary_parts)


class AudioService:
    """音频文件服务"""
    
    @staticmethod
    def validate_audio_file(file_path: str) -> bool:
        """
        验证音频文件格式
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 是否有效
        """
        # 演示模式：接受任何文件
        return True
        
        # 生产模式：验证音频格式
        # valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        # _, ext = os.path.splitext(file_path.lower())
        # return ext in valid_extensions
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
        
        Returns:
            int: 文件大小（字节）
        """
        return os.path.getsize(file_path)