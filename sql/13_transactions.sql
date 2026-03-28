-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 13: Transactions and Savepoints
-- ============================================

-- TRANSACTION 1: Add New Timetable Entries Safely
BEGIN
    -- Step 1: Insert first entry
    INSERT INTO Timetable VALUES (
        seq_timetable.NEXTVAL, 1, 101, 1, 1, 6, 3, 'A', '2025-2026'
    );
    DBMS_OUTPUT.PUT_LINE('Step 1: First entry inserted');
    SAVEPOINT sp1;

    -- Step 2: Insert second entry
    INSERT INTO Timetable VALUES (
        seq_timetable.NEXTVAL, 1, 102, 3, 2, 8, 3, 'A', '2025-2026'
    );
    DBMS_OUTPUT.PUT_LINE('Step 2: Second entry inserted');
    SAVEPOINT sp2;

    -- Step 3: Insert third entry
    INSERT INTO Timetable VALUES (
        seq_timetable.NEXTVAL, 1, 103, 4, 1, 10, 3, 'A', '2025-2026'
    );
    DBMS_OUTPUT.PUT_LINE('Step 3: Third entry inserted');
    SAVEPOINT sp3;

    -- Commit all changes
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('All 3 entries committed successfully!');

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
        DBMS_OUTPUT.PUT_LINE('All changes rolled back!');
END;
/

-- ============================================

-- TRANSACTION 2: Demonstrate ROLLBACK TO SAVEPOINT
BEGIN
    -- Insert valid entry
    INSERT INTO Timetable VALUES (
        seq_timetable.NEXTVAL, 2, 104, 6, 3, 2, 3, 'A', '2025-2026'
    );
    DBMS_OUTPUT.PUT_LINE('Entry 1 inserted successfully');
    SAVEPOINT sp1;

    -- Insert another valid entry
    INSERT INTO Timetable VALUES (
        seq_timetable.NEXTVAL, 2, 105, 7, 3, 4, 3, 'A', '2025-2026'
    );
    DBMS_OUTPUT.PUT_LINE('Entry 2 inserted successfully');
    SAVEPOINT sp2;

    -- Simulate a mistake - rolling back to sp1
    DBMS_OUTPUT.PUT_LINE('Mistake found! Rolling back to SP1...');
    ROLLBACK TO sp1;
    DBMS_OUTPUT.PUT_LINE('Rolled back to SP1 - Entry 2 removed');

    -- Commit only entry 1
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Entry 1 committed. Entry 2 discarded.');

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
END;
/

-- ============================================

-- TRANSACTION 3: Safe Attendance Marking
BEGIN
    -- Mark attendance for multiple students
    INSERT INTO Attendance VALUES
    (seq_attendance.NEXTVAL, 1001, 1, SYSDATE, 'Present');
    SAVEPOINT att_sp1;

    INSERT INTO Attendance VALUES
    (seq_attendance.NEXTVAL, 1002, 1, SYSDATE, 'Present');
    SAVEPOINT att_sp2;

    INSERT INTO Attendance VALUES
    (seq_attendance.NEXTVAL, 1003, 1, SYSDATE, 'Absent');
    SAVEPOINT att_sp3;

    INSERT INTO Attendance VALUES
    (seq_attendance.NEXTVAL, 1004, 1, SYSDATE, 'Present');
    SAVEPOINT att_sp4;

    INSERT INTO Attendance VALUES
    (seq_attendance.NEXTVAL, 1005, 1, SYSDATE, 'OD');

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Attendance marked for 5 students successfully!');

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('ERROR marking attendance: ' || SQLERRM);
        DBMS_OUTPUT.PUT_LINE('All attendance entries rolled back!');
END;
/

-- ============================================

-- TRANSACTION 4: Update and Rollback Demo
DECLARE
    v_old_room NUMBER;
BEGIN
    -- Save original room
    SELECT room_id INTO v_old_room
    FROM Timetable
    WHERE timetable_id = 1;

    DBMS_OUTPUT.PUT_LINE('Original Room ID: ' || v_old_room);
    SAVEPOINT before_update;

    -- Update room
    UPDATE Timetable
    SET room_id = 2
    WHERE timetable_id = 1;
    DBMS_OUTPUT.PUT_LINE('Room updated to ID: 2');

    -- Simulate change of mind
    ROLLBACK TO before_update;
    DBMS_OUTPUT.PUT_LINE('Changed mind! Rolled back to original room.');

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Transaction complete. No changes made.');

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Timetable record not found!');
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
END;
/

-- ============================================
-- END OF FILE 13
-- ============================================
