"""健康检查接口。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health")
async def health_check():
    """返回服务健康状态。

    第一阶段仅返回基础状态，不依赖数据库。
    """
    return {
        "status": "ok",
        "service": "china-university-map-api",
    }