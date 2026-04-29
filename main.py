from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.products import router as products_router
from routers.stock import router as stock_router
from routers.sales import router as sales_router
from routers.customers import router as customers_router
from routers.debt import router as debt_router
from routers.services import router as services_router
from routers.reports import router as reports_router

app = FastAPI(title="ร้านโชห่วย API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ตอน dev เปิดหมด ตอน prod ใส่ IP tablet จริง
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,      prefix="/auth",      tags=["auth"])
app.include_router(products_router,  prefix="/products",  tags=["products"])
app.include_router(stock_router,     prefix="/stock",     tags=["stock"])
app.include_router(sales_router,     prefix="/sales",     tags=["sales"])
app.include_router(customers_router, prefix="/customers", tags=["customers"])
app.include_router(debt_router,      prefix="/debt",      tags=["debt"])
app.include_router(services_router,  prefix="/services",  tags=["services"])
app.include_router(reports_router,   prefix="/reports",   tags=["reports"])

@app.get("/health")
def health():
    return {"status": "ok"}