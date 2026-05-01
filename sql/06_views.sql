-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 06: Views, Synonyms
-- ============================================

-- VIEW 1: Full Timetable View
CREATE OR REPLACE VIEW Full_Timetable AS
SELECT 
    d.dept_name,
    t.semester,
    t.section,
    t.academic_year,
    ts.day_name,
    ts.start_time,
    ts.end_time,
    ts.period_no,
    sub.subject_name,
    sub.type        AS subject_type,
    teach.teacher_name,
    cr.room_name,
    cr.room_type
FROM Timetable t
JOIN Department d   ON t.dept_id    = d.dept_id
JOIN Time_Slots ts  ON t.slot_id    = ts.slot_id
JOIN Subjects sub   ON t.subject_id = sub.subject_id
JOIN Teachers teach ON t.teacher_id = teach.teacher_id
JOIN Classrooms cr  ON t.room_id    = cr.room_id;

-- HOW TO USE:
-- SELECT * FROM Full_Timetable WHERE dept_name = 'Computer Science and Engineering';
-- SELECT * FROM Full_Timetable WHERE teacher_name = 'Mr. Suresh Babu';
-- SELECT * FROM Full_Timetable WHERE day_name = 'Monday';

-- ============================================

-- VIEW 2: Teacher Workload View
CREATE OR REPLACE VIEW Teacher_Workload_View AS
SELECT 
    teach.teacher_id,
    teach.teacher_name,
    d.dept_name,
    COUNT(t.timetable_id)        AS periods_per_week,
    COUNT(DISTINCT t.subject_id) AS subjects_handling
FROM Teachers teach
JOIN Department d   ON teach.dept_id  = d.dept_id
LEFT JOIN Timetable t ON teach.teacher_id = t.teacher_id
GROUP BY teach.teacher_id, teach.teacher_name, d.dept_name;

-- HOW TO USE:
-- SELECT * FROM Teacher_Workload_View ORDER BY periods_per_week DESC;

-- ============================================

-- VIEW 3: Student Attendance View
CREATE OR REPLACE VIEW Student_Attendance_View AS
SELECT 
    s.student_id,
    s.student_name,
    s.roll_no,
    s.section,
    COUNT(a.attendance_id) AS total_classes,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended,
    ROUND(
        SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0
        / COUNT(a.attendance_id), 2
    ) AS attendance_pct
FROM Students s
JOIN Attendance a ON s.student_id = a.student_id
GROUP BY s.student_id, s.student_name, s.roll_no, s.section;

-- HOW TO USE:
-- SELECT * FROM Student_Attendance_View WHERE attendance_pct < 75;
-- SELECT * FROM Student_Attendance_View ORDER BY attendance_pct ASC;

-- ============================================

-- VIEW 4: Room Availability View
CREATE OR REPLACE VIEW Room_Availability_View AS
SELECT 
    cr.room_name,
    cr.capacity,
    cr.room_type,
    ts.day_name,
    ts.start_time,
    ts.end_time,
    CASE 
        WHEN t.room_id IS NOT NULL THEN 'Occupied'
        ELSE 'Available'
    END AS availability_status,
    teach.teacher_name AS occupied_by
FROM Classrooms cr
CROSS JOIN Time_Slots ts
LEFT JOIN Timetable t  ON cr.room_id  = t.room_id 
                      AND ts.slot_id  = t.slot_id
LEFT JOIN Teachers teach ON t.teacher_id = teach.teacher_id;

-- HOW TO USE:
-- SELECT * FROM Room_Availability_View WHERE availability_status = 'Available';

-- ============================================

-- SYNONYMS
CREATE OR REPLACE SYNONYM tt      FOR Timetable;
CREATE OR REPLACE SYNONYM tt_view FOR Full_Timetable;
CREATE OR REPLACE SYNONYM att     FOR Attendance;

-- HOW TO USE:
-- SELECT * FROM tt;
-- SELECT * FROM tt_view;

-- ============================================
-- END OF FILE 06
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
| `06_views.sql` | ⬅️ Do this now |
| `07_indexes.sql` | 🔒 Next |

---

**Commit message to use:**
```
Added 06_views.sql - 4 views and 3 synonyms created
