-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 08: Triggers
-- ============================================

-- First create Audit Log Table
CREATE TABLE Timetable_Audit (
    audit_id     NUMBER(10) PRIMARY KEY,
    action_type  VARCHAR2(10),
    timetable_id NUMBER(5),
    changed_by   VARCHAR2(50) DEFAULT USER,
    changed_on   DATE DEFAULT SYSDATE
);

-- ============================================

-- TRIGGER 1: Prevent Teacher Clash
-- Fires BEFORE INSERT on Timetable
-- Blocks if teacher already has class in same slot

CREATE OR REPLACE TRIGGER prevent_teacher_clash
BEFORE INSERT ON Timetable
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM Timetable
    WHERE teacher_id    = :NEW.teacher_id
    AND   slot_id       = :NEW.slot_id
    AND   academic_year = :NEW.academic_year;

    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20001,
        'ERROR: Teacher is already scheduled in this time slot!');
    END IF;
END;
/

-- ============================================

-- TRIGGER 2: Prevent Room Clash
-- Fires BEFORE INSERT on Timetable
-- Blocks if room already occupied in same slot

CREATE OR REPLACE TRIGGER prevent_room_clash
BEFORE INSERT ON Timetable
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM Timetable
    WHERE room_id       = :NEW.room_id
    AND   slot_id       = :NEW.slot_id
    AND   academic_year = :NEW.academic_year;

    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20002,
        'ERROR: Room is already occupied in this time slot!');
    END IF;
END;
/

-- ============================================

-- TRIGGER 3: Audit Log Trigger
-- Fires AFTER INSERT, UPDATE, DELETE on Timetable
-- Records every change with user and timestamp

CREATE OR REPLACE TRIGGER timetable_audit_log
AFTER INSERT OR UPDATE OR DELETE ON Timetable
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Timetable_Audit VALUES
        (seq_audit.NEXTVAL, 'INSERT', :NEW.timetable_id, USER, SYSDATE);

    ELSIF UPDATING THEN
        INSERT INTO Timetable_Audit VALUES
        (seq_audit.NEXTVAL, 'UPDATE', :NEW.timetable_id, USER, SYSDATE);

    ELSIF DELETING THEN
        INSERT INTO Timetable_Audit VALUES
        (seq_audit.NEXTVAL, 'DELETE', :OLD.timetable_id, USER, SYSDATE);
    END IF;
END;
/

-- ============================================

-- TRIGGER 4: Block Attendance on Holidays
-- Fires BEFORE INSERT on Attendance
-- Prevents marking attendance on holiday dates

CREATE OR REPLACE TRIGGER no_attendance_on_holiday
BEFORE INSERT ON Attendance
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM Holidays
    WHERE holiday_date = TRUNC(:NEW.attend_date);

    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20003,
        'ERROR: Cannot mark attendance - Today is a Holiday!');
    END IF;
END;
/

-- ============================================

-- TRIGGER 5: Auto Update Last Modified Date
-- Fires BEFORE UPDATE on Timetable
-- Useful for tracking when records were last changed

CREATE OR REPLACE TRIGGER trg_timetable_update
BEFORE UPDATE ON Timetable
FOR EACH ROW
BEGIN
    DBMS_OUTPUT.PUT_LINE(
        'Timetable record ' || :OLD.timetable_id || 
        ' updated by ' || USER || 
        ' on ' || TO_CHAR(SYSDATE, 'DD-MON-YYYY HH24:MI')
    );
END;
/

-- ============================================
-- TO CHECK AUDIT LOG:
-- SELECT * FROM Timetable_Audit ORDER BY changed_on DESC;
--
-- TO CHECK ALL TRIGGERS:
-- SELECT trigger_name, status FROM user_triggers;
-- ============================================

-- END OF FILE 08
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
| `08_triggers.sql` | ⬅️ Do this now |
| `09_procedures.sql` | 🔒 Next |

---

**Commit message to use:**
```
Added 08_triggers.sql - 5 triggers including clash detection and audit log
