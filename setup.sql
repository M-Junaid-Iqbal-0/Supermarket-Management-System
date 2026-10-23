-- ══════════════════════════════════════════════════════════
--  RUN THIS ONCE in SQL Developer before starting the app
-- ══════════════════════════════════════════════════════════

-- Users table for login system
CREATE TABLE AppUser (
    UserID       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Username     VARCHAR2(50)  NOT NULL UNIQUE,
    PasswordHash VARCHAR2(255) NOT NULL,
    Role         VARCHAR2(20)  NOT NULL CHECK (Role IN ('admin', 'employee', 'customer')),
    EmployeeID   NUMBER,
    CustomerID   NUMBER,
    IsActive     NUMBER(1) DEFAULT 1,
    CONSTRAINT fk_user_employee FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL,
    CONSTRAINT fk_user_customer FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE SET NULL
);

-- Sale History table (completed/archived sales)
CREATE TABLE Sale_History (
    HistoryID    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OrigSaleID   NUMBER,
    CustomerID   NUMBER,
    EmployeeID   NUMBER,
    SaleDate     TIMESTAMP,
    TotalAmount  NUMBER(10,2),
    PaymentMethod VARCHAR2(50),
    AmountPaid   NUMBER(10,2),
    ArchivedAt   TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Seed a default admin account (password: admin123)
-- PasswordHash below is SHA256 of "admin123"
INSERT INTO AppUser (Username, PasswordHash, Role)
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin');

COMMIT;
