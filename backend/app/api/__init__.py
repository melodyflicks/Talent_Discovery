from .assistant import router as assistant_router
from .auth import router as auth_router
from .courses import router as courses_router
from .employees import router as employees_router
from .hr import router as hr_router
from .matching import router as matching_router
from .profiles import router as profiles_router
from .roadmap import router as roadmap_router
from .roles import router as roles_router
from .skill_gaps import router as skill_gaps_router
from .skills import router as skills_router

routers = [
    auth_router,
    employees_router,
    profiles_router,
    skills_router,
    roles_router,
    matching_router,
    skill_gaps_router,
    courses_router,
    roadmap_router,
    assistant_router,
    hr_router,
]

__all__ = ["routers"]
