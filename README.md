# ร้านโชห่วย API

## Setup

```bash
# 1. clone แล้ว install
pip install -r requirements.txt

# 2. copy env
cp .env.example .env
# แก้ DATABASE_URL และ SECRET_KEY ใน .env

# 3. สร้าง database บน Supabase แล้ว run schema.sql
# เอาไฟล์ schema.sql ไป paste ใน Supabase SQL Editor แล้วกด Run

# 4. run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## โครงสร้างไฟล์

```
chohuay-api/
├── main.py                  # FastAPI app + register routers
├── requirements.txt
├── .env                     # ไม่ commit ขึ้น git
├── schema.sql               # SQL สำหรับ Supabase
│
├── core/
│   ├── config.py            # อ่าน .env
│   ├── database.py          # SQLAlchemy async engine
│   ├── security.py          # hash PIN, สร้าง/decode JWT
│   └── dependencies.py      # get_current_user, require_owner
│
├── models/                  # SQLAlchemy ORM (map กับตาราง DB)
│   ├── user.py
│   ├── product.py           # Product, ProductVariant, BundleRule, Category
│   ├── stock.py             # Stock, PurchaseLog
│   ├── sale.py              # Sale, SaleItem
│   ├── customer.py
│   ├── debt.py              # DebtTransaction
│   └── service.py           # ServiceTransaction
│
└── routers/                 # API endpoints แยกตาม domain
    ├── auth.py              # POST /auth/login (PIN → JWT)
    ├── products.py          # CRUD สินค้า + bundle rules
    ├── stock.py             # รับสินค้าเข้า, ดูสต๊อก
    ├── sales.py             # บันทึกขาย, ยกเลิกบิล, เช็ค bundle price
    ├── customers.py         # CRUD ลูกค้า
    ├── debt.py              # ดูหนี้, รับชำระ
    ├── services.py          # บันทึกโอนเงิน/เติมเงิน
    └── reports.py           # รายงานกำไร, สต๊อกต่ำ, สินค้าขายดี
```

## API Docs

เปิด http://localhost:8000/docs จะเห็น Swagger UI ครบทุก endpoint

## Role

| Role  | ทำอะไรได้                                      |
|-------|-----------------------------------------------|
| owner | ทุกอย่าง                                       |
| staff | ขายสินค้า, บันทึกโอนเงิน/เติมเงิน เท่านั้น    |

## สร้าง user แรก (owner)

```python
# run ครั้งเดียวใน python shell
import bcrypt
pin = "1234"
hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
print(hashed)
# เอา hash ไป INSERT ใน Supabase:
# INSERT INTO users (name, pin_hash, role) VALUES ('พ่อ', '<hash>', 'owner');
```