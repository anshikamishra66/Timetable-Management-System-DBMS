-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 01: Create Tables
-- ============================================

-- 1. Department Table
CREATE TABLE Department (
    dept_id   NUMBER(5) PRIMARY KEY,
    dept_name VARCHAR2(100) NOT NULL,
    hod_name  VARCHAR2(100)
);

-- 2. Teachers Table
CREATE TABLE Teachers (
    teacher_id   NUMBER(5) PRIMARY KEY,
    teacher_name VARCHAR2(100) NOT NULL,
    dept_id      NUMBER(5),
    email        VARCHAR2(100),
    contact_no   VARCHAR2(15),
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
);

-- 3. Subjects Table
CREATE TABLE Subjects (
    subject_id   NUMBER(5) PRIMARY KEY,
    subject_name VARCHAR2(100) NOT NULL,
    subject_code VARCHAR2(20) UNIQUE,
    dept_id      NUMBER(5),
    credits      NUMBER(2),
    type         VARCHAR2(20),
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
);

-- 4. Classrooms Table
CREATE TABLE Classrooms (
    room_id   NUMBER(5) PRIMARY KEY,
    room_name VARCHAR2(50),
    capacity  NUMBER(5),
    room_type VARCHAR2(30)
);

-- 5. Time Slots Table
CREATE TABLE Time_Slots (
    slot_id    NUMBER(5) PRIMARY KEY,
    day_name   VARCHAR2(20),
    start_time VARCHAR2(10),
    end_time   VARCHAR2(10),
    period_no  NUMBER(2)
);

-- 6. Timetable Table (Main Table)
CREATE TABLE Timetable (
    timetable_id  NUMBER(5) PRIMARY KEY,
    dept_id       NUMBER(5),
    teacher_id    NUMBER(5),
    subject_id    NUMBER(5),
    room_id       NUMBER(5),
    slot_id       NUMBER(5),
    semester      NUMBER(2),
    section       VARCHAR2(5),
    academic_year VARCHAR2(20),
    FOREIGN KEY (dept_id)    REFERENCES Department(dept_id),
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id),
    FOREIGN KEY (room_id)    REFERENCES Classrooms(room_id),
    FOREIGN KEY (slot_id)    REFERENCES Time_Slots(slot_id)
);

-- 7. Students Table
CREATE TABLE Students (
    student_id   NUMBER(5) PRIMARY KEY,
    student_name VARCHAR2(100) NOT NULL,
    roll_no      VARCHAR2(20) UNIQUE,
    dept_id      NUMBER(5),
    semester     NUMBER(2),
    section      VARCHAR2(5),
    email        VARCHAR2(100),
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
);

-- 8. Attendance Table
CREATE TABLE Attendance (
    attendance_id NUMBER(10) PRIMARY KEY,
    student_id    NUMBER(5),
    timetable_id  NUMBER(5),
    attend_date   DATE DEFAULT SYSDATE,
    status        VARCHAR2(10),
    FOREIGN KEY (student_id)   REFERENCES Students(student_id),
    FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id)
);

-- 9. Teacher Subject Mapping Table
CREATE TABLE Teacher_Subject (
    mapping_id    NUMBER(5) PRIMARY KEY,
    teacher_id    NUMBER(5),
    subject_id    NUMBER(5),
    dept_id       NUMBER(5),
    semester      NUMBER(2),
    assigned_date DATE DEFAULT SYSDATE,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id),
    FOREIGN KEY (dept_id)    REFERENCES Department(dept_id)
);

-- 10. Holidays Table
CREATE TABLE Holidays (
    holiday_id   NUMBER(5) PRIMARY KEY,
    holiday_date DATE NOT NULL,
    reason       VARCHAR2(200),
    holiday_type VARCHAR2(30)
);

-- ============================================
-- END OF FILE 01
-- ============================================
