#!/usr/bin/env python3
"""
AI增强版录音机演示脚本
"""
import requests
import json
import time
import os

def test_api():
    """测试API功能"""
    base_url = "http://localhost:8002"
    
    print("🎙️ AI增强版录音机演示")
    print("=" * 50)
    
    # 1. 健康检查
    print("1. 健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ 服务运行正常")
            print(f"   响应: {response.json()}")
        else:
            print("❌ 服务异常")
            return
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    print()
    
    # 2. 获取转写记录
    print("2. 获取转写记录...")
    try:
        response = requests.get(f"{base_url}/api/transcripts")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 当前有 {len(data['transcripts'])} 条转写记录")
            if data['transcripts']:
                for i, transcript in enumerate(data['transcripts'][:3]):  # 只显示前3条
                    print(f"   {i+1}. {transcript.get('filename', 'Unknown')} - {transcript.get('status', 'Unknown')}")
        else:
            print("❌ 获取转写记录失败")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print()
    
    # 3. 获取录音记录
    print("3. 获取录音记录...")
    try:
        response = requests.get(f"{base_url}/api/recordings")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 当前有 {len(data['recordings'])} 条录音记录")
            if data['recordings']:
                for i, recording in enumerate(data['recordings'][:3]):  # 只显示前3条
                    print(f"   {i+1}. {recording.get('filename', 'Unknown')} - {recording.get('status', 'Unknown')}")
        else:
            print("❌ 获取录音记录失败")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print()
    
    # 4. 演示上传（使用文本文件模拟）
    print("4. 演示上传功能...")
    print("   注意: 当前为演示模式，会生成模拟转写结果")
    
    # 创建一个模拟的音频文件
    demo_file = "demo_audio.txt"
    with open(demo_file, "w", encoding="utf-8") as f:
        f.write("这是一个演示音频文件")
    
    try:
        with open(demo_file, "rb") as f:
            files = {"file": (demo_file, f, "audio/mpeg")}
            data = {
                "enable_speaker_diarization": "true",
                "speakers_expected": "2",
                "model": "universal"
            }
            
            print("   正在上传文件...")
            response = requests.post(f"{base_url}/api/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 文件上传成功")
                print(f"   录音ID: {result['recording_id']}")
                print(f"   转写ID: {result['transcript_id']}")
                print(f"   状态: {result['status']}")
                
                # 等待转写完成
                transcript_id = result['transcript_id']
                print("   等待转写完成...")
                
                for i in range(10):  # 最多等待20秒
                    time.sleep(2)
                    try:
                        response = requests.get(f"{base_url}/api/transcripts/{transcript_id}")
                        if response.status_code == 200:
                            transcript = response.json()
                            if transcript.get('status') == 'completed':
                                print("✅ 转写完成!")
                                print(f"   转写文本: {transcript.get('text', '')[:100]}...")
                                print(f"   说话人数量: {len(set(utt['speaker'] for utt in transcript.get('utterances', [])))}")
                                print(f"   对话段数: {len(transcript.get('utterances', []))}")
                                break
                    except Exception as e:
                        print(f"   检查转写状态失败: {e}")
                else:
                    print("⏰ 转写超时")
                    
            else:
                print(f"❌ 上传失败: {response.text}")
                
    except Exception as e:
        print(f"❌ 上传测试失败: {e}")
    finally:
        # 清理演示文件
        if os.path.exists(demo_file):
            os.remove(demo_file)
    
    print()
    print("🎉 演示完成!")
    print(f"📱 访问 http://localhost:8002 使用Web界面")
    print(f"📚 API文档: http://localhost:8002/docs")

if __name__ == "__main__":
    test_api()