/* =====================================================================
   BankDemo — schema + seed for MySQL 8.0+ (DBeaver-ready)
   Balances are DERIVED from Transactions (single source of truth).
   Dates are relative to today, so "last 30 days" always returns rows.
   ===================================================================== */

CREATE DATABASE IF NOT EXISTS BankDemo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE BankDemo;

-- 1) Drop in dependency order (re-runnable)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Transactions;
DROP TABLE IF EXISTS Accounts;
DROP TABLE IF EXISTS AccountTypes;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Branches;
SET FOREIGN_KEY_CHECKS = 1;

-- 2) Schema
CREATE TABLE Branches (
  BranchId   INT AUTO_INCREMENT PRIMARY KEY,
  BranchCode CHAR(4)     NOT NULL UNIQUE,
  BranchName VARCHAR(80) NOT NULL,
  City       VARCHAR(40) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Customers (
  CustomerId  INT AUTO_INCREMENT PRIMARY KEY,
  FullName    VARCHAR(100) NOT NULL,
  NidNumber   VARCHAR(17)  NOT NULL UNIQUE,
  MobileNo    VARCHAR(20)  NOT NULL,
  Email       VARCHAR(120) NULL,
  District    VARCHAR(40)  NOT NULL,
  CreatedDate DATE NOT NULL DEFAULT (CURRENT_DATE)   -- needs MySQL 8.0.13+
) ENGINE=InnoDB;

CREATE TABLE AccountTypes (
  AccountTypeId INT AUTO_INCREMENT PRIMARY KEY,
  TypeCode      VARCHAR(8)   NOT NULL UNIQUE,
  TypeName      VARCHAR(60)  NOT NULL,
  IsIslamic     TINYINT      NOT NULL DEFAULT 1,
  ProfitRate    DECIMAL(5,2) NULL
) ENGINE=InnoDB;

CREATE TABLE Accounts (
  AccountId     INT AUTO_INCREMENT PRIMARY KEY,
  AccountNo     VARCHAR(16) NOT NULL UNIQUE,
  CustomerId    INT NOT NULL,
  BranchId      INT NOT NULL,
  AccountTypeId INT NOT NULL,
  OpenedDate    DATE NOT NULL,
  Status        VARCHAR(10) NOT NULL,
  Currency      CHAR(3) NOT NULL DEFAULT 'BDT',
  Balance       DECIMAL(18,2) NOT NULL DEFAULT 0,
  CONSTRAINT FK_Accounts_Customer FOREIGN KEY (CustomerId)    REFERENCES Customers(CustomerId),
  CONSTRAINT FK_Accounts_Branch   FOREIGN KEY (BranchId)      REFERENCES Branches(BranchId),
  CONSTRAINT FK_Accounts_Type     FOREIGN KEY (AccountTypeId) REFERENCES AccountTypes(AccountTypeId),
  CONSTRAINT CK_Accounts_Status   CHECK (Status IN ('Active','Dormant','Closed'))
) ENGINE=InnoDB;

CREATE INDEX IX_Accounts_OpenedDate ON Accounts(OpenedDate);
CREATE INDEX IX_Accounts_Customer   ON Accounts(CustomerId);

CREATE TABLE Transactions (
  TransactionId BIGINT AUTO_INCREMENT PRIMARY KEY,
  AccountId     INT NOT NULL,
  TxnDate       DATETIME NOT NULL,
  TxnType       VARCHAR(12) NOT NULL,
  Amount        DECIMAL(18,2) NOT NULL,   -- signed: credits +, debits -
  Narration     VARCHAR(200) NULL,
  CONSTRAINT FK_Txn_Account FOREIGN KEY (AccountId) REFERENCES Accounts(AccountId),
  CONSTRAINT CK_Txn_Type    CHECK (TxnType IN ('Deposit','Withdrawal','Profit','Charge','Transfer'))
) ENGINE=InnoDB;

CREATE INDEX IX_Txn_Account ON Transactions(AccountId, TxnDate);

-- 3) Seed: Branches
INSERT INTO Branches (BranchId, BranchCode, BranchName, City) VALUES
(1,'0101','Motijheel Branch','Dhaka'),
(2,'0102','Gulshan Branch','Dhaka'),
(3,'0103','Dhanmondi Branch','Dhaka'),
(4,'0104','Uttara Branch','Dhaka'),
(5,'0201','Agrabad Branch','Chattogram'),
(6,'0301','Zindabazar Branch','Sylhet');

-- 4) Seed: Account types (Islamic products)
INSERT INTO AccountTypes (AccountTypeId, TypeCode, TypeName, IsIslamic, ProfitRate) VALUES
(1,'AWCA','Al-Wadiah Current Account',     1, NULL),
(2,'MSA' ,'Mudaraba Savings Account',      1, 4.50),
(3,'MSND','Mudaraba Short Notice Deposit', 1, 3.00),
(4,'MTDR','Mudaraba Term Deposit Receipt', 1, 7.25),
(5,'SMSA','Student Mudaraba Savings',      1, 4.00);

-- 5) Seed: Customers
INSERT INTO Customers (CustomerId, FullName, NidNumber, MobileNo, Email, District, CreatedDate) VALUES
(1 ,'Abdul Karim Chowdhury','1990234567','+8801711000001','akarim@example.com' ,'Dhaka'     , CURDATE() - INTERVAL 1210 DAY),
(2 ,'Nasrin Akter'         ,'1985456712','+8801712000002',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL  910 DAY),
(3 ,'Md. Rafiqul Islam'    ,'1978112233','+8801713000003','rafiqul@example.com','Dhaka'     , CURDATE() - INTERVAL  810 DAY),
(4 ,'Farhana Yasmin'       ,'1992556677','+8801714000004',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL  740 DAY),
(5 ,'Tanvir Ahmed'         ,'1988334455','+8801715000005','tanvir@example.com' ,'Dhaka'     , CURDATE() - INTERVAL  660 DAY),
(6 ,'Sultana Razia'        ,'1975998877','+8801716000006',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL  550 DAY),
(7 ,'Mohammad Ali Hossain' ,'2001445566','+8801717000007',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL  510 DAY),
(8 ,'Shirin Sultana'       ,'1983221144','+8801718000008','shirin@example.com' ,'Dhaka'     , CURDATE() - INTERVAL  430 DAY),
(9 ,'Kamrul Hasan'         ,'1980778899','+8801719000009',NULL                 ,'Chattogram', CURDATE() - INTERVAL  375 DAY),
(10,'Ayesha Siddika'       ,'1995662211','+8801811000010','ayesha@example.com' ,'Chattogram', CURDATE() - INTERVAL  310 DAY),
(11,'Jahangir Alam'        ,'1972113355','+8801812000011',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL  260 DAY),
(12,'Nusrat Jahan'         ,'1998447722','+8801813000012','nusrat@example.com' ,'Dhaka'     , CURDATE() - INTERVAL  210 DAY),
(13,'Mizanur Rahman'       ,'1969556644','+8801814000013',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL  170 DAY),
(14,'Rehana Parvin'        ,'1987330099','+8801815000014',NULL                 ,'Sylhet'    , CURDATE() - INTERVAL  130 DAY),
(15,'Shahidul Islam'       ,'2002885511','+8801816000015','shahid@example.com' ,'Dhaka'     , CURDATE() - INTERVAL  105 DAY),
(16,'Taslima Begum'        ,'1979220066','+8801817000016',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL   70 DAY),
(17,'Arif Mahmud'          ,'1990774433','+8801818000017','arif@example.com'   ,'Dhaka'     , CURDATE() - INTERVAL   55 DAY),
(18,'Fatema Khatun'        ,'1993668822','+8801819000018',NULL                 ,'Dhaka'     , CURDATE() - INTERVAL   35 DAY),
(19,'Habibur Rahman'       ,'1984551199','+8801911000019',NULL                 ,'Chattogram', CURDATE() - INTERVAL   30 DAY),
(20,'Sadia Islam'          ,'1996443377','+8801912000020','sadia@example.com'  ,'Dhaka'     , CURDATE() - INTERVAL   25 DAY);

-- 6) Seed: Accounts
--    AccountIds 18-23 fall within the last 30 days. AccountId 24 is Closed, nets to zero.
INSERT INTO Accounts (AccountId, AccountNo, CustomerId, BranchId, AccountTypeId, OpenedDate, Status) VALUES
(1 ,'0101000010001', 1 ,1 ,2 , CURDATE() - INTERVAL 1200 DAY,'Active'),
(2 ,'0101000010002', 2 ,1 ,1 , CURDATE() - INTERVAL  900 DAY,'Active'),
(3 ,'0102000010003', 3 ,2 ,2 , CURDATE() - INTERVAL  800 DAY,'Active'),
(4 ,'0102000010004', 4 ,2 ,4 , CURDATE() - INTERVAL  730 DAY,'Active'),
(5 ,'0103000010005', 5 ,3 ,2 , CURDATE() - INTERVAL  650 DAY,'Active'),
(6 ,'0103000010006', 6 ,3 ,1 , CURDATE() - INTERVAL  540 DAY,'Dormant'),
(7 ,'0104000010007', 7 ,4 ,5 , CURDATE() - INTERVAL  500 DAY,'Active'),
(8 ,'0104000010008', 8 ,4 ,2 , CURDATE() - INTERVAL  420 DAY,'Active'),
(9 ,'0201000010009', 9 ,5 ,3 , CURDATE() - INTERVAL  365 DAY,'Active'),
(10,'0201000010010',10 ,5 ,2 , CURDATE() - INTERVAL  300 DAY,'Active'),
(11,'0101000010011',11 ,1 ,1 , CURDATE() - INTERVAL  250 DAY,'Active'),
(12,'0102000010012',12 ,2 ,2 , CURDATE() - INTERVAL  200 DAY,'Active'),
(13,'0103000010013',13 ,3 ,4 , CURDATE() - INTERVAL  160 DAY,'Active'),
(14,'0301000010014',14 ,6 ,2 , CURDATE() - INTERVAL  120 DAY,'Active'),
(15,'0104000010015',15 ,4 ,5 , CURDATE() - INTERVAL   95 DAY,'Active'),
(16,'0101000010016',16 ,1 ,2 , CURDATE() - INTERVAL   60 DAY,'Active'),
(17,'0102000010017',17 ,2 ,1 , CURDATE() - INTERVAL   45 DAY,'Dormant'),
(18,'0103000010018',18 ,3 ,2 , CURDATE() - INTERVAL   28 DAY,'Active'),
(19,'0201000010019',19 ,5 ,2 , CURDATE() - INTERVAL   22 DAY,'Active'),
(20,'0104000010020',20 ,4 ,4 , CURDATE() - INTERVAL   15 DAY,'Active'),
(21,'0101000010021', 1 ,1 ,3 , CURDATE() - INTERVAL    9 DAY,'Active'),
(22,'0102000010022', 5 ,2 ,5 , CURDATE() - INTERVAL    4 DAY,'Active'),
(23,'0103000010023',10 ,3 ,1 , CURDATE() - INTERVAL    2 DAY,'Active'),
(24,'0104000010024', 3 ,4 ,2 , CURDATE() - INTERVAL  350 DAY,'Closed');

-- 7) Seed: Transactions (the ledger). Credits +, debits -.
INSERT INTO Transactions (AccountId, TxnDate, TxnType, Amount, Narration) VALUES
-- A/C 1  (MSA, salaried)
(1 , NOW() - INTERVAL 1200 DAY,'Deposit'   ,  25000.00,'Account opening deposit'),
(1 , NOW() - INTERVAL   90 DAY,'Deposit'   ,  45000.00,'Salary credit'),
(1 , NOW() - INTERVAL   85 DAY,'Withdrawal', -20000.00,'ATM withdrawal'),
(1 , NOW() - INTERVAL   55 DAY,'Withdrawal',  -3200.00,'DESCO electricity bill'),
(1 , NOW() - INTERVAL   30 DAY,'Deposit'   ,  45000.00,'Salary credit'),
(1 , NOW() - INTERVAL    1 DAY,'Profit'    ,    560.00,'Quarterly Mudaraba profit'),
-- A/C 2  (AWCA, business current)
(2 , NOW() - INTERVAL  900 DAY,'Deposit'   , 150000.00,'Account opening deposit'),
(2 , NOW() - INTERVAL  120 DAY,'Deposit'   ,  80000.00,'Sales collection'),
(2 , NOW() - INTERVAL  100 DAY,'Withdrawal', -50000.00,'Supplier payment'),
(2 , NOW() - INTERVAL   90 DAY,'Charge'    ,   -575.00,'Half-yearly service charge'),
-- A/C 3  (MSA)
(3 , NOW() - INTERVAL  800 DAY,'Deposit'   ,  30000.00,'Account opening deposit'),
(3 , NOW() - INTERVAL  200 DAY,'Deposit'   ,  12000.00,'Cash deposit'),
(3 , NOW() - INTERVAL   95 DAY,'Profit'    ,    410.00,'Quarterly Mudaraba profit'),
-- A/C 4  (MTDR, term)
(4 , NOW() - INTERVAL  730 DAY,'Deposit'   , 500000.00,'Term deposit placement'),
(4 , NOW() - INTERVAL  365 DAY,'Profit'    ,  18125.00,'Annual Mudaraba profit'),
-- A/C 5  (MSA)
(5 , NOW() - INTERVAL  650 DAY,'Deposit'   ,  18000.00,'Account opening deposit'),
(5 , NOW() - INTERVAL  300 DAY,'Deposit'   ,  22000.00,'Cash deposit'),
(5 , NOW() - INTERVAL  120 DAY,'Withdrawal',  -5000.00,'ATM withdrawal'),
-- A/C 6  (AWCA, dormant)
(6 , NOW() - INTERVAL  540 DAY,'Deposit'   ,  40000.00,'Account opening deposit'),
(6 , NOW() - INTERVAL  400 DAY,'Withdrawal', -35000.00,'Cheque payment'),
-- A/C 7  (SMSA, student)
(7 , NOW() - INTERVAL  500 DAY,'Deposit'   ,   1000.00,'Account opening deposit'),
(7 , NOW() - INTERVAL  200 DAY,'Deposit'   ,    500.00,'Cash deposit'),
(7 , NOW() - INTERVAL   60 DAY,'Deposit'   ,    500.00,'Cash deposit'),
-- A/C 8  (MSA, salaried)
(8 , NOW() - INTERVAL  420 DAY,'Deposit'   ,  35000.00,'Account opening deposit'),
(8 , NOW() - INTERVAL  100 DAY,'Deposit'   ,  52000.00,'Salary credit'),
(8 , NOW() - INTERVAL   80 DAY,'Withdrawal', -15000.00,'ATM withdrawal'),
(8 , NOW() - INTERVAL   10 DAY,'Profit'    ,    300.00,'Quarterly Mudaraba profit'),
-- A/C 9  (MSND)
(9 , NOW() - INTERVAL  365 DAY,'Deposit'   , 200000.00,'Account opening deposit'),
(9 , NOW() - INTERVAL  150 DAY,'Withdrawal', -50000.00,'Fund transfer out'),
(9 , NOW() - INTERVAL   40 DAY,'Deposit'   , 100000.00,'Cash deposit'),
-- A/C 10 (MSA)
(10, NOW() - INTERVAL  300 DAY,'Deposit'   ,  28000.00,'Account opening deposit'),
(10, NOW() - INTERVAL  120 DAY,'Deposit'   ,   9000.00,'Cash deposit'),
-- A/C 11 (AWCA)
(11, NOW() - INTERVAL  250 DAY,'Deposit'   ,  90000.00,'Account opening deposit'),
(11, NOW() - INTERVAL   90 DAY,'Deposit'   ,  45000.00,'Sales collection'),
(11, NOW() - INTERVAL   70 DAY,'Withdrawal', -30000.00,'Supplier payment'),
-- A/C 12 (MSA)
(12, NOW() - INTERVAL  200 DAY,'Deposit'   ,  16000.00,'Account opening deposit'),
(12, NOW() - INTERVAL   95 DAY,'Profit'    ,    180.00,'Quarterly Mudaraba profit'),
-- A/C 13 (MTDR, term)
(13, NOW() - INTERVAL  160 DAY,'Deposit'   ,1500000.00,'Term deposit placement'),
(13, NOW() - INTERVAL    2 DAY,'Profit'    ,  54375.00,'Half-yearly Mudaraba profit'),
-- A/C 14 (MSA, salaried)
(14, NOW() - INTERVAL  120 DAY,'Deposit'   ,  42000.00,'Account opening deposit'),
(14, NOW() - INTERVAL   30 DAY,'Deposit'   ,  60000.00,'Salary credit'),
(14, NOW() - INTERVAL   20 DAY,'Withdrawal', -18000.00,'ATM withdrawal'),
-- A/C 15 (SMSA, student)
(15, NOW() - INTERVAL   95 DAY,'Deposit'   ,    800.00,'Account opening deposit'),
(15, NOW() - INTERVAL   40 DAY,'Deposit'   ,   1200.00,'Cash deposit'),
-- A/C 16 (MSA)
(16, NOW() - INTERVAL   60 DAY,'Deposit'   ,  50000.00,'Account opening deposit'),
(16, NOW() - INTERVAL   20 DAY,'Deposit'   ,  25000.00,'Cash deposit'),
-- A/C 17 (AWCA, dormant)
(17, NOW() - INTERVAL   45 DAY,'Deposit'   ,  20000.00,'Account opening deposit'),
-- A/C 18 (MSA)  <-- opened within 30 days
(18, NOW() - INTERVAL   28 DAY,'Deposit'   ,  40000.00,'Account opening deposit'),
-- A/C 19 (MSA)  <-- opened within 30 days
(19, NOW() - INTERVAL   22 DAY,'Deposit'   ,  15000.00,'Account opening deposit'),
(19, NOW() - INTERVAL   10 DAY,'Deposit'   ,  38000.00,'Salary credit'),
-- A/C 20 (MTDR) <-- opened within 30 days
(20, NOW() - INTERVAL   15 DAY,'Deposit'   ,1000000.00,'Term deposit placement'),
-- A/C 21 (MSND) <-- opened within 30 days
(21, NOW() - INTERVAL    9 DAY,'Deposit'   , 250000.00,'Account opening deposit'),
-- A/C 22 (SMSA) <-- opened within 30 days
(22, NOW() - INTERVAL    4 DAY,'Deposit'   ,   2000.00,'Account opening deposit'),
-- A/C 23 (AWCA) <-- opened within 30 days
(23, NOW() - INTERVAL    2 DAY,'Deposit'   , 120000.00,'Account opening deposit'),
-- A/C 24 (MSA, closed - nets to zero)
(24, NOW() - INTERVAL  350 DAY,'Deposit'   ,  30000.00,'Account opening deposit'),
(24, NOW() - INTERVAL    5 DAY,'Withdrawal', -30000.00,'Account closure - balance withdrawn');

-- 8) Reset auto-increment counters past the seeded IDs (replaces SET IDENTITY_INSERT)
ALTER TABLE Branches     AUTO_INCREMENT = 7;
ALTER TABLE AccountTypes AUTO_INCREMENT = 6;
ALTER TABLE Customers    AUTO_INCREMENT = 21;
ALTER TABLE Accounts     AUTO_INCREMENT = 25;

-- 9) Derive balances from the ledger (single source of truth)
UPDATE Accounts a
JOIN (SELECT AccountId, SUM(Amount) AS Bal
      FROM Transactions
      GROUP BY AccountId) t ON t.AccountId = a.AccountId
SET a.Balance = t.Bal;

-- 10) Sanity checks
SELECT '--- Accounts opened in the last 30 days ---' AS info;
SELECT COUNT(*)     AS AccountsOpenedLast30Days,   -- expect 6
       SUM(Balance) AS TotalBalanceBDT             -- expect 1,465,000
FROM Accounts
WHERE OpenedDate >= CURDATE() - INTERVAL 30 DAY;

SELECT '--- Portfolio by product ---' AS info;
SELECT acty.TypeName,
       COUNT(*)          AS NumAccounts,
       SUM(a.Balance)    AS TotalBalanceBDT
FROM Accounts a
JOIN AccountTypes acty ON acty.AccountTypeId = a.AccountTypeId
GROUP BY acty.TypeName
ORDER BY TotalBalanceBDT DESC;

SELECT '--- Ledger vs stored balance reconciliation (should be zero rows) ---' AS info;
SELECT a.AccountNo, a.Balance AS StoredBalance, SUM(t.Amount) AS LedgerBalance
FROM Accounts a
JOIN Transactions t ON t.AccountId = a.AccountId
GROUP BY a.AccountNo, a.Balance
HAVING a.Balance <> SUM(t.Amount);

-- 11) Row count verification
SELECT 'Branches' AS tbl, COUNT(*) AS cnt FROM Branches
UNION ALL SELECT 'Customers',    COUNT(*) FROM Customers
UNION ALL SELECT 'AccountTypes', COUNT(*) FROM AccountTypes
UNION ALL SELECT 'Accounts',     COUNT(*) FROM Accounts
UNION ALL SELECT 'Transactions', COUNT(*) FROM Transactions;