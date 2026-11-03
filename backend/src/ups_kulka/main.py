from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ups_kulka.container import Container
from ups_kulka.modules.catalog.presentation import router as catalog_router
from ups_kulka.shared.presentation.errors import register_error_handlers

# Every module's presentation router: registered and wired for DI.
ROUTER_MODULES = (catalog_router,)


def create_app(container: Container | None = None) -> FastAPI:
    container = container or Container()
    container.wire(modules=list(ROUTER_MODULES))

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await container.engine().dispose()

    app = FastAPI(title="УПС! Кулька API", version="0.1.0", lifespan=lifespan)
    app.state.container = container
    register_error_handlers(app)

    @app.get("/healthz", tags=["system"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    for module in ROUTER_MODULES:
        app.include_router(module.router)
    return app


app = create_app()
