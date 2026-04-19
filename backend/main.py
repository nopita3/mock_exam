from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference



from backend.middelwares.log_control import log_control
from backend.cores.exception import add_exception_handlers


from backend.database.sessions import create_db_tables
from backend.api.router import master_router


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(
    # Server start/stop listener
    lifespan=lifespan_handler,
)

add_exception_handlers(app)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. เพิ่ม Custom Middleware สำหรับ Logging (ที่คุณต้องการ) ---
app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # เริ่มจับเวลา
    start_time = perf_counter()
    response: Response = await call_next(request)
    process_time = round(perf_counter() - start_time, 4)


    # --- ส่วนที่เพิ่ม: พยายามแกะ User ID จาก Token ---
    auth_header = request.headers.get("Authorization")
    log_data = log_control(auth_header,request,response,process_time)


    
    return response



app.include_router(master_router)


app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
