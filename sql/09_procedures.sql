-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 09: Procedures and Functions
-- ============================================

-- PROCEDURE 1: Show Department Timetable
CREATE OR REPLACE PROCEDURE show_dept_timetable(
    p_dept_id  IN NUMBER,
    p_semester IN NUMBER
) AS
BEGIN
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('TIMETABLE - DEPT: ' || p_dept_id || 
                         ' SEM: ' || p_semester);
    DBMS_OUTPUT.PUT_LINE('========================================');
    FOR rec IN (
        SELECT ts.day_name, ts.start_time, ts.end_time,
               sub.subject_name, teach.teacher_name,
               cr.room_name, t.section
        FROM Timetable t
        JOIN Time_Slots ts  ON t.slot_id    = ts.slot_id
        JOIN Subjects sub   ON t.subject_id = sub.subject_id
        JOIN Teachers teach ON t.teacher_id = teach.teacher_id
        JOIN Classrooms cr  ON t.room_id    = cr.room_id
        WHERE t.dept_id  = p_dept_id
        AND   t.semester = p_semester
        ORDER BY ts.day_name, ts.period_no
    ) LOOP
        DBMS_OUTPUT.PUT_LINE(
            RPAD(rec.day_name, 12)    || ' | ' ||
            rec.start_time || '-' || rec.end_time || ' | ' ||
            RPAD(rec.subject_name,30) || ' | ' ||
            RPAD(rec.teacher_name,20) || ' | ' ||
            'Room: ' || rec.room_name || ' | ' ||
            'Section: ' || rec.section
        );
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('========================================');
END;
/

-- HOW TO CALL:
-- EXEC show_dept_timetable(1, 3);

-- ============================================

-- PROCEDURE 2: Show Teacher Weekly Schedule
CREATE OR REPLACE PROCEDURE show_teacher_schedule(
    p_teacher_id IN NUMBER
) AS
    v_name VARCHAR2(100);
BEGIN
    SELECT teacher_name INTO v_name
    FROM Teachers
    WHERE teacher_id = p_teacher_id;

    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('SCHEDULE FOR: ' || v_name);
    DBMS_OUTPUT.PUT_LINE('========================================');
    FOR rec IN (
        SELECT ts.day_name, ts.start_time, ts.end_time,
               sub.subject_name, cr.room_name, t.section
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id    = ts.slot_id
        JOIN Subjects sub  ON t.subject_id = sub.subject_id
        JOIN Classrooms cr ON t.room_id    = cr.room_id
        WHERE t.teacher_id = p_teacher_id
        ORDER BY ts.day_name, ts.period_no
    ) LOOP
        DBMS_OUTPUT.PUT_LINE(
            RPAD(rec.day_name,12)  || ' | ' ||
            rec.start_time || '-' || rec.end_time || ' | ' ||
            RPAD(rec.subject_name,30) || ' | ' ||
            'Room: ' || rec.room_name || ' | ' ||
            'Section: ' || rec.section
        );
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('========================================');
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Teacher ID ' || 
                              p_teacher_id || ' not found!');
END;
/

-- HOW TO CALL:
-- EXEC show_teacher_schedule(101);

-- ============================================

-- PROCEDURE 3: Mark Attendance
CREATE OR REPLACE PROCEDURE mark_attendance(
    p_student_id   IN NUMBER,
    p_timetable_id IN NUMBER,
    p_date         IN DATE,
    p_status       IN VARCHAR2
) AS
BEGIN
    INSERT INTO Attendance VALUES (
        seq_attendance.NEXTVAL,
        p_student_id,
        p_timetable_id,
        p_date,
        p_status
    );
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Attendance marked successfully for Student ID: ' 
                          || p_student_id);
EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Attendance already marked!');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
        ROLLBACK;
END;
/

-- HOW TO CALL:
-- EXEC mark_attendance(1001, 1, SYSDATE, 'Present');

-- ============================================

-- FUNCTION 1: Check Teacher Clash
CREATE OR REPLACE FUNCTION check_teacher_clash(
    p_teacher_id   IN NUMBER,
    p_slot_id      IN NUMBER,
    p_acad_year    IN VARCHAR2
) RETURN VARCHAR2 AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM Timetable
    WHERE teacher_id    = p_teacher_id
    AND   slot_id       = p_slot_id
    AND   academic_year = p_acad_year;

    IF v_count > 0 THEN
        RETURN 'CLASH DETECTED - Teacher already has a class!';
    ELSE
        RETURN 'SLOT IS FREE - Teacher can be assigned!';
    END IF;
END;
/

-- HOW TO USE:
-- SELECT check_teacher_clash(101, 2, '2025-2026') FROM DUAL;

-- ============================================

-- FUNCTION 2: Get Attendance Status
CREATE
