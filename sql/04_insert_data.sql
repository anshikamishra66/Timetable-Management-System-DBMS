-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 04: Insert Sample Data
-- ============================================

-- 1. Departments
INSERT INTO Department VALUES (seq_dept.NEXTVAL, 'Computer Science and Engineering', 'Dr. Ramesh Kumar');
INSERT INTO Department VALUES (seq_dept.NEXTVAL, 'Information Technology', 'Dr. Priya Sharma');
INSERT INTO Department VALUES (seq_dept.NEXTVAL, 'Electronics and Communication', 'Dr. Anil Verma');

-- 2. Teachers
INSERT INTO Teachers VALUES (seq_teacher.NEXTVAL, 'Mr. Suresh Babu',    1, 'suresh@university.com',  '9876543210');
INSERT INTO Teachers VALUES (seq_teacher.NEXTVAL, 'Ms. Divya Lakshmi',  1, 'divya@university.com',   '9876541230');
INSERT INTO Teachers VALUES (seq_teacher.NEXTVAL, 'Mr. Karthik Raja',   1, 'karthik@university.com', '9876549870');
INSERT INTO Teachers VALUES (seq_teacher.NEXTVAL, 'Ms. Preethi Nair',   2, 'preethi@university.com', '9876512340');
INSERT INTO Teachers VALUES (seq_teacher.NEXTVAL, 'Mr. Arun Prakash',   2, 'arun@university.com',    '9876598760');
INSERT INTO Teachers VALUES (seq_teacher.NEXTVAL, 'Ms. Kavitha Menon',  3, 'kavitha@university.com', '9876567890');

-- 3. Subjects
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'Database Management Systems',  'CS301',  1, 4, 'Theory');
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'DBMS Laboratory',              'CS301L', 1, 2, 'Lab');
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'Data Structures',              'CS201',  1, 4, 'Theory');
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'Operating Systems',            'CS401',  1, 4, 'Theory');
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'Computer Networks',            'CS501',  1, 4, 'Theory');
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'Web Technology',               'IT301',  2, 4, 'Theory');
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'Software Engineering',         'IT401',  2, 4, 'Theory');
INSERT INTO Subjects VALUES (seq_subject.NEXTVAL, 'Digital Electronics',          'EC301',  3, 4, 'Theory');

-- 4. Classrooms
INSERT INTO Classrooms VALUES (seq_classroom.NEXTVAL, 'Room 101',    60, 'Lecture Hall');
INSERT INTO Classrooms VALUES (seq_classroom.NEXTVAL, 'Room 102',    60, 'Lecture Hall');
INSERT INTO Classrooms VALUES (seq_classroom.NEXTVAL, 'Room 201',    60, 'Lecture Hall');
INSERT INTO Classrooms VALUES (seq_classroom.NEXTVAL, 'CS Lab 1',    40, 'Lab');
INSERT INTO Classrooms VALUES (seq_classroom.NEXTVAL, 'CS Lab 2',    40, 'Lab');
INSERT INTO Classrooms VALUES (seq_classroom.NEXTVAL, 'Seminar Hall', 100, 'Seminar Hall');

-- 5. Time Slots
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Monday',    '09:00', '10:00', 1);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Monday',    '10:00', '11:00', 2);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Monday',    '11:00', '12:00', 3);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Tuesday',   '09:00', '10:00', 1);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Tuesday',   '10:00', '11:00', 2);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Tuesday',   '11:00', '12:00', 3);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Wednesday', '09:00', '10:00', 1);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Wednesday', '10:00', '11:00', 2);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Thursday',  '09:00', '10:00', 1);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Thursday',  '10:00', '11:00', 2);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Friday',    '09:00', '10:00', 1);
INSERT INTO Time_Slots VALUES (seq_slot.NEXTVAL, 'Friday',    '10:00', '11:00', 2);

-- 6. Timetable Entries
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 101, 1, 1, 1,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 102, 3, 1, 2,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 103, 4, 2, 3,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 101, 5, 1, 4,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 102, 3, 2, 5,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 103, 1, 1, 7,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 101, 2, 4, 9,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 1, 102, 4, 1, 11, 3, 'B', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 2, 104, 6, 3, 6,  3, 'A', '2025-2026');
INSERT INTO Timetable VALUES (seq_timetable.NEXTVAL, 2, 105, 7, 3, 8,  3, 'A', '2025-2026');

-- 7. Students
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Aarav Sharma',    'CS2023001', 1, 3, 'A', 'aarav@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Priya Patel',     'CS2023002', 1, 3, 'A', 'priya@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Rahul Verma',     'CS2023003', 1, 3, 'A', 'rahul@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Sneha Reddy',     'CS2023004', 1, 3, 'A', 'sneha@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Arjun Nair',      'CS2023005', 1, 3, 'A', 'arjun@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Meena Iyer',      'CS2023006', 1, 3, 'A', 'meena@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Vikram Singh',    'CS2023007', 1, 3, 'B', 'vikram@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Ananya Das',      'CS2023008', 1, 3, 'B', 'ananya@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Kiran Kumar',     'CS2023009', 1, 3, 'B', 'kiran@mail.com');
INSERT INTO Students VALUES (seq_student.NEXTVAL, 'Divya Menon',     'CS2023010', 1, 3, 'B', 'divya@mail.com');

-- 8. Attendance Records
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1001, 1, TO_DATE('2026-01-06','YYYY-MM-DD'), 'Present');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1001, 2, TO_DATE('2026-01-06','YYYY-MM-DD'), 'Present');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1002, 1, TO_DATE('2026-01-06','YYYY-MM-DD'), 'Absent');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1002, 2, TO_DATE('2026-01-06','YYYY-MM-DD'), 'Present');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1003, 1, TO_DATE('2026-01-06','YYYY-MM-DD'), 'Present');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1003, 2, TO_DATE('2026-01-06','YYYY-MM-DD'), 'OD');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1001, 1, TO_DATE('2026-01-07','YYYY-MM-DD'), 'Present');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1002, 1, TO_DATE('2026-01-07','YYYY-MM-DD'), 'Absent');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1003, 1, TO_DATE('2026-01-07','YYYY-MM-DD'), 'Present');
INSERT INTO Attendance VALUES (seq_attendance.NEXTVAL, 1004, 1, TO_DATE('2026-01-07','YYYY-MM-DD'), 'Present');

-- 9. Teacher Subject Mapping
INSERT INTO Teacher_Subject VALUES (seq_mapping.NEXTVAL, 101, 1, 1, 3, SYSDATE);
INSERT INTO Teacher_Subject VALUES (seq_mapping.NEXTVAL, 101, 5, 1, 3, SYSDATE);
INSERT INTO Teacher_Subject VALUES (seq_mapping.NEXTVAL, 102, 3, 1, 3, SYSDATE);
INSERT INTO Teacher_Subject VALUES (seq_mapping.NEXTVAL, 102, 4, 1, 3, SYSDATE);
INSERT INTO Teacher_Subject VALUES (seq_mapping.NEXTVAL, 103, 4, 1, 3, SYSDATE);
INSERT INTO Teacher_Subject VALUES (seq_mapping.NEXTVAL, 104, 6, 2, 3, SYSDATE);
INSERT INTO Teacher_Subject VALUES (seq_mapping.NEXTVAL, 105, 7, 2, 3, SYSDATE);

-- 10. Holidays
INSERT INTO Holidays VALUES (seq_holiday.NEXTVAL, TO_DATE('2026-01-26','YYYY-MM-DD'), 'Republic Day',   'National');
INSERT INTO Holidays VALUES (seq_holiday.NEXTVAL, TO_DATE('2026-03-25','YYYY-MM-DD'), 'Holi',           'Festival');
INSERT INTO Holidays VALUES (seq_holiday.NEXTVAL, TO_DATE('2026-08-15','YYYY-MM-DD'), 'Independence Day','National');
INSERT INTO Holidays VALUES (seq_holiday.NEXTVAL, TO_DATE('2026-10-02','YYYY-MM-DD'), 'Gandhi Jayanti', 'National');

COMMIT;

-- ============================================
-- END OF FILE 04
-- ============================================
```

---

## 📊 Progress So Far

| File | Status |
|---|---|
| `01_create_tables.sql` | ✅ Done |
| `02_constraints.sql` | ✅ Done |
| `03_sequences.sql` | ✅ Done |
| `04_insert_data.sql` | ⬅️ Do this now |
| `05_queries.sql` | 🔒 Next |

---

**Commit message to use:**
```
Added 04_insert_data.sql - Realistic data for all 10 tables
