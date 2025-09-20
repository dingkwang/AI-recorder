"""
AI增强版录音机 - 主应用入口
"""
import os
import uvicorn
from dotenv import load_dotenv
from app.api import app

# 加载环境变量
load_dotenv()

if __name__ == "__main__":
    # 检查必要的环境变量
    if not os.getenv("ASSEMBLYAI_API_KEY"):
        print("❌ 错误: 请设置 ASSEMBLYAI_API_KEY 环境变量")
        print("   在 .env 文件中添加: ASSEMBLYAI_API_KEY=your_api_key_here")
        exit(1)
    
    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("🚀 启动 AI增强版录音机...")
    print(f"📡 服务地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔧 调试模式: {debug}")
    
    # 启动服务
    uvicorn.run(
        "app.api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )