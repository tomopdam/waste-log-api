from fastapi import APIRouter

router = APIRouter()


def register_routers():
    from app.routers import analytics, auth, teams, users, waste_log

    router.include_router(auth.router)
    router.include_router(users.router)
    router.include_router(teams.router)
    router.include_router(waste_log.router)
    router.include_router(analytics.router)
