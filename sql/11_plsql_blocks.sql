-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 11: PL/SQL Blocks with Exception Handling
-- ============================================

-- BLOCK 1: Check Teacher Clash with User Input
DECLARE
    v_teacher_id NUMBER := &teacher_id;
    v_slot_id    NUMBER := &slot_id;
    v_count      NUMBER;
    v_name       VARCHAR2(100);
BEGIN
    -- Get teacher name
    SELECT teacher_name INTO v_name
    FROM Teachers
    WHERE teacher_id = v_teacher_id;

    -- Check for clash
    SELECT COUNT(*) INTO v_count
    FROM Timetable
    WHERE teacher_id = v_teacher_id
    AND   slot_id    = v_slot_id;

    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('CLASH CHECK FOR: ' || v_name);
    DBMS_OUTPUT.PUT_LINE('========================================');

    IF v_count > 0 THEN
        DBMS_OUTPUT.PUT_LINE('STATUS: CLASH DETECTED!');
        DBMS_OUTPUT.PUT_LINE('Teacher already has a class in this slot.');
    ELSE
        DBMS_OUTPUT.PUT_LINE('STATUS: SLOT IS FREE!');
        DBMS_OUTPUT.PUT_LINE('Teacher can be assigned to this slot.');
    END IF;

    DBMS_OUTPUT.PUT_LINE('========================================');

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Teacher ID ' || 
                              v_teacher_id || ' does not exist!');
    WHEN TOO_MANY_ROWS THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Multiple records found!');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('UNEXPECTED ERROR: ' || SQLERRM);
END;
/

-- ============================================

-- BLOCK 2: Student Attendance Status Check
DECLARE
    v_student_id NUMBER := &student_id;
    v_name       VARCHAR2(100);
    v_roll       VARCHAR2(20);
    v_total      NUMBER;
    v_attended   NUMBER;
    v_pct        NUMBER;
BEGIN
    -- Get student details
    SELECT student_name, roll_no
    INTO v_name, v_roll
    FROM Students
    WHERE student_id = v_student_id;

    -- Calculate attendance
    SELECT 
        COUNT(*),
        SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END)
    INTO v_total, v_attended
    FROM Attendance
    WHERE student_id = v_student_id;

    -- Calculate percentage
    v_pct := ROUND(v_attended * 100.0 / v_total, 2);

    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('ATTENDANCE REPORT');
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('Name       : ' || v_name);
    DBMS_OUTPUT.PUT_LINE('Roll No    : ' || v_roll);
    DBMS_OUTPUT.PUT_LINE('Total      : ' || v_total);
    DBMS_OUTPUT.PUT_LINE('Attended   : ' || v_attended);
    DBMS_OUTPUT.PUT_LINE('Percentage : ' || v_pct || '%');

    IF v_pct >= 75 THEN
        DBMS_OUTPUT.PUT_LINE('STATUS     : SAFE');
    ELSIF v_pct >= 60 THEN
        DBMS_OUTPUT.PUT_LINE('STATUS     : WARNING - Attendance low!');
    ELSE
        DBMS_OUTPUT.PUT_LINE('STATUS     : DETAINED - Below 60%!');
    END IF;

    DBMS_OUTPUT.PUT_LINE('========================================');

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Student ID ' || 
                              v_student_id || ' not found!');
    WHEN ZERO_DIVIDE THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: No attendance records found!');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('UNEXPECTED ERROR: ' || SQLERRM);
END;
/

-- ============================================

-- BLOCK 3: Room Availability Checker
DECLARE
    v_slot_id  NUMBER := &slot_id;
    v_count    NUMBER;
    v_day      VARCHAR2(20);
    v_time     VARCHAR2(20);
BEGIN
    -- Get slot details
    SELECT day_name, start_time || '-' || end_time
    INTO v_day, v_time
    FROM Time_Slots
    WHERE slot_id = v_slot_id;

    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('ROOM AVAILABILITY FOR SLOT ' || v_slot_id);
    DBMS_OUTPUT.PUT_LINE('Day: ' || v_day || ' Time: ' || v_time);
    DBMS_OUTPUT.PUT_LINE('========================================');

    -- List all free rooms
    FOR rec IN (
        SELECT room_name, capacity, room_type
        FROM Classrooms
        WHERE room_id NOT IN (
            SELECT room_id FROM Timetable WHERE slot_id = v_slot_id
        )
        ORDER BY capacity DESC
    ) LOOP
        DBMS_OUTPUT.PUT_LINE(
            RPAD(rec.room_name, 15) || ' | ' ||
            'Capacity: ' || rec.capacity || ' | ' ||
            rec.room_type
        );
        v_count := v_count + 1;
    END LOOP;

    IF v_count = 0 THEN
        DBMS_OUTPUT.PUT_LINE('No free rooms available in this slot!');
    ELSE
        DBMS_OUTPUT.PUT_LINE('Total Free Rooms: ' || v_count);
    END IF;

    DBMS_OUTPUT.PUT_LINE('========================================');

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Slot ID ' || 
                              v_slot_id || ' not found!');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('UNEXPECTED ERROR: ' || SQLERRM);
END;
/

-- ============================================

-- BLOCK 4: Department Summary Report
DECLARE
    v_dept_id  NUMBER := &dept_id;
    v_dname    VARCHAR2(100);
    v_teachers NUMBER;
    v_subjec
