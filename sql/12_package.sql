-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 12: Package
-- ============================================

-- PACKAGE SPECIFICATION
-- (Declares all procedures and functions)
CREATE OR REPLACE PACKAGE timetable_pkg AS

    -- Procedures
    PROCEDURE show_dept_schedule(
        p_dept_id  IN NUMBER,
        p_semester IN NUMBER
    );

    PROCEDURE show_teacher_schedule(
        p_teacher_id IN NUMBER
    );

    PROCEDURE show_detention_list;

    PROCEDURE show_dept_summary(
        p_dept_id IN NUMBER
    );

    -- Functions
    FUNCTION check_clash(
        p_teacher_id IN NUMBER,
        p_slot_id    IN NUMBER,
        p_acad_year  IN VARCHAR2
    ) RETURN VARCHAR2;

    FUNCTION get_free_rooms(
        p_slot_id IN NUMBER
    ) RETURN NUMBER;

    FUNCTION get_attendance_pct(
        p_student_id IN NUMBER
    ) RETURN NUMBER;

END timetable_pkg;
/

-- ============================================

-- PACKAGE BODY
-- (Implements all procedures and functions)
CREATE OR REPLACE PACKAGE BODY timetable_pkg AS

    -- ----------------------------------------
    -- PROCEDURE 1: Show Department Schedule
    -- ----------------------------------------
    PROCEDURE show_dept_schedule(
        p_dept_id  IN NUMBER,
        p_semester IN NUMBER
    ) AS
        v_dname VARCHAR2(100);
    BEGIN
        SELECT dept_name INTO v_dname
        FROM Department
        WHERE dept_id = p_dept_id;

        DBMS_OUTPUT.PUT_LINE('========================================');
        DBMS_OUTPUT.PUT_LINE('TIMETABLE: ' || v_dname || 
                             ' | SEM: ' || p_semester);
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
                RPAD(rec.day_name,12)      || ' | ' ||
                rec.start_time || '-' ||
                rec.end_time               || ' | ' ||
                RPAD(rec.subject_name, 25) || ' | ' ||
                RPAD(rec.teacher_name, 20) || ' | ' ||
                'Room: ' || rec.room_name  || ' | ' ||
                'Sec: '  || rec.section
            );
        END LOOP;
        DBMS_OUTPUT.PUT_LINE('========================================');
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            DBMS_OUTPUT.PUT_LINE('ERROR: Department not found!');
    END show_dept_schedule;

    -- ----------------------------------------
    -- PROCEDURE 2: Show Teacher Schedule
    -- ----------------------------------------
    PROCEDURE show_teacher_schedule(
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
                RPAD(rec.day_name, 12)     || ' | ' ||
                rec.start_time || '-' ||
                rec.end_time               || ' | ' ||
                RPAD(rec.subject_name, 25) || ' | ' ||
                'Room: ' || rec.room_name  || ' | ' ||
          
