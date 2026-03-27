-- ============================================
-- TIMETABLE MANAGEMENT SYSTEM
-- File 02: Constraints
-- ============================================

-- 1. Subjects - Valid type only
ALTER TABLE Subjects 
ADD CONSTRAINT chk_subject_type 
CHECK (type IN ('Theory', 'Lab', 'Elective'));

-- 2. Subjects - Valid credits
ALTER TABLE Subjects 
ADD CONSTRAINT chk_credits 
CHECK (credits BETWEEN 1 AND 6);

-- 3. Time_Slots - Valid day names
ALTER TABLE Time_Slots 
ADD CONSTRAINT chk_day 
CHECK (day_name IN ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'));

-- 4. Time_Slots - Valid period number
ALTER TABLE Time_Slots 
ADD CONSTRAINT chk_period 
CHECK (period_no BETWEEN 1 AND 8);

-- 5. Timetable - Valid semester
ALTER TABLE Timetable 
ADD CONSTRAINT chk_semester 
CHECK (semester BETWEEN 1 AND 8);

-- 6. Students - Valid semester
ALTER TABLE Students 
ADD CONSTRAINT chk_student_sem 
CHECK (semester BETWEEN 1 AND 8);

-- 7. Attendance - Valid status only
ALTER TABLE Attendance 
ADD CONSTRAINT chk_status 
CHECK (status IN ('Present', 'Absent', 'OD'));

-- 8. Classrooms - Valid room type
ALTER TABLE Classrooms 
ADD CONSTRAINT chk_room_type 
CHECK (room_type IN ('Lecture Hall', 'Lab', 'Seminar Hall'));

-- 9. Classrooms - Valid capacity
ALTER TABLE Classrooms 
ADD CONSTRAINT chk_capacity 
CHECK (capacity > 0);

-- 10. No same teacher in same slot (clash prevention)
ALTER TABLE Timetable 
ADD CONSTRAINT no_teacher_clash 
UNIQUE (teacher_id, slot_id, academic_year);

-- 11. No same room in same slot (clash prevention)
ALTER TABLE Timetable 
ADD CONSTRAINT no_room_clash 
UNIQUE (room_id, slot_id, academic_year);

-- 12. Teacher email must be unique
ALTER TABLE Teachers
ADD CONSTRAINT uq_teacher_email
UNIQUE (email);

-- 13. Student email must be unique
ALTER TABLE Students
ADD CONSTRAINT uq_student_email
UNIQUE (email);

-- ============================================
-- END OF FILE 02
-- ============================================
