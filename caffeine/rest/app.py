from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from caffeine.common.settings import Settings
from caffeine.rest.bootstrap import WebBaseBootstrap

app = Starlette()


settings = Settings()
settings.read_env()

web = WebBaseBootstrap(app, settings)

app.add_event_handler("startup", web.init)
app.add_event_handler("shutdown", web.shutdown)


@app.route("/")
async def homepage(request):
    return PlainTextResponse("This is messeeks, look at me!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
