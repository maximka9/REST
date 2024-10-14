# app/main.py
from fastapi import FastAPI, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api import user, task

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.state.limiter = limiter

app.include_router(user.router)
app.include_router(task.router)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@limiter.limit("100/minute")  
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response

for route in user.router.routes:
    if route.path not in ["/users/", "/login"]:
        route.dependencies.append(Depends(limiter.limit("100/minute")))

