import os
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
# from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv
from sqlalchemy import text

from controllers import api_router
from configs import get_session, async_session, engine, AsyncSession
from utils import register_exception_handlers

load_dotenv()

# 基本日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("app")

app = FastAPI()

# app.mount("/statics", StaticFiles(directory="statics"), name="statics")

app.include_router(api_router)

# Register all exception handlers
register_exception_handlers(app)


@app.on_event("startup")
async def on_startup():
    # 可选：启动时测试连接
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        logger.info("MySQL (SQLAlchemy async) connected")
    except Exception as e:
        logger.error("MySQL connection failed on startup: %s", e)


@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()
    print("Engine disposed")


@app.get("/")
def read_root():
    return {"Hello": "World"}

# Favicon 处理，避免 404 日志污染
@app.get("/favicon.ico")
async def favicon():
    # return {"file": "statics/favicon.ico"}
    return HTMLResponse(content="", media_type="image/x-icon")


# 测试接口：使用 SQLAlchemy 执行查询
@app.get("/test-db")
async def test_db(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(text("SELECT VERSION()"))
        version = result.scalar_one_or_none()
        return {"mysql_ok": bool(version), "version": version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))