from fastapi import FastAPI

from starlette.requests import Request

from caffeine import app_info
from caffeine.common.settings import Settings
from caffeine.rest.bootstrap import FastApiBootstrap


app = FastAPI(title=app_info.name, version=app_info.version)

settings = Settings()
settings.read_env()

web = FastApiBootstrap(app, settings)


@app.middleware("http")
async def add_states_middleware(request: Request, call_next):
    request.state.health_service = web.states['health_service']
    request.state.user_service = web.states['user_service']
    request.state.recaptcha = web.states['recaptcha']
    response = await call_next(request)
    return response

app.add_event_handler("startup", web.init)
app.add_event_handler("shutdown", web.shutdown)


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
