# 📅 Timetable Management System

> Built using Oracle SQL & PL/SQL

![SQL](https://img.shields.io/badge/SQL-Oracle-blue)
![PL/SQL](https://img.shields.io/badge/PL%2FSQL-Procedures%20%26%20Triggers-orange)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## 📌 About
A fully-featured database-driven system to manage 
departments, teachers, subjects, classrooms, students 
and attendance — with automatic clash detection, 
workload analysis and attendance tracking.

---

## 🗃️ Database Overview

| Feature | Details |
|---|---|
| Tables | 10 interrelated tables |
| Constraints | PK, FK, UNIQUE, CHECK |
| Sequences | 11 auto-increment sequences |
| Indexes | 10 query optimization indexes |
| Views | 4 views + 3 synonyms |
| Triggers | 5 triggers |
| Procedures | 3 stored procedures |
| Functions | 3 functions |
| Cursors | 4 explicit cursors |
| Package | 1 full PL/SQL package |
| PL/SQL Blocks | 4 blocks with exception handling |
| Transactions | 4 transactions with savepoints |

---

## 📁 File Structure
```
sql/
├── 01_create_tables.sql   → All 10 table definitions
├── 02_constraints.sql     → All constraints and keys
├── 03_sequences.sql       → 11 auto-increment sequences
├── 04_insert_data.sql     → Realistic sample data
├── 05_queries.sql         → 10 advanced SQL queries
├── 06_views.sql           → 4 views and 3 synonyms
├── 07_indexes.sql         → 10 indexes for optimization
├── 08_triggers.sql        → 5 triggers including clash detection
├── 09_procedures.sql      → 3 procedures and 3 functions
├── 10_cursors.sql         → 4 explicit cursors
├── 11_plsql_blocks.sql    → 4 PL/SQL blocks with exceptions
├── 12_package.sql         → Full PL/SQL package
└── 13_transactions.sql    → 4 transactions with savepoints
```

---

## ⭐ Key Features

- **Clash Detection** — Triggers automatically prevent
  teacher and room scheduling conflicts
- **Attendance Tracking** — Marks and calculates 
  attendance percentage per student
- **Detention List** — Auto-generates list of students
  below 75% attendance
- **Audit Log** — Records every timetable change
  with user and timestamp
- **Holiday Block** — Prevents attendance marking
  on holidays
- **Workload Analysis** — Shows periods per week
  for every teacher

---

## ▶️ How to Run

1. Open Oracle SQL Developer or MySQL Workbench
2. Run files **in order** from `01` to `13`
3. Enable DBMS Output to see PL/SQL results
4. All scripts are self-contained

---

## 🗂️ Tables

| Table | Description |
|---|---|
| Department | Stores department details |
| Teachers | Stores teacher information |
| Subjects | Stores subject details |
| Classrooms | Stores room details |
| Time_Slots | Stores day and time periods |
| Timetable | Main scheduling table |
| Students | Stores student records |
| Attendance | Tracks daily attendance |
| Teacher_Subject | Maps teachers to subjects |
| Holidays | Stores holiday calendar |

---



