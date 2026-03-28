-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 07: Indexes
-- ============================================

-- INDEX 1: Speed up timetable search by department
CREATE INDEX idx_timetable_dept 
ON Timetable(dept_id, semester);

-- INDEX 2: Speed up teacher schedule lookup
CREATE INDEX idx_timetable_teacher 
ON Timetable(teacher_id);

-- INDEX 3: Speed up room availability check
CREATE INDEX idx_timetable_room 
ON Timetable(room_id, slot_id);

-- INDEX 4: Speed up slot lookup
CREATE INDEX idx_timetable_slot 
ON Timetable(slot_id);

-- INDEX 5: Speed up attendance search by student
CREATE INDEX idx_attendance_student 
ON Attendance(student_id, attend_date);

-- INDEX 6: Speed up attendance search by date
CREATE INDEX idx_attendance_date 
ON Attendance(attend_date);

-- INDEX 7: Speed up student search by department
CREATE INDEX idx_student_dept 
ON Students(dept_id, semester, section);

-- INDEX 8: Speed up student roll number search
CREATE INDEX idx_student_roll 
ON Students(roll_no);

-- INDEX 9: Speed up subject search by department
CREATE INDEX idx_subject_dept 
ON Subjects(dept_id);

-- INDEX 10: Speed up holiday date lookup
CREATE INDEX idx_holiday_date 
ON Holidays(holiday_date);

-- ============================================
-- WHY INDEXES?
-- Without index: Oracle scans every row (slow)
-- With index:    Oracle jumps directly (fast)
-- Best used on columns used in WHERE, JOIN, ORDER BY
-- ============================================

-- END OF FILE 07
-- ============================================
```

---

## 📊 Progress So Far

| File | Status |
|---|---|
| `01_create_tables.sql` | ✅ Done |
| `02_constraints.sql` | ✅ Done |
| `03_sequences.sql` | ✅ Done |
| `04_insert_data.sql` | ✅ Done |
| `05_queries.sql` | ✅ Done |
| `06_views.sql` | ✅ Done |
| `07_indexes.sql` | ⬅️ Do this now |
| `08_triggers.sql` | 🔒 Next |

---

**Commit message to use:**
```
Added 07_indexes.sql - 10 indexes for query optimization
