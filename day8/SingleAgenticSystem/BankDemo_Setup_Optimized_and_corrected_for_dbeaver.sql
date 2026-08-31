/* =====================================================================================
   BankDemo — schema + seed data for the single-agent "Database Analyst" demo.

   Domain:   Islamic-banking flavoured (Al-Wadiah / Mudaraba products, "Profit" not
             interest). All amounts in BDT.
   Design:   Account balances are NOT hand-typed — they are DERIVED from the ledger
             (Transactions) at the end of the script, so the two tables can never
             disagree. A sharp agent can cross-check SUM(Transactions.Amount) against
             Accounts.Balance and get the same number.
   Dates:    OpenedDate / TxnDate are all relative to GETDATE(), so "accounts opened in
             the last 30 days" always returns rows no matter when you run this.

   Run in SSMS / Azure Data Studio / sqlcmd against a SQL Server 2019+ instance.
   ===================================================================================== */

-------------------------------------------------------------------------------------
-- 0) Database
-------------------------------------------------------------------------------------
IF DB_ID('BankDemo') IS NULL
    CREATE DATABASE BankDemo;

USE BankDemo;


-------------------------------------------------------------------------------------
-- 1) Drop in dependency order (so the script is re-runnable)
-------------------------------------------------------------------------------------
IF OBJECT_ID('dbo.Transactions','U') IS NOT NULL DROP TABLE dbo.Transactions;
IF OBJECT_ID('dbo.Accounts','U')     IS NOT NULL DROP TABLE dbo.Accounts;
IF OBJECT_ID('dbo.AccountTypes','U') IS NOT NULL DROP TABLE dbo.AccountTypes;
IF OBJECT_ID('dbo.Customers','U')    IS NOT NULL DROP TABLE dbo.Customers;
IF OBJECT_ID('dbo.Branches','U')     IS NOT NULL DROP TABLE dbo.Branches;


-------------------------------------------------------------------------------------
-- 2) Schema
-------------------------------------------------------------------------------------
CREATE TABLE dbo.Branches (
    BranchId    INT IDENTITY(1,1) CONSTRAINT PK_Branches PRIMARY KEY,
    BranchCode  CHAR(4)       NOT NULL CONSTRAINT UQ_Branches_Code UNIQUE,
    BranchName  NVARCHAR(80)  NOT NULL,
    City        NVARCHAR(40)  NOT NULL
);

CREATE TABLE dbo.Customers (
    CustomerId  INT IDENTITY(1,1) CONSTRAINT PK_Customers PRIMARY KEY,
    FullName    NVARCHAR(100) NOT NULL,
    NidNumber   VARCHAR(17)   NOT NULL CONSTRAINT UQ_Customers_Nid UNIQUE,
    MobileNo    VARCHAR(20)   NOT NULL,
    Email       NVARCHAR(120) NULL,
    District    NVARCHAR(40)  NOT NULL,
    CreatedDate DATE          NOT NULL CONSTRAINT DF_Customers_Created DEFAULT (CAST(GETDATE() AS date))
);

CREATE TABLE dbo.AccountTypes (
    AccountTypeId INT IDENTITY(1,1) CONSTRAINT PK_AccountTypes PRIMARY KEY,
    TypeCode      VARCHAR(8)   NOT NULL CONSTRAINT UQ_AccountTypes_Code UNIQUE,
    TypeName      NVARCHAR(60) NOT NULL,
    IsIslamic     BIT          NOT NULL CONSTRAINT DF_AccountTypes_Islamic DEFAULT (1),
    ProfitRate    DECIMAL(5,2) NULL          -- indicative annual profit rate; NULL for current a/c
);

CREATE TABLE dbo.Accounts (
    AccountId     INT IDENTITY(1,1) CONSTRAINT PK_Accounts PRIMARY KEY,
    AccountNo     VARCHAR(16)  NOT NULL CONSTRAINT UQ_Accounts_No UNIQUE,
    CustomerId    INT          NOT NULL CONSTRAINT FK_Accounts_Customer   REFERENCES dbo.Customers(CustomerId),
    BranchId      INT          NOT NULL CONSTRAINT FK_Accounts_Branch     REFERENCES dbo.Branches(BranchId),
    AccountTypeId INT          NOT NULL CONSTRAINT FK_Accounts_Type       REFERENCES dbo.AccountTypes(AccountTypeId),
    OpenedDate    DATE         NOT NULL,
    Status        VARCHAR(10)  NOT NULL CONSTRAINT CK_Accounts_Status
                                        CHECK (Status IN ('Active','Dormant','Closed')),
    Currency      CHAR(3)      NOT NULL CONSTRAINT DF_Accounts_Ccy DEFAULT ('BDT'),
    Balance       DECIMAL(18,2) NOT NULL CONSTRAINT DF_Accounts_Bal DEFAULT (0)
);
CREATE INDEX IX_Accounts_OpenedDate ON dbo.Accounts(OpenedDate);
CREATE INDEX IX_Accounts_Customer   ON dbo.Accounts(CustomerId);

CREATE TABLE dbo.Transactions (
    TransactionId BIGINT IDENTITY(1,1) CONSTRAINT PK_Transactions PRIMARY KEY,
    AccountId     INT           NOT NULL CONSTRAINT FK_Txn_Account REFERENCES dbo.Accounts(AccountId),
    TxnDate       DATETIME2(0)  NOT NULL,
    TxnType       VARCHAR(12)   NOT NULL CONSTRAINT CK_Txn_Type
                                CHECK (TxnType IN ('Deposit','Withdrawal','Profit','Charge','Transfer')),
    Amount        DECIMAL(18,2) NOT NULL,   -- signed: credits +, debits -
    Narration     NVARCHAR(200) NULL
);
CREATE INDEX IX_Txn_Account ON dbo.Transactions(AccountId, TxnDate);


-------------------------------------------------------------------------------------
-- 3) Seed: Branches
-------------------------------------------------------------------------------------
SET IDENTITY_INSERT dbo.Branches ON;
INSERT dbo.Branches (BranchId, BranchCode, BranchName, City) VALUES
(1,'0101','Motijheel Branch','Dhaka'),
(2,'0102','Gulshan Branch','Dhaka'),
(3,'0103','Dhanmondi Branch','Dhaka'),
(4,'0104','Uttara Branch','Dhaka'),
(5,'0201','Agrabad Branch','Chattogram'),
(6,'0301','Zindabazar Branch','Sylhet');
SET IDENTITY_INSERT dbo.Branches OFF;

-------------------------------------------------------------------------------------
-- 4) Seed: Account types (Islamic products)
-------------------------------------------------------------------------------------
SET IDENTITY_INSERT dbo.AccountTypes ON;
INSERT dbo.AccountTypes (AccountTypeId, TypeCode, TypeName, IsIslamic, ProfitRate) VALUES
(1,'AWCA','Al-Wadiah Current Account',      1, NULL),
(2,'MSA' ,'Mudaraba Savings Account',       1, 4.50),
(3,'MSND','Mudaraba Short Notice Deposit',  1, 3.00),
(4,'MTDR','Mudaraba Term Deposit Receipt',  1, 7.25),
(5,'SMSA','Student Mudaraba Savings',       1, 4.00);
SET IDENTITY_INSERT dbo.AccountTypes OFF;

-------------------------------------------------------------------------------------
-- 5) Seed: Customers
-------------------------------------------------------------------------------------
SET IDENTITY_INSERT dbo.Customers ON;
INSERT dbo.Customers (CustomerId, FullName, NidNumber, MobileNo, Email, District, CreatedDate) VALUES
(1 ,N'Abdul Karim Chowdhury','1990234567','+8801711000001',N'akarim@example.com'  ,N'Dhaka'     , DATEADD(DAY,-1210, CAST(GETDATE() AS date))),
(2 ,N'Nasrin Akter'         ,'1985456712','+8801712000002',NULL                   ,N'Dhaka'     , DATEADD(DAY, -910, CAST(GETDATE() AS date))),
(3 ,N'Md. Rafiqul Islam'    ,'1978112233','+8801713000003',N'rafiqul@example.com' ,N'Dhaka'     , DATEADD(DAY, -810, CAST(GETDATE() AS date))),
(4 ,N'Farhana Yasmin'       ,'1992556677','+8801714000004',NULL                   ,N'Dhaka'     , DATEADD(DAY, -740, CAST(GETDATE() AS date))),
(5 ,N'Tanvir Ahmed'         ,'1988334455','+8801715000005',N'tanvir@example.com'  ,N'Dhaka'     , DATEADD(DAY, -660, CAST(GETDATE() AS date))),
(6 ,N'Sultana Razia'        ,'1975998877','+8801716000006',NULL                   ,N'Dhaka'     , DATEADD(DAY, -550, CAST(GETDATE() AS date))),
(7 ,N'Mohammad Ali Hossain' ,'2001445566','+8801717000007',NULL                   ,N'Dhaka'     , DATEADD(DAY, -510, CAST(GETDATE() AS date))),
(8 ,N'Shirin Sultana'       ,'1983221144','+8801718000008',N'shirin@example.com'  ,N'Dhaka'     , DATEADD(DAY, -430, CAST(GETDATE() AS date))),
(9 ,N'Kamrul Hasan'         ,'1980778899','+8801719000009',NULL                   ,N'Chattogram', DATEADD(DAY, -375, CAST(GETDATE() AS date))),
(10,N'Ayesha Siddika'       ,'1995662211','+8801811000010',N'ayesha@example.com'  ,N'Chattogram', DATEADD(DAY, -310, CAST(GETDATE() AS date))),
(11,N'Jahangir Alam'        ,'1972113355','+8801812000011',NULL                   ,N'Dhaka'     , DATEADD(DAY, -260, CAST(GETDATE() AS date))),
(12,N'Nusrat Jahan'         ,'1998447722','+8801813000012',N'nusrat@example.com'  ,N'Dhaka'     , DATEADD(DAY, -210, CAST(GETDATE() AS date))),
(13,N'Mizanur Rahman'       ,'1969556644','+8801814000013',NULL                   ,N'Dhaka'     , DATEADD(DAY, -170, CAST(GETDATE() AS date))),
(14,N'Rehana Parvin'        ,'1987330099','+8801815000014',NULL                   ,N'Sylhet'    , DATEADD(DAY, -130, CAST(GETDATE() AS date))),
(15,N'Shahidul Islam'       ,'2002885511','+8801816000015',N'shahid@example.com'  ,N'Dhaka'     , DATEADD(DAY, -105, CAST(GETDATE() AS date))),
(16,N'Taslima Begum'        ,'1979220066','+8801817000016',NULL                   ,N'Dhaka'     , DATEADD(DAY,  -70, CAST(GETDATE() AS date))),
(17,N'Arif Mahmud'          ,'1990774433','+8801818000017',N'arif@example.com'    ,N'Dhaka'     , DATEADD(DAY,  -55, CAST(GETDATE() AS date))),
(18,N'Fatema Khatun'        ,'1993668822','+8801819000018',NULL                   ,N'Dhaka'     , DATEADD(DAY,  -35, CAST(GETDATE() AS date))),
(19,N'Habibur Rahman'       ,'1984551199','+8801911000019',NULL                   ,N'Chattogram', DATEADD(DAY,  -30, CAST(GETDATE() AS date))),
(20,N'Sadia Islam'          ,'1996443377','+8801912000020',N'sadia@example.com'   ,N'Dhaka'     , DATEADD(DAY,  -25, CAST(GETDATE() AS date)));
SET IDENTITY_INSERT dbo.Customers OFF;

-------------------------------------------------------------------------------------
-- 6) Seed: Accounts
--    OpenedDate offsets are chosen so exactly 6 accounts fall within the last 30 days
--    (AccountIds 18-23). AccountId 24 is a Closed account that nets to zero.
-------------------------------------------------------------------------------------
SET IDENTITY_INSERT dbo.Accounts ON;
INSERT dbo.Accounts (AccountId, AccountNo, CustomerId, BranchId, AccountTypeId, OpenedDate, Status) VALUES
(1 ,'0101000010001', 1 ,1 ,2 , DATEADD(DAY,-1200, CAST(GETDATE() AS date)),'Active'),
(2 ,'0101000010002', 2 ,1 ,1 , DATEADD(DAY, -900, CAST(GETDATE() AS date)),'Active'),
(3 ,'0102000010003', 3 ,2 ,2 , DATEADD(DAY, -800, CAST(GETDATE() AS date)),'Active'),
(4 ,'0102000010004', 4 ,2 ,4 , DATEADD(DAY, -730, CAST(GETDATE() AS date)),'Active'),
(5 ,'0103000010005', 5 ,3 ,2 , DATEADD(DAY, -650, CAST(GETDATE() AS date)),'Active'),
(6 ,'0103000010006', 6 ,3 ,1 , DATEADD(DAY, -540, CAST(GETDATE() AS date)),'Dormant'),
(7 ,'0104000010007', 7 ,4 ,5 , DATEADD(DAY, -500, CAST(GETDATE() AS date)),'Active'),
(8 ,'0104000010008', 8 ,4 ,2 , DATEADD(DAY, -420, CAST(GETDATE() AS date)),'Active'),
(9 ,'0201000010009', 9 ,5 ,3 , DATEADD(DAY, -365, CAST(GETDATE() AS date)),'Active'),
(10,'0201000010010',10 ,5 ,2 , DATEADD(DAY, -300, CAST(GETDATE() AS date)),'Active'),
(11,'0101000010011',11 ,1 ,1 , DATEADD(DAY, -250, CAST(GETDATE() AS date)),'Active'),
(12,'0102000010012',12 ,2 ,2 , DATEADD(DAY, -200, CAST(GETDATE() AS date)),'Active'),
(13,'0103000010013',13 ,3 ,4 , DATEADD(DAY, -160, CAST(GETDATE() AS date)),'Active'),
(14,'0301000010014',14 ,6 ,2 , DATEADD(DAY, -120, CAST(GETDATE() AS date)),'Active'),
(15,'0104000010015',15 ,4 ,5 , DATEADD(DAY,  -95, CAST(GETDATE() AS date)),'Active'),
(16,'0101000010016',16 ,1 ,2 , DATEADD(DAY,  -60, CAST(GETDATE() AS date)),'Active'),
(17,'0102000010017',17 ,2 ,1 , DATEADD(DAY,  -45, CAST(GETDATE() AS date)),'Dormant'),
(18,'0103000010018',18 ,3 ,2 , DATEADD(DAY,  -28, CAST(GETDATE() AS date)),'Active'),
(19,'0201000010019',19 ,5 ,2 , DATEADD(DAY,  -22, CAST(GETDATE() AS date)),'Active'),
(20,'0104000010020',20 ,4 ,4 , DATEADD(DAY,  -15, CAST(GETDATE() AS date)),'Active'),
(21,'0101000010021', 1 ,1 ,3 , DATEADD(DAY,   -9, CAST(GETDATE() AS date)),'Active'),
(22,'0102000010022', 5 ,2 ,5 , DATEADD(DAY,   -4, CAST(GETDATE() AS date)),'Active'),
(23,'0103000010023',10 ,3 ,1 , DATEADD(DAY,   -2, CAST(GETDATE() AS date)),'Active'),
(24,'0104000010024', 3 ,4 ,2 , DATEADD(DAY, -350, CAST(GETDATE() AS date)),'Closed');
SET IDENTITY_INSERT dbo.Accounts OFF;

-------------------------------------------------------------------------------------
-- 7) Seed: Transactions (the ledger). Credits are +, debits are -.
--    Every account starts with an opening deposit; several have realistic activity.
-------------------------------------------------------------------------------------
INSERT dbo.Transactions (AccountId, TxnDate, TxnType, Amount, Narration) VALUES
-- A/C 1  (MSA, salaried)
(1 , DATEADD(DAY,-1200,GETDATE()),'Deposit'   ,  25000.00, N'Account opening deposit'),
(1 , DATEADD(DAY,  -90,GETDATE()),'Deposit'   ,  45000.00, N'Salary credit'),
(1 , DATEADD(DAY,  -85,GETDATE()),'Withdrawal', -20000.00, N'ATM withdrawal'),
(1 , DATEADD(DAY,  -55,GETDATE()),'Withdrawal',  -3200.00, N'DESCO electricity bill'),
(1 , DATEADD(DAY,  -30,GETDATE()),'Deposit'   ,  45000.00, N'Salary credit'),
(1 , DATEADD(DAY,   -1,GETDATE()),'Profit'    ,    560.00, N'Quarterly Mudaraba profit'),
-- A/C 2  (AWCA, business current)
(2 , DATEADD(DAY, -900,GETDATE()),'Deposit'   , 150000.00, N'Account opening deposit'),
(2 , DATEADD(DAY, -120,GETDATE()),'Deposit'   ,  80000.00, N'Sales collection'),
(2 , DATEADD(DAY, -100,GETDATE()),'Withdrawal', -50000.00, N'Supplier payment'),
(2 , DATEADD(DAY,  -90,GETDATE()),'Charge'    ,   -575.00, N'Half-yearly service charge'),
-- A/C 3  (MSA)
(3 , DATEADD(DAY, -800,GETDATE()),'Deposit'   ,  30000.00, N'Account opening deposit'),
(3 , DATEADD(DAY, -200,GETDATE()),'Deposit'   ,  12000.00, N'Cash deposit'),
(3 , DATEADD(DAY,  -95,GETDATE()),'Profit'    ,    410.00, N'Quarterly Mudaraba profit'),
-- A/C 4  (MTDR, term)
(4 , DATEADD(DAY, -730,GETDATE()),'Deposit'   , 500000.00, N'Term deposit placement'),
(4 , DATEADD(DAY, -365,GETDATE()),'Profit'    ,  18125.00, N'Annual Mudaraba profit'),
-- A/C 5  (MSA)
(5 , DATEADD(DAY, -650,GETDATE()),'Deposit'   ,  18000.00, N'Account opening deposit'),
(5 , DATEADD(DAY, -300,GETDATE()),'Deposit'   ,  22000.00, N'Cash deposit'),
(5 , DATEADD(DAY, -120,GETDATE()),'Withdrawal',  -5000.00, N'ATM withdrawal'),
-- A/C 6  (AWCA, dormant)
(6 , DATEADD(DAY, -540,GETDATE()),'Deposit'   ,  40000.00, N'Account opening deposit'),
(6 , DATEADD(DAY, -400,GETDATE()),'Withdrawal', -35000.00, N'Cheque payment'),
-- A/C 7  (SMSA, student)
(7 , DATEADD(DAY, -500,GETDATE()),'Deposit'   ,   1000.00, N'Account opening deposit'),
(7 , DATEADD(DAY, -200,GETDATE()),'Deposit'   ,    500.00, N'Cash deposit'),
(7 , DATEADD(DAY,  -60,GETDATE()),'Deposit'   ,    500.00, N'Cash deposit'),
-- A/C 8  (MSA, salaried)
(8 , DATEADD(DAY, -420,GETDATE()),'Deposit'   ,  35000.00, N'Account opening deposit'),
(8 , DATEADD(DAY, -100,GETDATE()),'Deposit'   ,  52000.00, N'Salary credit'),
(8 , DATEADD(DAY,  -80,GETDATE()),'Withdrawal', -15000.00, N'ATM withdrawal'),
(8 , DATEADD(DAY,  -10,GETDATE()),'Profit'    ,    300.00, N'Quarterly Mudaraba profit'),
-- A/C 9  (MSND)
(9 , DATEADD(DAY, -365,GETDATE()),'Deposit'   , 200000.00, N'Account opening deposit'),
(9 , DATEADD(DAY, -150,GETDATE()),'Withdrawal', -50000.00, N'Fund transfer out'),
(9 , DATEADD(DAY,  -40,GETDATE()),'Deposit'   , 100000.00, N'Cash deposit'),
-- A/C 10 (MSA)
(10, DATEADD(DAY, -300,GETDATE()),'Deposit'   ,  28000.00, N'Account opening deposit'),
(10, DATEADD(DAY, -120,GETDATE()),'Deposit'   ,   9000.00, N'Cash deposit'),
-- A/C 11 (AWCA)
(11, DATEADD(DAY, -250,GETDATE()),'Deposit'   ,  90000.00, N'Account opening deposit'),
(11, DATEADD(DAY,  -90,GETDATE()),'Deposit'   ,  45000.00, N'Sales collection'),
(11, DATEADD(DAY,  -70,GETDATE()),'Withdrawal', -30000.00, N'Supplier payment'),
-- A/C 12 (MSA)
(12, DATEADD(DAY, -200,GETDATE()),'Deposit'   ,  16000.00, N'Account opening deposit'),
(12, DATEADD(DAY,  -95,GETDATE()),'Profit'    ,    180.00, N'Quarterly Mudaraba profit'),
-- A/C 13 (MTDR, term)
(13, DATEADD(DAY, -160,GETDATE()),'Deposit'   ,1500000.00, N'Term deposit placement'),
(13, DATEADD(DAY,   -2,GETDATE()),'Profit'    ,  54375.00, N'Half-yearly Mudaraba profit'),
-- A/C 14 (MSA, salaried)
(14, DATEADD(DAY, -120,GETDATE()),'Deposit'   ,  42000.00, N'Account opening deposit'),
(14, DATEADD(DAY,  -30,GETDATE()),'Deposit'   ,  60000.00, N'Salary credit'),
(14, DATEADD(DAY,  -20,GETDATE()),'Withdrawal', -18000.00, N'ATM withdrawal'),
-- A/C 15 (SMSA, student)
(15, DATEADD(DAY,  -95,GETDATE()),'Deposit'   ,    800.00, N'Account opening deposit'),
(15, DATEADD(DAY,  -40,GETDATE()),'Deposit'   ,   1200.00, N'Cash deposit'),
-- A/C 16 (MSA)
(16, DATEADD(DAY,  -60,GETDATE()),'Deposit'   ,  50000.00, N'Account opening deposit'),
(16, DATEADD(DAY,  -20,GETDATE()),'Deposit'   ,  25000.00, N'Cash deposit'),
-- A/C 17 (AWCA, dormant)
(17, DATEADD(DAY,  -45,GETDATE()),'Deposit'   ,  20000.00, N'Account opening deposit'),
-- A/C 18 (MSA)   <-- opened within 30 days
(18, DATEADD(DAY,  -28,GETDATE()),'Deposit'   ,  40000.00, N'Account opening deposit'),
-- A/C 19 (MSA)   <-- opened within 30 days
(19, DATEADD(DAY,  -22,GETDATE()),'Deposit'   ,  15000.00, N'Account opening deposit'),
(19, DATEADD(DAY,  -10,GETDATE()),'Deposit'   ,  38000.00, N'Salary credit'),
-- A/C 20 (MTDR)  <-- opened within 30 days
(20, DATEADD(DAY,  -15,GETDATE()),'Deposit'   ,1000000.00, N'Term deposit placement'),
-- A/C 21 (MSND)  <-- opened within 30 days
(21, DATEADD(DAY,   -9,GETDATE()),'Deposit'   , 250000.00, N'Account opening deposit'),
-- A/C 22 (SMSA)  <-- opened within 30 days
(22, DATEADD(DAY,   -4,GETDATE()),'Deposit'   ,   2000.00, N'Account opening deposit'),
-- A/C 23 (AWCA)  <-- opened within 30 days
(23, DATEADD(DAY,   -2,GETDATE()),'Deposit'   , 120000.00, N'Account opening deposit'),
-- A/C 24 (MSA, closed - nets to zero)
(24, DATEADD(DAY, -350,GETDATE()),'Deposit'   ,  30000.00, N'Account opening deposit'),
(24, DATEADD(DAY,   -5,GETDATE()),'Withdrawal', -30000.00, N'Account closure - balance withdrawn');


-------------------------------------------------------------------------------------
-- 8) Derive balances from the ledger (single source of truth)
-------------------------------------------------------------------------------------
UPDATE a
SET    a.Balance = t.Bal
FROM   dbo.Accounts a
JOIN  (SELECT AccountId, SUM(Amount) AS Bal
       FROM   dbo.Transactions
       GROUP  BY AccountId) t ON t.AccountId = a.AccountId;


-------------------------------------------------------------------------------------
-- 9) Sanity checks (what the agent's demo question should return)
-------------------------------------------------------------------------------------
PRINT '--- Accounts opened in the last 30 days ---';
SELECT COUNT(*)      AS AccountsOpenedLast30Days,
       SUM(Balance)  AS TotalBalanceBDT
FROM   dbo.Accounts
WHERE  OpenedDate >= DATEADD(DAY, -30, CAST(GETDATE() AS date));   -- expect 6 rows

PRINT '--- Portfolio by product ---';
SELECT at.TypeName,
       COUNT(*)                 AS NumAccounts,
       SUM(a.Balance)           AS TotalBalanceBDT
FROM   dbo.Accounts a
JOIN   dbo.AccountTypes at ON at.AccountTypeId = a.AccountTypeId
GROUP  BY at.TypeName
ORDER  BY TotalBalanceBDT DESC;

PRINT '--- Ledger vs stored balance reconciliation (should be zero rows) ---';
SELECT a.AccountNo, a.Balance AS StoredBalance, SUM(t.Amount) AS LedgerBalance
FROM   dbo.Accounts a
JOIN   dbo.Transactions t ON t.AccountId = a.AccountId
GROUP  BY a.AccountNo, a.Balance
HAVING a.Balance <> SUM(t.Amount);

