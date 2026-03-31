from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.api.report_routes import router
from app.core.rate_limit import limiter, rate_limit_handler

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.include_router(router)
