"""Mini-OpenClaw backend entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 【关键点】在导入任何其他业务模块（如 config 或 provider）之前加载环境变量
# 这样可以确保其他模块在执行 import 时，os.getenv() 能够读取到 .env 中的 Key
# Load .env before any config/provider imports
load_dotenv()


# 此时加载配置，config 模块内部会读取已注入的环境变量
from config import config
from graph.agent import AgentManager
from tools.skills_scanner import write_snapshot

# 获取当前文件的绝对路径目录，作为项目运行的根基准路径
BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    定义 FastAPI 的生命周期管理器。
    用于处理服务启动时的初始化任务和关闭时的清理任务。
    """
    # Startup
    print("[startup] Mini-OpenClaw backend starting...")
    
    # 扫描 skills 目录并生成能力快照文件 SKILLS_SNAPSHOT.md
    write_snapshot(BASE_DIR)  #此部分需要详细了解
    # 实例化全局 Agent 管理器
    agent_manager = AgentManager(base_dir=BASE_DIR, config=config)
    try:
        # 执行重型初始化：建立模型连接、加载工具集
        agent_manager.initialize()
        print(f"[startup] Agent engine: {config.agent_engine}")
    except Exception as e:
        # 如果 LLM 配置缺失，记录警告但不停止服务（允许用户通过 API 动态配置）
        print(f"[startup] Warning: Agent initialization failed: {e}")
        print("[startup] Chat will not work until LLM provider is configured.")
    # 将核心对象存储在 app.state 中，方便在具体的 API 路由函数中通过 request.app 访问
    app.state.agent_manager = agent_manager
    app.state.base_dir = BASE_DIR

    yield  # 此处是分割点，应用运行期间会停留在这里

    # Shutdown     --- 停止阶段 (Shutdown) ---
    print("[shutdown] Mini-OpenClaw backend stopping...")

# 初始化 FastAPI 实例，传入生命周期处理器
app = FastAPI(title="Mini-OpenClaw", version="0.1.0", lifespan=lifespan)
# 配置 CORS 中间件，允许前端（通常是 port 3000）跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 【模块化路由注册】
# 这里的延迟导入是为了确保 app 实例已经创建，且避免循环引用
# Register routers
from api.chat import router as chat_router
from api.sessions import router as sessions_router
from api.files import router as files_router
from api.tokens import router as tokens_router
from api.compress import router as compress_router
from api.config_api import router as config_router

# 将各功能模块的路由挂载到总应用上
app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(files_router)
app.include_router(tokens_router)
app.include_router(compress_router)
app.include_router(config_router)


@app.get("/api/health")
async def health():
    """健康检查接口，用于确认后端服务和引擎状态"""
    return {"status": "ok", "engine": config.agent_engine}
