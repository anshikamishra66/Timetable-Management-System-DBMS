-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 10: Cursors
-- ============================================

-- CURSOR 1: Print Full Weekly Timetable
DECLARE
    CURSOR c_timetable IS
        SELECT 
            ts.day_name,
            ts.start_time,
            ts.end_time,
            sub.subject_name,
            teach.teacher_name,
            cr.room_name,
            t.section
        FROM Timetable t
        JOIN Time_Slots ts  ON t.slot_id    = ts.slot_id
        JOIN Subjects sub   ON t.subject_id = sub.subject_id
        JOIN Teachers teach ON t.teacher_id = teach.teacher_id
        JOIN Classrooms cr  ON t.room_id    = cr.room_id
        WHERE t.dept_id  = 1
        AND   t.semester = 3
        ORDER BY ts.day_name, ts.period_no;

    v_row c_timetable%ROWTYPE;
BEGIN
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('COMPLETE WEEKLY TIMETABLE - SEM 3');
    DBMS_OUTPUT.PUT_LINE('========================================');

    OPEN c_timetable;
    LOOP
        FETCH c_timetable INTO v_row;
        EXIT WHEN c_timetable%NOTFOUND;

        DBMS_OUTPUT.PUT_LINE(
            RPAD(v_row.day_name, 12)       || ' | ' ||
            v_row.start_time || '-' || 
            v_row.end_time                 || ' | ' ||
            RPAD(v_row.subject_name, 30)   || ' | ' ||
            RPAD(v_row.teacher_name, 20)   || ' | ' ||
            'Room: ' || v_row.room_name    || ' | ' ||
            'Sec: '  || v_row.section
        );
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('Total Classes: ' || c_timetable%ROWCOUNT);
    DBMS_OUTPUT.PUT_LINE('========================================');

    CLOSE c_timetable;
END;
/

-- ============================================

-- CURSOR 2: Print Attendance Defaulters List
DECLARE
    CURSOR c_defaulters IS
        SELECT 
            s.student_name,
            s.roll_no,
            s.section,
            COUNT(a.attendance_id) AS total_classes,
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended,
            ROUND(
                SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0
                / COUNT(a.attendance_id), 2
            ) AS pct
        FROM Students s
        JOIN Attendance a ON s.student_id = a.student_id
        GROUP BY s.student_name, s.roll_no, s.section
        HAVING ROUND(
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0
            / COUNT(a.attendance_id), 2
        ) < 75
        ORDER BY pct ASC;

BEGIN
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('DETENTION LIST - BELOW 75% ATTENDANCE');
    DBMS_OUTPUT.PUT_LINE('========================================');

    FOR rec IN c_defaulters LOOP
        DBMS_OUTPUT.PUT_LINE(
            RPAD(rec.roll_no, 12)       || ' | ' ||
            RPAD(rec.student_name, 20)  || ' | ' ||
            'Section: ' || rec.section  || ' | ' ||
            'Attended: ' || rec.attended || '/' || rec.total_classes || ' | ' ||
            'Percentage: ' || rec.pct   || '%'
        );
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('========================================');
END;
/

-- ============================================

-- CURSOR 3: Print Teacher Workload Report
DECLARE
    CURSOR c_workload IS
        SELECT 
            teach.teacher_name,
            d.dept_name,
            COUNT(t.timetable_id)        AS total_periods,
            COUNT(DISTINCT t.subject_id) AS total_subjects
        FROM Teachers teach
        JOIN Department d     ON teach.dept_id    = d.dept_id
        LEFT JOIN Timetable t ON teach.teacher_id = t.teacher_id
        GROUP BY teach.teacher_name, d.dept_name
        ORDER BY total_periods DESC;

BEGIN
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('TEACHER WORKLOAD REPORT');
    DBMS_OUTPUT.PUT_LINE('========================================');

    FOR rec IN c_workload LOOP
        DBMS_OUTPUT.PUT_LINE(
            RPAD(rec.teacher_name, 22) || ' | ' ||
            RPAD(rec.dept_name, 35)    || ' | ' ||
            'Periods/Week: ' || rec.total_periods  || ' | ' ||
            'Subjects: '     || rec.total_subjects
        );
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('========================================');
END;
/

-- ============================================

-- CURSOR 4: Print Free Rooms for Each Slot
DECLARE
    CURSOR c_free_rooms IS
        SELECT 
            cr.room_name,
            cr.capacity,
            cr.room_type
        FROM Classrooms cr
        WHERE cr.room_id NOT IN (
            SELECT room_id
            FROM Timetable
            WHERE slot_id = 1
        )
        ORDER BY cr.capacity DESC;

BEGIN
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('FREE ROOMS FOR SLOT 1');
    DBMS_OUTPUT.PUT_LINE('========================================');

    FOR rec IN c_free_rooms LOOP
        DBMS_OUTPUT.PUT_LINE(
            RPAD(rec.room_name, 15) || ' | ' ||
            'Capacity: ' || rec.capacity || ' | ' ||
            rec.room_type
        );
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('========================================');
END;
/

-- ============================================
-- END OF FILE 10
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
| `07_indexes.sql` | ✅ Done |
| `08_triggers.sql` | ✅ Done |
| `09_procedures.sql` | ✅ Done |
| `10_cursors.sql` | ⬅️ Do this now |
| `11_plsql_blocks.sql` | 🔒 Next |

---

**Commit message to use:**
```
Added 10_cursors.sql - 4 explicit cursors created
