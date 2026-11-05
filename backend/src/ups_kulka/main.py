from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ups_kulka.container import Container
from ups_kulka.modules.admin_auth.presentation import router as admin_auth_router
from ups_kulka.modules.banners.presentation import router as banners_router
from ups_kulka.modules.catalog.presentation import router as catalog_router
from ups_kulka.modules.media.presentation import router as media_router
from ups_kulka.modules.orders.presentation import router as orders_router
from ups_kulka.modules.payments.presentation import router as payments_router
from ups_kulka.shared.presentation.errors import register_error_handlers

# Every module's presentation router: registered and wired for DI.
ROUTER_MODULES = (
    admin_auth_router,
    banners_router,
    catalog_router,
    media_router,
    orders_router,
    payments_router,
)


def create_app(container: Container | None = None) -> FastAPI:
    container = container or Container()
    container.wire(modules=list(ROUTER_MODULES))

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await container.engine().dispose()

    app = FastAPI(title="УПС! Кулька API", version="0.1.0", lifespan=lifespan)
    app.state.container = container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)

    media_dir = Path(container.settings().media_root)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

    @app.get("/healthz", tags=["system"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    for module in ROUTER_MODULES:
        app.include_router(module.router)
    return app


app = create_app()
