-- ============================================================
--  ร้านโชห่วย — Database Schema
--  PostgreSQL
-- ============================================================

-- ────────────────────────────────────────────────────────────
--  AUTH
-- ────────────────────────────────────────────────────────────
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    pin_hash    VARCHAR(255) NOT NULL,
    role        VARCHAR(20)  NOT NULL
                CHECK (role IN ('owner','staff')),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
--  PRODUCTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE categories (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL
);

CREATE TYPE product_type AS ENUM (
    'unit',
    'bulk_weight',
    'farm'
);

CREATE TYPE cost_source AS ENUM (
    'makro', 'super_cheap', 'market', 'delivery', 'farm', 'other'
);

CREATE TABLE products (
    id                SERIAL PRIMARY KEY,
    category_id       INT           REFERENCES categories(id),
    name              VARCHAR(200)  NOT NULL,
    product_type      product_type  NOT NULL DEFAULT 'unit',
    barcode           VARCHAR(100),
    cost_source       cost_source   NOT NULL DEFAULT 'other',

    -- unit / farm
    cost_price        NUMERIC(10,2),
    sell_price        NUMERIC(10,2) NOT NULL,
    sell_unit         VARCHAR(50)   NOT NULL DEFAULT 'ชิ้น',

    -- bulk_weight
    bulk_unit         VARCHAR(50),
    bulk_qty          NUMERIC(10,3),
    bulk_cost         NUMERIC(10,2),
    sell_qty_per_unit NUMERIC(10,3),
    -- cost_price = bulk_cost / (bulk_qty / sell_qty_per_unit)

    is_active         BOOLEAN       NOT NULL DEFAULT TRUE,
    deleted_at        TIMESTAMPTZ,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE TABLE product_variants (
    id          SERIAL PRIMARY KEY,
    product_id  INT           NOT NULL REFERENCES products(id),
    name        VARCHAR(100)  NOT NULL,
    cost_price  NUMERIC(10,2),
    sell_price  NUMERIC(10,2) NOT NULL,
    is_active   BOOLEAN       NOT NULL DEFAULT TRUE
);

CREATE TABLE bundle_rules (
    id            SERIAL PRIMARY KEY,
    product_id    INT           NOT NULL REFERENCES products(id),
    min_qty       INT           NOT NULL,
    bundle_price  NUMERIC(10,2) NOT NULL,
    is_active     BOOLEAN       NOT NULL DEFAULT TRUE
);

-- ────────────────────────────────────────────────────────────
--  STOCK
-- ────────────────────────────────────────────────────────────
CREATE TABLE stock (
    id          SERIAL PRIMARY KEY,
    product_id  INT           NOT NULL REFERENCES products(id) UNIQUE,
    variant_id  INT           REFERENCES product_variants(id),
    quantity    NUMERIC(10,3) NOT NULL DEFAULT 0,
    min_qty     NUMERIC(10,3) NOT NULL DEFAULT 5,
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE TABLE purchase_logs (
    id          SERIAL PRIMARY KEY,
    product_id  INT           NOT NULL REFERENCES products(id),
    variant_id  INT           REFERENCES product_variants(id),
    qty         NUMERIC(10,3) NOT NULL,
    unit_cost   NUMERIC(10,2) NOT NULL,
    total_cost  NUMERIC(10,2) NOT NULL,
    source      cost_source   NOT NULL DEFAULT 'other',
    note        TEXT,
    created_by  INT           NOT NULL REFERENCES users(id),
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
--  CUSTOMERS & DEBT
-- ────────────────────────────────────────────────────────────
CREATE TABLE customers (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(200) NOT NULL,
    phone        VARCHAR(20),
    note         TEXT,
    credit_limit NUMERIC(10,2) DEFAULT 500,
    is_active    BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
--  SALES
-- ────────────────────────────────────────────────────────────
CREATE TYPE payment_method AS ENUM (
    'cash',
    'qr'
);

CREATE TABLE sales (
    id              SERIAL PRIMARY KEY,
    customer_id     INT             REFERENCES customers(id),
    is_credit       BOOLEAN         NOT NULL DEFAULT FALSE,
    payment_method  payment_method  NOT NULL DEFAULT 'cash',
    slip_image_url  TEXT,                          -- optional ถ่ายสลิปเก็บ
    total_amount    NUMERIC(10,2)   NOT NULL,
    total_cost      NUMERIC(10,2)   NOT NULL,
    note            TEXT,
    created_by      INT             NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    cancelled_at    TIMESTAMPTZ,
    cancelled_by    INT             REFERENCES users(id)
);

CREATE TABLE sale_items (
    id              SERIAL PRIMARY KEY,
    sale_id         INT           NOT NULL REFERENCES sales(id),
    product_id      INT           NOT NULL REFERENCES products(id),
    variant_id      INT           REFERENCES product_variants(id),
    qty             NUMERIC(10,3) NOT NULL,
    unit_price      NUMERIC(10,2) NOT NULL,
    unit_cost       NUMERIC(10,2) NOT NULL,
    bundle_rule_id  INT           REFERENCES bundle_rules(id)
);

-- ────────────────────────────────────────────────────────────
--  DEBT TRANSACTIONS
-- ────────────────────────────────────────────────────────────
CREATE TYPE debt_tx_type AS ENUM (
    'charge',
    'payment'
);

CREATE TABLE debt_transactions (
    id           SERIAL PRIMARY KEY,
    customer_id  INT           NOT NULL REFERENCES customers(id),
    type         debt_tx_type  NOT NULL,
    amount       NUMERIC(10,2) NOT NULL,
    sale_id      INT           REFERENCES sales(id),
    note         TEXT,
    created_by   INT           NOT NULL REFERENCES users(id),
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
--  SERVICE TRANSACTIONS (โอนเงิน / เติมเงิน)
-- ────────────────────────────────────────────────────────────
CREATE TYPE service_type AS ENUM (
    'transfer',   -- โอนเงิน
    'topup'       -- เติมเงิน
);

CREATE TABLE service_transactions (
    id          SERIAL PRIMARY KEY,
    type        service_type    NOT NULL,
    amount      NUMERIC(10,2)   NOT NULL,  -- จำนวนเงินที่ลูกค้าโอน/เติม
    fee         NUMERIC(10,2)   NOT NULL,  -- ค่าธรรมเนียมที่ร้านได้
    note        TEXT,
    created_by  INT             NOT NULL REFERENCES users(id),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────────
--  VIEWS
-- ────────────────────────────────────────────────────────────
CREATE VIEW customer_balance AS
SELECT
    c.id            AS customer_id,
    c.name,
    c.credit_limit,
    COALESCE(SUM(
        CASE WHEN dt.type = 'charge'  THEN  dt.amount
             WHEN dt.type = 'payment' THEN -dt.amount
        END
    ), 0)           AS balance,
    MAX(dt.created_at) AS last_transaction
FROM customers c
LEFT JOIN debt_transactions dt ON dt.customer_id = c.id
GROUP BY c.id, c.name, c.credit_limit;

CREATE VIEW daily_summary AS
SELECT
    d.sale_date,
    COALESCE(d.total_sales, 0)                          AS total_sales,
    COALESCE(d.revenue, 0)                              AS revenue,
    COALESCE(d.cost, 0)                                 AS cost,
    COALESCE(d.profit, 0)                               AS profit,
    COALESCE(svc.service_fee_income, 0)                 AS service_fee_income,
    COALESCE(d.profit, 0) + COALESCE(svc.service_fee_income, 0) AS total_income
FROM (
    SELECT
        DATE(created_at)                AS sale_date,
        COUNT(*)                        AS total_sales,
        SUM(total_amount)               AS revenue,
        SUM(total_cost)                 AS cost,
        SUM(total_amount - total_cost)  AS profit
    FROM sales
    WHERE cancelled_at IS NULL
    GROUP BY DATE(created_at)
) d
LEFT JOIN (
    SELECT
        DATE(created_at)    AS sale_date,
        SUM(fee)            AS service_fee_income
    FROM service_transactions
    GROUP BY DATE(created_at)
) svc ON svc.sale_date = d.sale_date
ORDER BY d.sale_date DESC;

CREATE VIEW low_stock_alert AS
SELECT
    p.id, p.name, p.sell_unit,
    s.quantity, s.min_qty
FROM stock s
JOIN products p ON p.id = s.product_id
WHERE s.quantity <= s.min_qty
  AND p.is_active;

-- ────────────────────────────────────────────────────────────
--  INDEXES
-- ────────────────────────────────────────────────────────────
CREATE INDEX idx_sales_created_at        ON sales(created_at);
CREATE INDEX idx_sales_customer          ON sales(customer_id);
CREATE INDEX idx_sale_items_sale         ON sale_items(sale_id);
CREATE INDEX idx_debt_tx_customer        ON debt_transactions(customer_id);
CREATE INDEX idx_debt_tx_created         ON debt_transactions(created_at);
CREATE INDEX idx_products_barcode        ON products(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_purchase_logs_product   ON purchase_logs(product_id);
CREATE INDEX idx_service_tx_created      ON service_transactions(created_at);