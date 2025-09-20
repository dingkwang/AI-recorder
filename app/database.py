"""
数据库操作
"""
import sqlite3
import os
from typing import List, Optional
from datetime import datetime
import json

from .models import Transcript, Utterance


class Database:
    """SQLite数据库操作"""
    
    def __init__(self, db_path: str = "ai_recorder.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建录音记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recordings (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    duration REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'uploaded'
                )
            """)
            
            # 创建转写记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    id TEXT PRIMARY KEY,
                    recording_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    utterances_json TEXT,
                    duration REAL,
                    language TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed',
                    FOREIGN KEY (recording_id) REFERENCES recordings (id)
                )
            """)
            
            conn.commit()
    
    def save_recording(self, recording_id: str, filename: str, file_path: str, 
                      file_size: int, duration: Optional[float] = None) -> bool:
        """保存录音记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO recordings (id, filename, file_path, file_size, duration)
                    VALUES (?, ?, ?, ?, ?)
                """, (recording_id, filename, file_path, file_size, duration))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving recording: {e}")
            return False
    
    def save_transcript(self, transcript_id: str, recording_id: str, 
                       transcript: Transcript) -> bool:
        """保存转写记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 将utterances转换为JSON字符串
                utterances_json = json.dumps([
                    {
                        'speaker': utt.speaker,
                        'start': utt.start,
                        'end': utt.end,
                        'text': utt.text,
                        'confidence': utt.confidence
                    }
                    for utt in transcript.utterances
                ])
                
                cursor.execute("""
                    INSERT INTO transcripts (id, recording_id, text, utterances_json, 
                                           duration, language, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (transcript_id, recording_id, transcript.text, utterances_json,
                     transcript.duration, transcript.language, transcript.status))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return False
    
    def get_recording(self, recording_id: str) -> Optional[dict]:
        """获取录音记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_path, file_size, duration, created_at, status
                    FROM recordings WHERE id = ?
                """, (recording_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'filename': row[1],
                        'file_path': row[2],
                        'file_size': row[3],
                        'duration': row[4],
                        'created_at': row[5],
                        'status': row[6]
                    }
                return None
        except Exception as e:
            print(f"Error getting recording: {e}")
            return None
    
    def get_transcript(self, transcript_id: str) -> Optional[dict]:
        """获取转写记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, recording_id, text, utterances_json, duration, 
                           language, created_at, status
                    FROM transcripts WHERE id = ?
                """, (transcript_id,))
                row = cursor.fetchone()
                
                if row:
                    utterances = json.loads(row[3]) if row[3] else []
                    return {
                        'id': row[0],
                        'recording_id': row[1],
                        'text': row[2],
                        'utterances': utterances,
                        'duration': row[4],
                        'language': row[5],
                        'created_at': row[6],
                        'status': row[7]
                    }
                return None
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return None
    
    def get_all_recordings(self) -> List[dict]:
        """获取所有录音记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_path, file_size, duration, created_at, status
                    FROM recordings ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'filename': row[1],
                        'file_path': row[2],
                        'file_size': row[3],
                        'duration': row[4],
                        'created_at': row[5],
                        'status': row[6]
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error getting recordings: {e}")
            return []
    
    def get_all_transcripts(self) -> List[dict]:
        """获取所有转写记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.id, t.recording_id, t.text, t.utterances_json, 
                           t.duration, t.language, t.created_at, t.status,
                           r.filename
                    FROM transcripts t
                    JOIN recordings r ON t.recording_id = r.id
                    ORDER BY t.created_at DESC
                """)
                rows = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'recording_id': row[1],
                        'text': row[2],
                        'utterances': json.loads(row[3]) if row[3] else [],
                        'duration': row[4],
                        'language': row[5],
                        'created_at': row[6],
                        'status': row[7],
                        'filename': row[8]
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error getting transcripts: {e}")
            return []