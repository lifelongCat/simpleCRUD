from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.router import router as musician_router

app = FastAPI(
    title='Simple CRUD',
    version='1.0',
    lifespan=init_db
)
app.include_router(musician_router)


origins = (
    'http://localhost',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'],
    allow_headers=['*'],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={exc['loc'][1]: exc['msg'] for exc in exc.errors()}
    )
