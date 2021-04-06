import time
from fastapi import Request
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
from common.middleware import AuthMiddleware
from system.routers import app
from system.settings import settings

# register database
register_tortoise(
    app,
    db_url=settings.get_db_url(),
    modules={'models': settings.models_path},
    generate_schemas=True,
    add_exception_handlers=True
)
app.add_middleware(AuthMiddleware, exclude=['/v1/public', '/docs', '/redoc', '/openapi'])

@app.middleware("http")
async def add_process_token_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == '__main__':
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT, log_level=settings.LOG_LEVEL,
                access_log=True, loop='uvloop', http='h11')
