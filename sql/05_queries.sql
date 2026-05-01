-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 05: SQL Queries
-- ============================================

-- QUERY 1: Full timetable for a department
SELECT 
    ts.day_name,
    ts.start_time,
    ts.end_time,
    sub.subject_name,
    sub.type,
    teach.teacher_name,
    cr.room_name,
    t.section
FROM Timetable t
JOIN Time_Slots ts   ON t.slot_id    = ts.slot_id
JOIN Subjects sub    ON t.subject_id = sub.subject_id
JOIN Teachers teach  ON t.teacher_id = teach.teacher_id
JOIN Classrooms cr   ON t.room_id    = cr.room_id
WHERE t.dept_id = 1 
AND t.semester  = 3
ORDER BY ts.day_name, ts.period_no;

-- ============================================

-- QUERY 2: Teacher's weekly schedule
SELECT 
    ts.day_name,
    ts.start_time,
    ts.end_time,
    sub.subject_name,
    cr.room_name,
    t.section
FROM Timetable t
JOIN Time_Slots ts  ON t.slot_id    = ts.slot_id
JOIN Subjects sub   ON t.subject_id = sub.subject_id
JOIN Classrooms cr  ON t.room_id    = cr.room_id
WHERE t.teacher_id = 101
ORDER BY ts.day_name, ts.period_no;

-- ============================================

-- QUERY 3: Find FREE rooms at a specific time slot
SELECT 
    room_name,
    capacity,
    room_type
FROM Classrooms
WHERE room_id NOT IN (
    SELECT room_id 
    FROM Timetable 
    WHERE slot_id = 1
)
ORDER BY capacity;

-- ============================================

-- QUERY 4: Find FREE teachers at a specific time slot
SELECT 
    teacher_name,
    email
FROM Teachers
WHERE teacher_id NOT IN (
    SELECT teacher_id 
    FROM Timetable 
    WHERE slot_id = 1
);

-- ============================================

-- QUERY 5: Teacher workload analysis
SELECT 
    teach.teacher_name,
    d.dept_name,
    COUNT(t.timetable_id)  AS total_periods_per_week,
    COUNT(DISTINCT t.subject_id) AS total_subjects
FROM Teachers teach
JOIN Department d ON teach.dept_id = d.dept_id
LEFT JOIN Timetable t ON teach.teacher_id = t.teacher_id
GROUP BY teach.teacher_name, d.dept_name
ORDER BY total_periods_per_week DESC;

-- ============================================

-- QUERY 6: Student attendance percentage
SELECT 
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
GROUP BY s.student_name, s.roll_no, s.section
ORDER BY attendance_pct ASC;

-- ============================================

-- QUERY 7: Detention list (below 75%)
SELECT 
    s.student_name,
    s.roll_no,
    s.section,
    ROUND(
        SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 
        / COUNT(a.attendance_id), 2
    ) AS attendance_pct
FROM Students s
JOIN Attendance a ON s.student_id = a.student_id
GROUP BY s.student_name, s.roll_no, s.section
HAVING ROUND(
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 
    / COUNT(a.attendance_id), 2
) < 75
ORDER BY attendance_pct;

-- ============================================

-- QUERY 8: Day-wise timetable summary
SELECT 
    ts.day_name,
    COUNT(t.timetable_id)        AS total_classes,
    COUNT(DISTINCT t.teacher_id) AS teachers_engaged,
    COUNT(DISTINCT t.room_id)    AS rooms_used
FROM Time_Slots ts
LEFT JOIN Timetable t ON ts.slot_id = t.slot_id
GROUP BY ts.day_name
ORDER BY ts.day_name;

-- ============================================

-- QUERY 9: Subject wise class count per week
SELECT 
    sub.subject_name,
    sub.type,
    COUNT(t.timetable_id) AS classes_per_week
FROM Subjects sub
LEFT JOIN Timetable t ON sub.subject_id = t.subject_id
GROUP BY sub.subject_name, sub.type
ORDER BY classes_per_week DESC;

-- ============================================

-- QUERY 10: List all upcoming holidays
SELECT 
    holiday_date,
    reason,
    holiday_type
FROM Holidays
WHERE holiday_date >= SYSDATE
ORDER BY holiday_date;

-- ============================================
-- END OF FILE 05
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
| `05_queries.sql` | ⬅️ Do this now |
| `06_views.sql` | 🔒 Next |

---

**Commit message to use:**
```
Added 05_queries.sql - 10 advanced SQL queries
