import json
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from database import (
    get_connection,
    create_tables,
)

app = Flask(__name__)
app.secret_key = 'timetable_secret_key_2025'

DAY_SEQUENCE = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
DAY_INDEX = {day_name: index for index, day_name in enumerate(DAY_SEQUENCE)}
BACKUP_DIR = Path(__file__).resolve().parent / 'backups'
LOCAL_LOCATION_PREFIXES = ('127.', '::1', '192.168.', '10.', '172.')

DEFAULT_DEPT_ID = 3
DEFAULT_SEMESTER = 4
DEFAULT_SECTION = 'A'
DEFAULT_ACADEMIC_YEAR = '2025-2026'

# Initialize database
create_tables()


def ordered_days():
    return list(DAY_SEQUENCE)


def parse_int_value(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_timetable_grid(rows):
    grid = {day: {} for day in ordered_days()}
    for row in rows:
        grid[row['day_name']][row['slot_id']] = row
    return grid


def build_slots_by_day(slots):
    slots_by_day = {day: {} for day in ordered_days()}
    for slot in slots:
        slots_by_day.setdefault(slot['day_name'], {})[slot['period_no']] = slot
    return slots_by_day


def build_period_slots(slots):
    first_slot_by_period = {}
    for slot in slots:
        first_slot_by_period.setdefault(slot['period_no'], slot)
    return [first_slot_by_period[period_no] for period_no in sorted(first_slot_by_period)]


def is_student_session():
    return session.get('role') == 'student' and session.get('student_id')


def is_teacher_session():
    return session.get('role') == 'teacher'


def today_iso():
    return date.today().isoformat()


def parse_iso_date(value, default=None):
    if not value:
        return default
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return default


def next_date_for_day(day_name, base_date=None):
    base = base_date or date.today()
    target_index = DAY_INDEX.get(day_name)
    if target_index is None:
        return base
    days_ahead = (target_index - base.weekday()) % 7
    return base + timedelta(days=days_ahead)


def next_occurrence_for_slot(day_name, start_time, now_value=None):
    now_dt = now_value or datetime.now()
    target_date = next_date_for_day(day_name, now_dt.date())
    start_clock = datetime.strptime(start_time, '%H:%M').time()
    slot_dt = datetime.combine(target_date, start_clock)
    if slot_dt <= now_dt:
        slot_dt += timedelta(days=7)
    return slot_dt


def get_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


def evaluate_location_status(ip_address):
    return 'verified-network' if str(ip_address).startswith(LOCAL_LOCATION_PREFIXES) else 'external-network'


def teacher_route_redirect():
    if 'user' not in session:
        return redirect(url_for('login'))
    if is_student_session():
        return redirect(url_for('dashboard'))
    return None


def get_current_user_record(cursor):
    username = session.get('user')
    user_email = session.get('user_email')
    if user_email:
        cursor.execute(
            '''
            SELECT user_id, username, email, role, name
            FROM Users
            WHERE LOWER(email) = LOWER(?)
            ''',
            (user_email,),
        )
        user_row = cursor.fetchone()
        if user_row:
            return user_row
    if username:
        cursor.execute(
            '''
            SELECT user_id, username, email, role, name
            FROM Users
            WHERE LOWER(username) = LOWER(?)
            ''',
            (username,),
        )
        return cursor.fetchone()
    return None


def get_current_user_id(cursor):
    user_record = get_current_user_record(cursor)
    return user_record['user_id'] if user_record else None


def get_current_teacher(cursor):
    if not is_teacher_session():
        return None

    identity = session.get('user_email') or session.get('user')
    if identity:
        cursor.execute(
            '''
            SELECT teacher_id, teacher_name, dept_id, email, contact_no, availability_status
            FROM Teachers
            WHERE LOWER(email) = LOWER(?)
            ''',
            (identity,),
        )
        teacher_row = cursor.fetchone()
        if teacher_row:
            return teacher_row

    if session.get('user_name'):
        cursor.execute(
            '''
            SELECT teacher_id, teacher_name, dept_id, email, contact_no, availability_status
            FROM Teachers
            WHERE LOWER(teacher_name) = LOWER(?)
            ''',
            (session['user_name'],),
        )
        return cursor.fetchone()
    return None


def resolve_teacher_id(cursor, requested_teacher_id=None):
    if is_teacher_session():
        current_teacher = get_current_teacher(cursor)
        return current_teacher['teacher_id'] if current_teacher else None

    if requested_teacher_id:
        return requested_teacher_id

    cursor.execute("SELECT teacher_id FROM Teachers ORDER BY teacher_name LIMIT 1")
    teacher_row = cursor.fetchone()
    return teacher_row['teacher_id'] if teacher_row else None

def authenticate_local_user(username, password):
    normalized_username = (username or '').strip()
    normalized_password = (password or '').strip()
    if not normalized_username or not normalized_password:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''
            SELECT student_id, student_name, roll_no, email
            FROM Students
            WHERE LOWER(TRIM(roll_no)) = LOWER(TRIM(?))
            ''',
            (normalized_username,),
        )
        student = cursor.fetchone()
        if student and normalized_password == (student['roll_no'] or '')[-3:]:
            return {
                'role': 'student',
                'user': student['roll_no'],
                'user_name': student['student_name'],
                'user_email': student['email'],
                'student_id': student['student_id'],
            }

        cursor.execute(
            '''
            SELECT user_id, username, role, email, name
            FROM Users
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(?)) AND password = ?
            ''',
            (normalized_username, normalized_password),
        )
        user = cursor.fetchone()
        if not user:
            return None

        return {
            'role': user['role'] or 'admin',
            'user': user['username'],
            'user_name': user['name'] or user['username'],
            'user_email': user['email'],
            'student_id': None,
        }
    finally:
        conn.close()


def ensure_attendance_session(cursor, timetable_id, session_date):
    cursor.execute(
        """
        SELECT session_id
        FROM Attendance_Sessions
        WHERE timetable_id=? AND session_date=?
        """,
        (timetable_id, session_date),
    )
    existing = cursor.fetchone()
    if existing:
        return existing['session_id']

    cursor.execute(
        """
        INSERT INTO Attendance_Sessions
            (timetable_id, session_date, attendance_mode, ip_address, created_at, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
        (timetable_id, session_date, 'manual', request.remote_addr),
    )
    return cursor.lastrowid


def log_activity(cursor, action_type, entity_type, entity_id, description, metadata_json=None):
    user_id = get_current_user_id(cursor)
    cursor.execute(
        """
        INSERT INTO Activity_Log
            (actor_email, action_type, entity_type, entity_id, description, ip_address, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            session.get('user_email') or session.get('user'),
            action_type,
            entity_type,
            entity_id,
            description,
            request.remote_addr,
            metadata_json,
        ),
    )

    if user_id is not None:
        cursor.execute(
            '''
            UPDATE Activity_Log
            SET user_id=?
            WHERE log_id = last_insert_rowid()
            ''',
            (user_id,),
        )


def log_system_event(cursor, log_level, source, message, stack_trace=None):
    cursor.execute(
        """
        INSERT INTO System_Log
            (log_level, source, message, stack_trace, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (log_level, source, message, stack_trace),
    )


def load_student_dashboard_data(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT s.*, d.dept_name
        FROM Students s
        JOIN Department d ON s.dept_id = d.dept_id
        WHERE s.student_id=?
        ''',
        (student_id,),
    )
    student = cursor.fetchone()

    cursor.execute(
        '''
        SELECT t.timetable_id, ts.day_name, ts.start_time, ts.end_time,
               sub.subject_name, sub.subject_code, sub.type,
               teach.teacher_name, teach.email AS teacher_email
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        JOIN Teachers teach ON t.teacher_id = teach.teacher_id
        WHERE t.dept_id=? AND t.semester=? AND t.section=?
        ORDER BY
            CASE ts.day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END,
            ts.period_no
        ''',
        (student['dept_id'], student['semester'], student['section']),
    )
    timetable_rows = cursor.fetchall()

    cursor.execute(
        '''
        SELECT
            COUNT(a.attendance_id) AS total_classes,
            SUM(CASE WHEN a.status="Present" THEN 1 ELSE 0 END) AS present_classes
        FROM Attendance a
        WHERE a.student_id=?
        ''',
        (student_id,),
    )
    attendance = cursor.fetchone()
    conn.close()

    total_classes = attendance['total_classes'] or 0
    present_classes = attendance['present_classes'] or 0
    percentage = round((present_classes / total_classes) * 100, 1) if total_classes else 0
    return student, timetable_rows, total_classes, present_classes, percentage


def safe_average(values):
    filtered_values = [value for value in values if value is not None]
    return round(sum(filtered_values) / len(filtered_values), 1) if filtered_values else 0


def fetch_teacher_classes(cursor, teacher_id):
    cursor.execute(
        '''
        SELECT
            t.timetable_id,
            t.dept_id,
            t.slot_id,
            t.room_id,
            t.semester,
            t.section,
            t.academic_year,
            d.dept_name,
            ts.day_name,
            ts.start_time,
            ts.end_time,
            ts.period_no,
            sub.subject_name,
            sub.subject_code,
            sub.type,
            COALESCE(sub.attendance_threshold, 75) AS attendance_threshold,
            cr.room_name
        FROM Timetable t
        JOIN Department d ON t.dept_id = d.dept_id
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        JOIN Classrooms cr ON t.room_id = cr.room_id
        WHERE t.teacher_id = ?
        ORDER BY
            CASE ts.day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END,
            ts.period_no
        ''',
        (teacher_id,),
    )
    return cursor.fetchall()


def build_teacher_recommendations(selected_class, roster_metrics, teacher_classes, recent_lessons):
    recommendations = []
    threshold = selected_class['attendance_threshold'] if selected_class else 75
    at_risk_students = sorted(
        [row for row in roster_metrics if row['risk_level'] in ('high', 'medium')],
        key=lambda item: (item['predicted_percentage'], item['student_name']),
    )
    average_attendance = safe_average([row['current_percentage'] for row in roster_metrics if row['session_count'] > 0])
    average_engagement = safe_average([row['avg_engagement'] for row in roster_metrics if row['avg_engagement'] is not None])
    latest_progress = recent_lessons[0]['syllabus_progress'] if recent_lessons else 0

    if at_risk_students:
        focus_names = ', '.join(student['student_name'].split()[0] for student in at_risk_students[:5])
        recommendations.append(
            {
                'title': 'At-risk students detected',
                'type': 'attendance',
                'priority': 'high',
                'details': f"Focus on {focus_names}. Their projected attendance may move below {threshold:.0f}%.",
            }
        )

    if average_attendance and average_attendance < threshold:
        recommendations.append(
            {
                'title': 'Conduct an extra support class',
                'type': 'intervention',
                'priority': 'high',
                'details': f"{selected_class['subject_name']} is averaging {average_attendance:.1f}% attendance. An extra class can lift coverage before the threshold is breached.",
            }
        )

    if average_engagement and average_engagement < 70:
        recommendations.append(
            {
                'title': 'Increase in-class participation',
                'type': 'engagement',
                'priority': 'medium',
                'details': f"Average engagement is {average_engagement:.1f}%. Try a quick quiz, viva round, or peer task in the next {selected_class['subject_name']} session.",
            }
        )

    if latest_progress and latest_progress < 65:
        recommendations.append(
            {
                'title': 'Lesson coverage is behind pace',
                'type': 'syllabus',
                'priority': 'medium',
                'details': f"Syllabus progress is at {latest_progress:.0f}%. Plan one high-density revision or combined topic session this week.",
            }
        )

    day_periods = {}
    for class_row in teacher_classes:
        day_periods.setdefault(class_row['day_name'], []).append(class_row['period_no'])

    for day_name, periods in day_periods.items():
        ordered_periods = sorted(periods)
        if len(ordered_periods) >= 4:
            recommendations.append(
                {
                    'title': f'Heavy workload on {day_name}',
                    'type': 'optimization',
                    'priority': 'medium',
                    'details': f"You have {len(ordered_periods)} periods on {day_name}. Consider balancing the timetable to reduce teacher fatigue.",
                }
            )
            break

        for previous_period, current_period in zip(ordered_periods, ordered_periods[1:]):
            if current_period - previous_period > 1:
                recommendations.append(
                    {
                        'title': 'Idle gap found in timetable',
                        'type': 'optimization',
                        'priority': 'low',
                        'details': f"{day_name} has a gap between period {previous_period} and {current_period}. The timetable optimizer can compress that gap.",
                    }
                )
                break
        if any(item['type'] == 'optimization' for item in recommendations):
            break

    if not recommendations:
        recommendations.append(
            {
                'title': 'Healthy class signal',
                'type': 'status',
                'priority': 'low',
                'details': 'Attendance, engagement, and timetable spacing are stable. Continue with the current teaching rhythm.',
            }
        )

    return recommendations


def build_teacher_workspace_data(cursor, teacher_id, selected_timetable_id=None, register_start=None, register_end=None):
    cursor.execute(
        '''
        SELECT t.teacher_id, t.teacher_name, t.dept_id, t.email, t.contact_no,
               t.availability_status, d.dept_name
        FROM Teachers t
        JOIN Department d ON t.dept_id = d.dept_id
        WHERE t.teacher_id = ?
        ''',
        (teacher_id,),
    )
    teacher_row = cursor.fetchone()
    teacher_classes = fetch_teacher_classes(cursor, teacher_id)
    selected_class = None
    if teacher_classes:
        selected_class = next(
            (row for row in teacher_classes if row['timetable_id'] == selected_timetable_id),
            teacher_classes[0],
        )

    register_from = register_start or today_iso()
    register_to = register_end or register_from
    active_register_date = register_to or register_from
    roster_metrics = []
    register_rows = []
    attendance_trend = []
    engagement_trend = []
    recent_lessons = []
    recommendations = []
    substitutions = []
    reminders = []
    backup_history = []
    activity_logs = []
    next_class = None
    today_classes = []
    average_attendance = 0
    average_engagement = 0
    session_count = 0
    recent_prediction_count = 0

    if teacher_row:
        teacher_user_id = None
        if teacher_row['email']:
            cursor.execute(
                '''
                SELECT user_id
                FROM Users
                WHERE LOWER(email) = LOWER(?)
                ''',
                (teacher_row['email'],),
            )
            teacher_user = cursor.fetchone()
            teacher_user_id = teacher_user['user_id'] if teacher_user else None

        now_dt = datetime.now()
        current_day_name = now_dt.strftime('%A')
        today_classes = [row for row in teacher_classes if row['day_name'] == current_day_name]
        future_classes = sorted(
            teacher_classes,
            key=lambda row: next_occurrence_for_slot(row['day_name'], row['start_time'], now_dt),
        )
        next_class = future_classes[0] if future_classes else None

        cursor.execute(
            '''
            SELECT r.reminder_id, r.remind_at, r.status, r.message,
                   sub.subject_name, ts.day_name, ts.start_time
            FROM Reminder_Queue r
            JOIN Timetable t ON r.timetable_id = t.timetable_id
            JOIN Subjects sub ON t.subject_id = sub.subject_id
            JOIN Time_Slots ts ON t.slot_id = ts.slot_id
            WHERE t.teacher_id = ?
            ORDER BY r.remind_at ASC
            LIMIT 6
            ''',
            (teacher_id,),
        )
        reminders = cursor.fetchall()

        cursor.execute(
            '''
            SELECT sa.allocation_id, sa.allocation_date, sa.status, sa.note,
                   orig.teacher_name AS original_teacher_name,
                   repl.teacher_name AS substitute_teacher_name,
                   sub.subject_name, ts.day_name, ts.start_time, ts.end_time
            FROM Substitute_Allocations sa
            JOIN Timetable t ON sa.timetable_id = t.timetable_id
            JOIN Subjects sub ON t.subject_id = sub.subject_id
            JOIN Time_Slots ts ON t.slot_id = ts.slot_id
            LEFT JOIN Teachers orig ON sa.original_teacher_id = orig.teacher_id
            LEFT JOIN Teachers repl ON sa.substitute_teacher_id = repl.teacher_id
            WHERE sa.original_teacher_id = ? OR sa.substitute_teacher_id = ?
            ORDER BY sa.allocation_date DESC, sa.created_at DESC
            LIMIT 8
            ''',
            (teacher_id, teacher_id),
        )
        substitutions = cursor.fetchall()

        cursor.execute(
            '''
            SELECT prediction_id
            FROM Attendance_Predictions
            WHERE timetable_id = ?
            ORDER BY created_at DESC
            LIMIT 10
            ''',
            (selected_class['timetable_id'],),
        ) if selected_class else None
        prediction_rows = cursor.fetchall() if selected_class else []
        recent_prediction_count = len(prediction_rows)

        if not is_teacher_session() or session.get('role') == 'admin':
            cursor.execute(
                '''
                SELECT backup_id, file_name, backup_type, status, created_at, restored_at
                FROM Backup_History
                ORDER BY created_at DESC
                LIMIT 6
                '''
            )
            backup_history = cursor.fetchall()

        if teacher_user_id is not None:
            cursor.execute(
                '''
                SELECT action_type, entity_type, description, created_at
                FROM Activity_Log
                WHERE user_id = ? OR LOWER(actor_email) = LOWER(?)
                ORDER BY created_at DESC
                LIMIT 8
                ''',
                (teacher_user_id, teacher_row['email']),
            )
        else:
            cursor.execute(
                '''
                SELECT action_type, entity_type, description, created_at
                FROM Activity_Log
                ORDER BY created_at DESC
                LIMIT 8
                '''
            )
        activity_logs = cursor.fetchall()

    if selected_class:
        cursor.execute(
            '''
            SELECT student_id, student_name, roll_no, email
            FROM Students
            WHERE dept_id = ? AND semester = ? AND section = ?
            ORDER BY roll_no
            ''',
            (selected_class['dept_id'], selected_class['semester'], selected_class['section']),
        )
        roster = cursor.fetchall()

        cursor.execute(
            '''
            SELECT COUNT(*) AS total_sessions
            FROM Attendance_Sessions
            WHERE timetable_id = ?
            ''',
            (selected_class['timetable_id'],),
        )
        session_count = cursor.fetchone()['total_sessions'] or 0

        cursor.execute(
            '''
            SELECT student_id, attend_date, status, location_status
            FROM Attendance
            WHERE timetable_id = ?
            ORDER BY attend_date DESC, attendance_id DESC
            ''',
            (selected_class['timetable_id'],),
        )
        attendance_records = cursor.fetchall()
        attendance_by_student = {}
        for record in attendance_records:
            attendance_by_student.setdefault(record['student_id'], []).append(record)

        cursor.execute(
            '''
            SELECT student_id,
                   ROUND(AVG(engagement_score), 1) AS avg_engagement,
                   ROUND(AVG(participation_score), 1) AS avg_participation,
                   ROUND(AVG(attention_score), 1) AS avg_attention
            FROM Student_Engagement
            WHERE timetable_id = ?
            GROUP BY student_id
            ''',
            (selected_class['timetable_id'],),
        )
        engagement_summary = {
            row['student_id']: row
            for row in cursor.fetchall()
        }

        for student in roster:
            student_records = attendance_by_student.get(student['student_id'], [])
            date_record = next(
                (item for item in student_records if item['attend_date'] == active_register_date),
                None,
            )
            present_count = sum(1 for item in student_records if item['status'] == 'Present')
            total_recorded = len(student_records)
            current_percentage = round((present_count / total_recorded) * 100, 1) if total_recorded else 0

            recent_records = student_records[:4]
            recent_ratio = (
                sum(1 for item in recent_records if item['status'] == 'Present') / len(recent_records)
                if recent_records else 1.0
            )
            overall_ratio = (present_count / total_recorded) if total_recorded else 0.82
            presence_probability = min(max((overall_ratio * 0.65) + (recent_ratio * 0.35), 0.2), 0.98)
            if len(recent_records) >= 2 and all(item['status'] == 'Absent' for item in recent_records[:2]):
                presence_probability = max(0.1, presence_probability - 0.18)

            predicted_percentage = round(
                ((present_count + presence_probability) / (total_recorded + 1)) * 100,
                1,
            ) if total_recorded else round(presence_probability * 100, 1)

            threshold = selected_class['attendance_threshold'] or 75
            if predicted_percentage < threshold - 5:
                risk_level = 'high'
            elif predicted_percentage < threshold + 2:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            engagement_row = engagement_summary.get(student['student_id'])
            average_student_engagement = (
                engagement_row['avg_engagement']
                if engagement_row and engagement_row['avg_engagement'] is not None
                else round((current_percentage * 0.6) + 25, 1) if total_recorded else None
            )
            recommendation = (
                'Immediate mentor follow-up and targeted revision recommended.'
                if risk_level == 'high'
                else 'Add one quick check-in and monitor the next class closely.'
                if risk_level == 'medium'
                else 'Attendance pattern is stable.'
            )

            roster_metrics.append(
                {
                    'student_id': student['student_id'],
                    'student_name': student['student_name'],
                    'roll_no': student['roll_no'],
                    'email': student['email'],
                    'session_count': total_recorded,
                    'present_count': present_count,
                    'current_percentage': current_percentage,
                    'predicted_percentage': predicted_percentage,
                    'risk_level': risk_level,
                    'avg_engagement': average_student_engagement,
                    'avg_participation': engagement_row['avg_participation'] if engagement_row else None,
                    'avg_attention': engagement_row['avg_attention'] if engagement_row else None,
                    'selected_date_status': date_record['status'] if date_record else 'No record',
                    'last_status': student_records[0]['status'] if student_records else 'No record',
                    'last_seen_date': student_records[0]['attend_date'] if student_records else None,
                    'recommendation': recommendation,
                }
            )

        roster_metrics.sort(key=lambda item: (item['predicted_percentage'], item['student_name']))
        average_attendance = safe_average([row['current_percentage'] for row in roster_metrics if row['session_count'] > 0])
        average_engagement = safe_average([row['avg_engagement'] for row in roster_metrics if row['avg_engagement'] is not None])

        cursor.execute(
            '''
            SELECT a.attend_date, s.student_name, s.roll_no, a.status, a.location_status,
                   COALESCE(se.participation_score, 0) AS participation_score,
                   COALESCE(se.attention_score, 0) AS attention_score,
                   COALESCE(se.engagement_score, 0) AS engagement_score
            FROM Attendance a
            JOIN Students s ON a.student_id = s.student_id
            LEFT JOIN Student_Engagement se
                ON se.student_id = a.student_id
               AND se.timetable_id = a.timetable_id
               AND se.engagement_date = a.attend_date
            WHERE a.timetable_id = ?
              AND a.attend_date BETWEEN ? AND ?
            ORDER BY a.attend_date DESC, s.roll_no
            ''',
            (selected_class['timetable_id'], register_from, register_to),
        )
        register_rows = cursor.fetchall()

        cursor.execute(
            '''
            SELECT attend_date,
                   ROUND(AVG(CASE WHEN status = 'Present' THEN 100.0 ELSE 0 END), 1) AS attendance_rate
            FROM Attendance
            WHERE timetable_id = ?
            GROUP BY attend_date
            ORDER BY attend_date DESC
            LIMIT 8
            ''',
            (selected_class['timetable_id'],),
        )
        attendance_trend = list(reversed(cursor.fetchall()))

        cursor.execute(
            '''
            SELECT engagement_date,
                   ROUND(AVG(engagement_score), 1) AS engagement_rate
            FROM Student_Engagement
            WHERE timetable_id = ?
            GROUP BY engagement_date
            ORDER BY engagement_date DESC
            LIMIT 8
            ''',
            (selected_class['timetable_id'],),
        )
        engagement_trend = list(reversed(cursor.fetchall()))

        cursor.execute(
            '''
            SELECT lesson_id, lesson_date, unit_name, topic_name, learning_outcome,
                   homework, syllabus_progress
            FROM Lesson_Tracker
            WHERE timetable_id = ?
            ORDER BY lesson_date DESC, lesson_id DESC
            LIMIT 6
            ''',
            (selected_class['timetable_id'],),
        )
        recent_lessons = cursor.fetchall()
        recommendations = build_teacher_recommendations(selected_class, roster_metrics, teacher_classes, recent_lessons)

    return {
        'teacher': teacher_row,
        'teacher_classes': teacher_classes,
        'selected_class': selected_class,
        'roster_metrics': roster_metrics,
        'register_rows': register_rows,
        'attendance_trend': attendance_trend,
        'engagement_trend': engagement_trend,
        'recent_lessons': recent_lessons,
        'recommendations': recommendations,
        'substitutions': substitutions,
        'reminders': reminders,
        'activity_logs': activity_logs,
        'backup_history': backup_history,
        'next_class': next_class,
        'today_classes': today_classes,
        'average_attendance': average_attendance,
        'average_engagement': average_engagement,
        'session_count': session_count,
        'recent_prediction_count': recent_prediction_count,
        'register_from': register_from,
        'register_to': register_to,
    }


def queue_teacher_reminders(cursor, teacher_row, teacher_classes):
    if not teacher_row or not teacher_classes:
        return 0

    cursor.execute(
        '''
        SELECT user_id
        FROM Users
        WHERE LOWER(email) = LOWER(?)
        ''',
        (teacher_row['email'],),
    )
    user_row = cursor.fetchone()
    target_user_id = user_row['user_id'] if user_row else None
    created_count = 0

    for class_row in teacher_classes:
        reminder_at = next_occurrence_for_slot(class_row['day_name'], class_row['start_time']) - timedelta(minutes=10)
        reminder_value = reminder_at.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            '''
            SELECT reminder_id
            FROM Reminder_Queue
            WHERE timetable_id = ? AND remind_at = ? AND COALESCE(target_user_id, 0) = COALESCE(?, 0)
            ''',
            (class_row['timetable_id'], reminder_value, target_user_id),
        )
        if cursor.fetchone():
            continue

        reminder_message = (
            f"{class_row['subject_name']} class in 10 mins for Semester {class_row['semester']} "
            f"Section {class_row['section']} at {class_row['start_time']} in {class_row['room_name']}."
        )
        cursor.execute(
            '''
            INSERT INTO Reminder_Queue
                (timetable_id, remind_at, target_role, target_user_id, channel, status, message, created_at)
            VALUES (?, ?, 'teacher', ?, 'in_app', 'pending', ?, CURRENT_TIMESTAMP)
            ''',
            (class_row['timetable_id'], reminder_value, target_user_id, reminder_message),
        )
        created_count += 1

    return created_count


def find_available_substitute(cursor, original_teacher_id, timetable_id, allocation_date):
    cursor.execute(
        '''
        SELECT t.timetable_id, t.dept_id, t.slot_id, ts.day_name, ts.start_time, ts.end_time,
               sub.subject_name
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        WHERE t.timetable_id = ? AND t.teacher_id = ?
        ''',
        (timetable_id, original_teacher_id),
    )
    target_class = cursor.fetchone()
    if not target_class:
        return None, None

    cursor.execute(
        '''
        SELECT candidate.teacher_id, candidate.teacher_name, candidate.email
        FROM Teachers candidate
        WHERE candidate.dept_id = ?
          AND candidate.teacher_id <> ?
          AND COALESCE(candidate.is_active, 1) = 1
          AND COALESCE(candidate.availability_status, 'available') = 'available'
          AND NOT EXISTS (
              SELECT 1
              FROM Timetable busy
              WHERE busy.teacher_id = candidate.teacher_id
                AND busy.slot_id = ?
          )
          AND NOT EXISTS (
              SELECT 1
              FROM Teacher_Absences abs
              WHERE abs.teacher_id = candidate.teacher_id
                AND abs.absence_date = ?
                AND COALESCE(abs.status, 'planned') <> 'cancelled'
          )
          AND NOT EXISTS (
              SELECT 1
              FROM Substitute_Allocations alloc
              WHERE alloc.substitute_teacher_id = candidate.teacher_id
                AND alloc.allocation_date = ?
                AND COALESCE(alloc.status, 'assigned') = 'assigned'
          )
        ORDER BY
            (SELECT COUNT(*) FROM Timetable load WHERE load.teacher_id = candidate.teacher_id),
            candidate.teacher_name
        LIMIT 1
        ''',
        (target_class['dept_id'], original_teacher_id, target_class['slot_id'], allocation_date, allocation_date),
    )
    substitute_row = cursor.fetchone()
    return target_class, substitute_row

def timetable_conflicts(cursor, dept_id, semester, section, slot_id, teacher_id, room_id, ignore_timetable_id=None):
    conflicts = []

    cursor.execute(
        '''
        SELECT t.timetable_id, ts.day_name, ts.start_time, ts.end_time, sub.subject_name
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        WHERE t.dept_id=? AND t.semester=? AND t.section=? AND t.slot_id=?
        ''',
        (dept_id, semester, section, slot_id),
    )
    slot_conflict = cursor.fetchone()
    if slot_conflict and (ignore_timetable_id is None or slot_conflict['timetable_id'] != ignore_timetable_id):
        conflicts.append(
            f"Slot clash: {slot_conflict['day_name']} {slot_conflict['start_time']}-{slot_conflict['end_time']} already has {slot_conflict['subject_name']}."
        )

    cursor.execute(
        '''
        SELECT t.timetable_id, ts.day_name, ts.start_time, ts.end_time, d.dept_name, t.semester, t.section
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        JOIN Department d ON t.dept_id = d.dept_id
        WHERE t.teacher_id=? AND t.slot_id=?
        ''',
        (teacher_id, slot_id),
    )
    teacher_conflict = cursor.fetchone()
    if teacher_conflict and (ignore_timetable_id is None or teacher_conflict['timetable_id'] != ignore_timetable_id):
        conflicts.append(
            f"Teacher clash: this faculty is already assigned at {teacher_conflict['day_name']} {teacher_conflict['start_time']}-{teacher_conflict['end_time']} for {teacher_conflict['dept_name']} Semester {teacher_conflict['semester']} Section {teacher_conflict['section']}."
        )

    cursor.execute(
        '''
        SELECT t.timetable_id, ts.day_name, ts.start_time, ts.end_time
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        WHERE t.room_id=? AND t.slot_id=?
        ''',
        (room_id, slot_id),
    )
    room_conflict = cursor.fetchone()
    if room_conflict and (ignore_timetable_id is None or room_conflict['timetable_id'] != ignore_timetable_id):
        conflicts.append(
            f"Room clash: this room is already used at {room_conflict['day_name']} {room_conflict['start_time']}-{room_conflict['end_time']}."
        )

    return conflicts

# ============================================
# AUTH ROUTES
# ============================================

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        auth_result = authenticate_local_user(username, password)

        if not auth_result:
            flash('Invalid login. Use your USN with the last 3 digits, or use admin / admin123 for the full dashboard.', 'error')
            return render_template('login.html')

        session.clear()
        session['user'] = auth_result['user']
        session['user_name'] = auth_result['user_name']
        session['role'] = auth_result['role']
        session['student_id'] = auth_result['student_id']
        if auth_result.get('user_email'):
            session['user_email'] = auth_result['user_email']

        if auth_result['role'] == 'student':
            return redirect(url_for('student_portal', roll_no=auth_result['user']))
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('role', None)
    session.pop('student_id', None)
    return redirect(url_for('login'))

# ============================================
# DASHBOARD
# ============================================

@app.route('/student-portal/<roll_no>')
def student_portal(roll_no):
    if 'user' not in session:
        return redirect(url_for('login'))
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))
    if not is_student_session():
        return redirect(url_for('dashboard'))

    own_roll_no = (session.get('user') or '').strip()
    requested_roll_no = (roll_no or '').strip()
    if own_roll_no.lower() != requested_roll_no.lower():
        return redirect(url_for('student_portal', roll_no=own_roll_no))

    student, timetable_rows, total_classes, present_classes, percentage = load_student_dashboard_data(session['student_id'])
    return render_template(
        'student_dashboard.html',
        student=student,
        timetable=timetable_rows,
        total_classes=total_classes,
        present_classes=present_classes,
        percentage=percentage,
    )

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    if is_student_session():
        return redirect(url_for('student_portal', roll_no=session.get('user')))
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Teachers WHERE dept_id=?", (DEFAULT_DEPT_ID,))
    teachers = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM Students WHERE dept_id=? AND semester=?",
        (DEFAULT_DEPT_ID, DEFAULT_SEMESTER)
    )
    students = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Subjects WHERE dept_id=?", (DEFAULT_DEPT_ID,))
    subjects = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM Timetable WHERE dept_id=? AND semester=? AND section=?",
        (DEFAULT_DEPT_ID, DEFAULT_SEMESTER, DEFAULT_SECTION)
    )
    classes = cursor.fetchone()[0]
    cursor.execute(
        '''
        SELECT ts.day_name, ts.start_time, ts.end_time, sub.subject_name, teach.teacher_name, sub.type
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        JOIN Teachers teach ON t.teacher_id = teach.teacher_id
        WHERE t.dept_id=? AND t.semester=? AND t.section=?
        ORDER BY
            CASE ts.day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END,
            ts.period_no
        LIMIT 4
        ''',
        (DEFAULT_DEPT_ID, DEFAULT_SEMESTER, DEFAULT_SECTION)
    )
    schedule_preview = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html',
        teachers=teachers,
        students=students,
        subjects=subjects,
        classes=classes,
        schedule_preview=schedule_preview,
        department_name='Artificial Intelligence and Data Science',
        semester=DEFAULT_SEMESTER,
        section=DEFAULT_SECTION
    )

# ============================================
# TIMETABLE
# ============================================

@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))

    dept_id = parse_int_value(request.args.get('dept_id'), DEFAULT_DEPT_ID)
    semester = parse_int_value(request.args.get('semester'), DEFAULT_SEMESTER)
    section = request.args.get('section', DEFAULT_SECTION).strip() or DEFAULT_SECTION
    academic_year = request.args.get('academic_year', DEFAULT_ACADEMIC_YEAR)

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        form_dept_id = parse_int_value(request.form.get('dept_id'), DEFAULT_DEPT_ID)
        form_semester = parse_int_value(request.form.get('semester'), DEFAULT_SEMESTER)
        form_section = request.form['section'].strip() or DEFAULT_SECTION
        form_academic_year = request.form['academic_year'].strip() or DEFAULT_ACADEMIC_YEAR
        slot_id = parse_int_value(request.form.get('slot_id'), 0)
        subject_id = parse_int_value(request.form.get('subject_id'), 0)
        teacher_id = parse_int_value(request.form.get('teacher_id'), 0)
        room_id = parse_int_value(request.form.get('room_id'), 0)

        cursor.execute(
            '''
            SELECT timetable_id
            FROM Timetable
            WHERE dept_id=? AND semester=? AND section=? AND slot_id=?
            ''',
            (form_dept_id, form_semester, form_section, slot_id)
        )
        existing = cursor.fetchone()
        conflicts = timetable_conflicts(
            cursor,
            form_dept_id,
            form_semester,
            form_section,
            slot_id,
            teacher_id,
            room_id,
            existing['timetable_id'] if existing else None,
        )

        if conflicts:
            for message in conflicts:
                flash(message, 'error')
            conn.close()
            return redirect(
                url_for(
                    'timetable',
                    dept_id=form_dept_id,
                    semester=form_semester,
                    section=form_section,
                    academic_year=form_academic_year
                )
            )

        if existing:
            cursor.execute(
                '''
                UPDATE Timetable
                SET teacher_id=?, subject_id=?, room_id=?, academic_year=?
                WHERE timetable_id=?
                ''',
                (teacher_id, subject_id, room_id, form_academic_year, existing['timetable_id'])
            )
        else:
            cursor.execute(
                '''
                INSERT INTO Timetable
                    (dept_id, teacher_id, subject_id, room_id, slot_id, semester, section, academic_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (form_dept_id, teacher_id, subject_id, room_id, slot_id, form_semester, form_section, form_academic_year)
            )
        conn.commit()
        flash('Timetable entry saved successfully.', 'success')
        conn.close()
        return redirect(
            url_for(
                'timetable',
                dept_id=form_dept_id,
                semester=form_semester,
                section=form_section,
                academic_year=form_academic_year
            )
        )

    cursor.execute("SELECT * FROM Department ORDER BY dept_name")
    departments = cursor.fetchall()
    cursor.execute("SELECT * FROM Teachers WHERE dept_id=? ORDER BY teacher_name", (dept_id,))
    teachers = cursor.fetchall()
    cursor.execute("SELECT * FROM Subjects WHERE dept_id=? ORDER BY subject_name", (dept_id,))
    subjects = cursor.fetchall()
    cursor.execute("SELECT * FROM Classrooms ORDER BY room_name")
    classrooms = cursor.fetchall()
    cursor.execute("SELECT * FROM Time_Slots ORDER BY slot_id")
    slots = cursor.fetchall()
    cursor.execute(
        '''
        SELECT t.timetable_id, t.slot_id, ts.day_name, ts.start_time, ts.end_time,
               sub.subject_name, teach.teacher_name, cr.room_name, t.section,
               t.semester, sub.type, t.academic_year
        FROM Timetable t
        JOIN Time_Slots ts  ON t.slot_id = ts.slot_id
        JOIN Subjects sub   ON t.subject_id = sub.subject_id
        JOIN Teachers teach ON t.teacher_id = teach.teacher_id
        JOIN Classrooms cr  ON t.room_id = cr.room_id
        WHERE t.dept_id=? AND t.semester=? AND t.section=?
        ORDER BY
            CASE ts.day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END,
            ts.period_no
        ''',
        (dept_id, semester, section)
    )
    timetable_data = cursor.fetchall()
    selected_department_name = next(
        (department['dept_name'] for department in departments if department['dept_id'] == dept_id),
        'Department'
    )
    conn.close()

    timetable_grid = build_timetable_grid(timetable_data)
    slots_by_day = build_slots_by_day(slots)
    period_slots = build_period_slots(slots)

    return render_template(
        'timetable.html',
        timetable=timetable_data,
        timetable_grid=timetable_grid,
        slots=slots,
        slots_by_day=slots_by_day,
        period_slots=period_slots,
        departments=departments,
        teachers=teachers,
        subjects=subjects,
        classrooms=classrooms,
        selected_dept_id=dept_id,
        selected_department_name=selected_department_name,
        selected_semester=semester,
        selected_section=section,
        selected_academic_year=academic_year,
        days=ordered_days()
    )


@app.route('/timetable/delete/<int:id>')
def delete_timetable_entry(id):
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT dept_id, semester, section, academic_year FROM Timetable WHERE timetable_id=?",
        (id,)
    )
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM Timetable WHERE timetable_id=?", (id,))
        conn.commit()
    conn.close()

    if row:
        return redirect(
            url_for(
                'timetable',
                dept_id=row['dept_id'],
                semester=row['semester'],
                section=row['section'],
                academic_year=row['academic_year']
            )
        )
    return redirect(url_for('timetable'))

# ============================================
# TEACHERS
# ============================================

@app.route('/teachers')
def teachers():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.teacher_id, t.teacher_name, d.dept_name,
               t.email, t.contact_no
        FROM Teachers t
        JOIN Department d ON t.dept_id = d.dept_id
    ''')
    teachers_data = cursor.fetchall()
    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()
    conn.close()
    return render_template('teachers.html',
        teachers=teachers_data,
        departments=departments
    )

@app.route('/teachers/add', methods=['POST'])
def add_teacher():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))
    name    = request.form['teacher_name']
    dept_id = request.form['dept_id']
    email   = request.form['email']
    contact = request.form['contact_no']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Teachers (teacher_name, dept_id, email, contact_no) VALUES (?,?,?,?)",
        (name, dept_id, email, contact)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('teachers'))

@app.route('/teachers/delete/<int:id>')
def delete_teacher(id):
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Teachers WHERE teacher_id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('teachers'))

# ============================================
# STUDENTS
# ============================================

@app.route('/students')
def students():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.student_id, s.student_name, s.roll_no,
               d.dept_name, s.semester, s.section, s.email,
               s.admission_id, s.generate_date, s.generate_time
        FROM Students s
        JOIN Department d ON s.dept_id = d.dept_id
        ORDER BY s.roll_no
    ''')
    students_data = cursor.fetchall()
    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()
    conn.close()
    return render_template('students.html',
        students=students_data,
        departments=departments
    )

@app.route('/students/add', methods=['POST'])
def add_student():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))
    name    = request.form['student_name']
    roll    = request.form['roll_no']
    dept_id = request.form['dept_id']
    sem     = request.form['semester']
    sec     = request.form['section']
    email   = request.form['email']
    admission_id = request.form.get('admission_id', '')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Students
            (student_name, roll_no, dept_id, semester, section, email, admission_id)
        VALUES (?,?,?,?,?,?,?)
        """,
        (name, roll, dept_id, sem, sec, email, admission_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('students'))


@app.route('/students/<int:id>')
def student_profile(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if is_student_session():
        return redirect(url_for('student_portal', roll_no=session.get('user')))
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT s.*, d.dept_name
        FROM Students s
        JOIN Department d ON s.dept_id = d.dept_id
        WHERE s.student_id = ?
        ''',
        (id,)
    )
    student = cursor.fetchone()
    if not student:
        conn.close()
        abort(404)

    cursor.execute(
        '''
        SELECT ts.day_name, ts.start_time, ts.end_time,
               sub.subject_name, sub.type, teach.teacher_name, cr.room_name,
               t.academic_year
        FROM Timetable t
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        JOIN Teachers teach ON t.teacher_id = teach.teacher_id
        JOIN Classrooms cr ON t.room_id = cr.room_id
        WHERE t.dept_id = ? AND t.semester = ? AND t.section = ?
        ORDER BY
            CASE ts.day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END,
            ts.period_no
        ''',
        (student['dept_id'], student['semester'], student['section'])
    )
    timetable_data = cursor.fetchall()

    cursor.execute(
        '''
        SELECT
            COUNT(a.attendance_id) AS total_classes,
            SUM(CASE WHEN a.status = "Present" THEN 1 ELSE 0 END) AS present_classes
        FROM Attendance a
        WHERE a.student_id = ?
        ''',
        (id,)
    )
    attendance_summary = cursor.fetchone()
    conn.close()

    total_classes = attendance_summary['total_classes'] or 0
    present_classes = attendance_summary['present_classes'] or 0
    percentage = round((present_classes / total_classes) * 100, 1) if total_classes else 0

    return render_template(
        'student_profile.html',
        student=student,
        timetable=timetable_data,
        total_classes=total_classes,
        present_classes=present_classes,
        percentage=percentage
    )

@app.route('/students/delete/<int:id>')
def delete_student(id):
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if is_teacher_session():
        return redirect(url_for('teacher_workspace'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE student_id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('students'))

# ============================================
# ATTENDANCE
# ============================================

@app.route('/attendance')
def attendance():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_connection()
    cursor = conn.cursor()
    if is_student_session():
        student, timetable_rows, total_classes, present_classes, percentage = load_student_dashboard_data(session['student_id'])
        cursor.execute(
            '''
            SELECT a.attend_date, a.status, sub.subject_name, ts.day_name, ts.start_time, ts.end_time
            FROM Attendance a
            JOIN Timetable t ON a.timetable_id = t.timetable_id
            JOIN Subjects sub ON t.subject_id = sub.subject_id
            JOIN Time_Slots ts ON t.slot_id = ts.slot_id
            WHERE a.student_id=?
            ORDER BY a.attend_date DESC, ts.period_no
            ''',
            (session['student_id'],)
        )
        attendance_records = cursor.fetchall()
        conn.close()
        return render_template(
            'student_attendance.html',
            student=student,
            timetable=timetable_rows,
            attendance_records=attendance_records,
            total_classes=total_classes,
            present_classes=present_classes,
            percentage=percentage,
        )
    if is_teacher_session():
        teacher_id = resolve_teacher_id(cursor)
        teacher_classes = fetch_teacher_classes(cursor, teacher_id) if teacher_id else []
        if not teacher_classes:
            conn.close()
            flash('No classes are assigned to your teacher account yet.', 'error')
            return redirect(url_for('teacher_workspace'))

        teacher_timetable_ids = [row['timetable_id'] for row in teacher_classes]
        timetable_placeholders = ','.join(['?'] * len(teacher_timetable_ids))
        class_filters = [
            (row['dept_id'], row['semester'], row['section'])
            for row in teacher_classes
        ]
        class_filter_sql = ' OR '.join(
            ['(s.dept_id = ? AND s.semester = ? AND s.section = ?)'] * len(class_filters)
        )
        class_filter_values = [
            value
            for class_filter in class_filters
            for value in class_filter
        ]
        cursor.execute(
            f'''
            SELECT s.student_id, s.student_name, s.roll_no,
                   COUNT(a.attendance_id) as total,
                   COALESCE(SUM(CASE WHEN a.status="Present" THEN 1 ELSE 0 END), 0) as attended,
                   ROUND(
                       CASE
                           WHEN COUNT(a.attendance_id) = 0 THEN 0
                           ELSE SUM(CASE WHEN a.status="Present" THEN 1.0 ELSE 0 END) * 100
                                / COUNT(a.attendance_id)
                       END,
                       1
                   ) as percentage
            FROM Students s
            LEFT JOIN Attendance a
                   ON s.student_id = a.student_id
                  AND a.timetable_id IN ({timetable_placeholders})
            WHERE {class_filter_sql}
            GROUP BY s.student_id
            ORDER BY s.roll_no
            ''',
            teacher_timetable_ids + class_filter_values,
        )
        attendance_data = cursor.fetchall()
        cursor.execute(
            f'''
            SELECT DISTINCT s.student_id, s.student_name, s.roll_no
            FROM Students s
            WHERE {class_filter_sql}
            ORDER BY s.roll_no
            ''',
            class_filter_values,
        )
        students_list = cursor.fetchall()
        cursor.execute(
            f'''
            SELECT a.attend_date, s.student_name, s.roll_no, sub.subject_name,
                   ts.day_name, ts.start_time, ts.end_time, a.status, a.updated_at
            FROM Attendance a
            JOIN Students s ON a.student_id = s.student_id
            JOIN Timetable t ON a.timetable_id = t.timetable_id
            JOIN Subjects sub ON t.subject_id = sub.subject_id
            JOIN Time_Slots ts ON t.slot_id = ts.slot_id
            WHERE a.timetable_id IN ({timetable_placeholders})
            ORDER BY a.updated_at DESC, a.attendance_id DESC
            LIMIT 20
            ''',
            teacher_timetable_ids,
        )
        recent_attendance_records = cursor.fetchall()
        conn.close()
        return render_template(
            'attendance.html',
            attendance=attendance_data,
            students=students_list,
            timetable=teacher_classes,
            teacher_mode=True,
            recent_attendance_records=recent_attendance_records,
        )

    cursor.execute('''
        SELECT s.student_name, s.roll_no,
               COUNT(a.attendance_id) as total,
               COALESCE(SUM(CASE WHEN a.status="Present" THEN 1 ELSE 0 END), 0) as attended,
               ROUND(
                   CASE
                       WHEN COUNT(a.attendance_id) = 0 THEN 0
                       ELSE SUM(CASE WHEN a.status="Present" THEN 1.0 ELSE 0 END) * 100
                            / COUNT(a.attendance_id)
                   END,
                   1
               ) as percentage
        FROM Students s
        LEFT JOIN Attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
    ''')
    attendance_data = cursor.fetchall()
    cursor.execute("SELECT * FROM Students")
    students_list = cursor.fetchall()
    cursor.execute(
        '''
        SELECT t.timetable_id, sub.subject_name, ts.day_name, ts.start_time, ts.end_time
        FROM Timetable t
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        ORDER BY
            CASE ts.day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END,
            ts.period_no
        '''
    )
    timetable_list = cursor.fetchall()
    cursor.execute(
        '''
        SELECT a.attend_date, s.student_name, s.roll_no, sub.subject_name,
               ts.day_name, ts.start_time, ts.end_time, a.status, a.updated_at
        FROM Attendance a
        JOIN Students s ON a.student_id = s.student_id
        JOIN Timetable t ON a.timetable_id = t.timetable_id
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        JOIN Time_Slots ts ON t.slot_id = ts.slot_id
        ORDER BY a.updated_at DESC, a.attendance_id DESC
        LIMIT 20
        '''
    )
    recent_attendance_records = cursor.fetchall()
    conn.close()
    return render_template('attendance.html',
        attendance=attendance_data,
        students=students_list,
        timetable=timetable_list,
        recent_attendance_records=recent_attendance_records,
    )

@app.route('/attendance/mark', methods=['POST'])
def mark_attendance():
    if 'user' not in session:
        return redirect(url_for('login'))
    if is_student_session():
        flash('Students can only view attendance. Attendance must be marked by a teacher or admin.', 'error')
        return redirect(url_for('attendance'))
    student_id   = request.form['student_id']
    timetable_id = request.form['timetable_id']
    date         = request.form['date']
    status       = request.form['status']
    conn = get_connection()
    cursor = conn.cursor()
    marked_by_user_id = get_current_user_id(cursor)
    location_status = "manual"

    if is_teacher_session():
        teacher_id = resolve_teacher_id(cursor)
        teacher_classes = fetch_teacher_classes(cursor, teacher_id) if teacher_id else []
        selected_class = next(
            (row for row in teacher_classes if row['timetable_id'] == parse_int_value(timetable_id, 0)),
            None,
        )
        if not selected_class:
            conn.close()
            flash('Teachers can only mark attendance for their own assigned classes.', 'error')
            return redirect(url_for('attendance'))
        cursor.execute(
            '''
            SELECT student_id
            FROM Students
            WHERE student_id = ? AND dept_id = ? AND semester = ? AND section = ?
            ''',
            (student_id, selected_class['dept_id'], selected_class['semester'], selected_class['section']),
        )
        if not cursor.fetchone():
            conn.close()
            flash('Select a student from the assigned class roster.', 'error')
            return redirect(url_for('attendance'))
        location_status = evaluate_location_status(get_client_ip())

    attendance_session_id = ensure_attendance_session(cursor, timetable_id, date)
    cursor.execute(
        """
        SELECT attendance_id
        FROM Attendance
        WHERE student_id=? AND timetable_id=? AND attend_date=?
        """,
        (student_id, timetable_id, date),
    )
    existing = cursor.fetchone()
    cursor.execute(
        """
        INSERT INTO Attendance
            (student_id, timetable_id, session_id, attend_date, status, marked_by_user_id,
             location_status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id, timetable_id, attend_date) DO UPDATE SET
            session_id=excluded.session_id,
            status=excluded.status,
            marked_by_user_id=excluded.marked_by_user_id,
            location_status=excluded.location_status,
            updated_at=CURRENT_TIMESTAMP
        """,
        (student_id, timetable_id, attendance_session_id, date, status, marked_by_user_id, location_status),
    )
    cursor.execute(
        """
        SELECT attendance_id
        FROM Attendance
        WHERE student_id=? AND timetable_id=? AND attend_date=?
        """,
        (student_id, timetable_id, date),
    )
    saved_record = cursor.fetchone()
    log_activity(
        cursor,
        'attendance_updated' if existing else 'attendance_marked',
        'Attendance',
        saved_record['attendance_id'] if saved_record else None,
        f"Attendance set to {status} for student {student_id} on {date}.",
    )
    conn.commit()
    conn.close()
    flash('Attendance updated successfully.' if existing else 'Attendance saved successfully.', 'success')
    return redirect(url_for('attendance'))


@app.route('/teacher/workspace')
def teacher_workspace():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    requested_teacher_id = parse_int_value(request.args.get('teacher_id'), 0)
    selected_timetable_id = parse_int_value(request.args.get('timetable_id'), 0) or None
    register_from = request.args.get('register_from', today_iso())
    register_to = request.args.get('register_to', register_from)
    teacher_id = resolve_teacher_id(cursor, requested_teacher_id)

    teacher_options = []
    if not is_teacher_session():
        cursor.execute(
            '''
            SELECT teacher_id, teacher_name, email
            FROM Teachers
            ORDER BY teacher_name
            '''
        )
        teacher_options = cursor.fetchall()

    cursor.execute(
        '''
        SELECT slot_id, day_name, start_time, end_time, period_no
        FROM Time_Slots
        ORDER BY
            CASE day_name
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END,
            period_no
        '''
    )
    slots = cursor.fetchall()

    cursor.execute(
        '''
        SELECT room_id, room_name, room_type
        FROM Classrooms
        ORDER BY room_name
        '''
    )
    classrooms = cursor.fetchall()

    subject_options = []
    if teacher_id:
        cursor.execute(
            '''
            SELECT sub.subject_id, sub.subject_name, sub.subject_code, sub.type
            FROM Subjects sub
            JOIN Teachers teach ON sub.dept_id = teach.dept_id
            WHERE teach.teacher_id = ?
            ORDER BY sub.subject_name
            ''',
            (teacher_id,),
        )
        subject_options = cursor.fetchall()

    workspace = build_teacher_workspace_data(
        cursor,
        teacher_id,
        selected_timetable_id=selected_timetable_id,
        register_start=register_from,
        register_end=register_to,
    ) if teacher_id else {
        'teacher': None,
        'teacher_classes': [],
        'selected_class': None,
        'roster_metrics': [],
        'register_rows': [],
        'attendance_trend': [],
        'engagement_trend': [],
        'recent_lessons': [],
        'recommendations': [],
        'substitutions': [],
        'reminders': [],
        'activity_logs': [],
        'backup_history': [],
        'next_class': None,
        'today_classes': [],
        'average_attendance': 0,
        'average_engagement': 0,
        'session_count': 0,
        'recent_prediction_count': 0,
        'register_from': register_from,
        'register_to': register_to,
    }
    conn.close()

    focus_predictions = [row for row in workspace['roster_metrics'] if row['risk_level'] in ('high', 'medium')][:8]
    teacher_timetable_grid = build_timetable_grid(workspace['teacher_classes'])
    slots_by_day = build_slots_by_day(slots)
    period_slots = build_period_slots(slots)

    return render_template(
        'teacher_workspace.html',
        teacher_options=teacher_options,
        show_teacher_selector=not is_teacher_session(),
        can_manage_backup=session.get('role') == 'admin',
        focus_predictions=focus_predictions,
        slots=slots,
        classrooms=classrooms,
        subject_options=subject_options,
        default_academic_year=DEFAULT_ACADEMIC_YEAR,
        teacher_timetable_grid=teacher_timetable_grid,
        slots_by_day=slots_by_day,
        period_slots=period_slots,
        days=ordered_days(),
        attendance_trend_labels=[row['attend_date'] for row in workspace['attendance_trend']],
        attendance_trend_values=[row['attendance_rate'] for row in workspace['attendance_trend']],
        engagement_trend_labels=[row['engagement_date'] for row in workspace['engagement_trend']],
        engagement_trend_values=[row['engagement_rate'] for row in workspace['engagement_trend']],
        **workspace,
    )


@app.route('/teacher/timetable/add', methods=['POST'])
def add_teacher_timetable():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    teacher_id = resolve_teacher_id(cursor, parse_int_value(request.form.get('teacher_id'), 0))
    slot_id = parse_int_value(request.form.get('slot_id'), 0)
    subject_id = parse_int_value(request.form.get('subject_id'), 0)
    room_id = parse_int_value(request.form.get('room_id'), 0)
    semester = parse_int_value(request.form.get('semester'), DEFAULT_SEMESTER)
    section = request.form.get('section', DEFAULT_SECTION).strip() or DEFAULT_SECTION
    academic_year = request.form.get('academic_year', DEFAULT_ACADEMIC_YEAR).strip() or DEFAULT_ACADEMIC_YEAR

    redirect_kwargs = {'teacher_id': teacher_id or 0}
    teacher_row = None
    if teacher_id:
        cursor.execute(
            '''
            SELECT teacher_id, teacher_name, dept_id
            FROM Teachers
            WHERE teacher_id = ?
            ''',
            (teacher_id,),
        )
        teacher_row = cursor.fetchone()

    if not teacher_row:
        conn.close()
        flash('Select a valid teacher before generating a timetable period.', 'error')
        return redirect(url_for('teacher_workspace', **redirect_kwargs))

    cursor.execute(
        '''
        SELECT subject_id, subject_name
        FROM Subjects
        WHERE subject_id = ? AND dept_id = ?
        ''',
        (subject_id, teacher_row['dept_id']),
    )
    subject_row = cursor.fetchone()

    cursor.execute(
        '''
        SELECT slot_id, day_name, start_time, end_time, period_no
        FROM Time_Slots
        WHERE slot_id = ?
        ''',
        (slot_id,),
    )
    slot_row = cursor.fetchone()

    cursor.execute(
        '''
        SELECT room_id, room_name
        FROM Classrooms
        WHERE room_id = ?
        ''',
        (room_id,),
    )
    room_row = cursor.fetchone()

    if not subject_row or not slot_row or not room_row:
        conn.close()
        flash('Choose a valid subject, period, and room before generating the timetable.', 'error')
        return redirect(url_for('teacher_workspace', **redirect_kwargs))

    conflicts = timetable_conflicts(
        cursor,
        teacher_row['dept_id'],
        semester,
        section,
        slot_id,
        teacher_id,
        room_id,
    )

    if conflicts:
        conn.close()
        for message in conflicts:
            flash(message, 'error')
        return redirect(url_for('teacher_workspace', **redirect_kwargs))

    cursor.execute(
        '''
        INSERT INTO Timetable
            (dept_id, teacher_id, subject_id, room_id, slot_id, semester, section, academic_year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (teacher_row['dept_id'], teacher_id, subject_id, room_id, slot_id, semester, section, academic_year),
    )
    timetable_id = cursor.lastrowid
    log_activity(
        cursor,
        'teacher_timetable_created',
        'Timetable',
        timetable_id,
        (
            f"{teacher_row['teacher_name']} generated {subject_row['subject_name']} for "
            f"Semester {semester} Section {section} on {slot_row['day_name']} period {slot_row['period_no']}."
        ),
        json.dumps(
            {
                'teacher_id': teacher_id,
                'subject_id': subject_id,
                'slot_id': slot_id,
                'room_id': room_id,
                'semester': semester,
                'section': section,
            }
        ),
    )
    conn.commit()
    conn.close()

    flash(
        (
            f"Generated {subject_row['subject_name']} on {slot_row['day_name']} "
            f"period {slot_row['period_no']} in {room_row['room_name']}."
        ),
        'success',
    )
    return redirect(url_for('teacher_workspace', teacher_id=teacher_id, timetable_id=timetable_id))


@app.route('/teacher/timetable/update', methods=['POST'])
def update_teacher_timetable():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    teacher_id = resolve_teacher_id(cursor, parse_int_value(request.form.get('teacher_id'), 0))
    timetable_id = parse_int_value(request.form.get('timetable_id'), 0)
    slot_id = parse_int_value(request.form.get('slot_id'), 0)
    room_id = parse_int_value(request.form.get('room_id'), 0)

    cursor.execute(
        '''
        SELECT t.timetable_id, t.teacher_id, t.dept_id, t.semester, t.section,
               sub.subject_name
        FROM Timetable t
        JOIN Subjects sub ON t.subject_id = sub.subject_id
        WHERE t.timetable_id = ?
        ''',
        (timetable_id,),
    )
    timetable_row = cursor.fetchone()

    if not timetable_row:
        conn.close()
        flash('The selected timetable entry could not be found.', 'error')
        return redirect(
            url_for(
                'teacher_workspace',
                teacher_id=teacher_id or 0,
                timetable_id=timetable_id or None,
            )
        )

    redirect_kwargs = {
        'teacher_id': timetable_row['teacher_id'],
        'timetable_id': timetable_row['timetable_id'],
    }

    if is_teacher_session() and timetable_row['teacher_id'] != teacher_id:
        conn.close()
        flash('You can only update timetable periods assigned to your own teacher account.', 'error')
        return redirect(url_for('teacher_workspace', **redirect_kwargs))

    cursor.execute(
        '''
        SELECT slot_id, day_name, start_time, end_time, period_no
        FROM Time_Slots
        WHERE slot_id = ?
        ''',
        (slot_id,),
    )
    slot_row = cursor.fetchone()
    cursor.execute(
        '''
        SELECT room_id, room_name, room_type
        FROM Classrooms
        WHERE room_id = ?
        ''',
        (room_id,),
    )
    room_row = cursor.fetchone()

    if not slot_row or not room_row:
        conn.close()
        flash('Choose a valid period and room before saving the teacher timetable.', 'error')
        return redirect(url_for('teacher_workspace', **redirect_kwargs))

    conflicts = timetable_conflicts(
        cursor,
        timetable_row['dept_id'],
        timetable_row['semester'],
        timetable_row['section'],
        slot_id,
        timetable_row['teacher_id'],
        room_id,
        timetable_row['timetable_id'],
    )

    if conflicts:
        conn.close()
        for message in conflicts:
            flash(message, 'error')
        return redirect(url_for('teacher_workspace', **redirect_kwargs))

    cursor.execute(
        '''
        UPDATE Timetable
        SET slot_id = ?, room_id = ?
        WHERE timetable_id = ?
        ''',
        (slot_id, room_id, timetable_id),
    )
    log_activity(
        cursor,
        'teacher_timetable_updated',
        'Timetable',
        timetable_id,
        (
            f"{timetable_row['subject_name']} moved to {slot_row['day_name']} "
            f"period {slot_row['period_no']} in {room_row['room_name']}."
        ),
        json.dumps(
            {
                'teacher_id': timetable_row['teacher_id'],
                'slot_id': slot_id,
                'room_id': room_id,
            }
        ),
    )
    conn.commit()
    conn.close()

    flash(
        (
            f"{timetable_row['subject_name']} updated to {slot_row['day_name']} "
            f"period {slot_row['period_no']} ({slot_row['start_time']} - {slot_row['end_time']}) "
            f"in {room_row['room_name']}."
        ),
        'success',
    )
    return redirect(url_for('teacher_workspace', **redirect_kwargs))


@app.route('/teacher/predictions/refresh', methods=['POST'])
def refresh_teacher_predictions():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    teacher_id = resolve_teacher_id(cursor, parse_int_value(request.form.get('teacher_id'), 0))
    timetable_id = parse_int_value(request.form.get('timetable_id'), 0)
    workspace = build_teacher_workspace_data(cursor, teacher_id, timetable_id, today_iso(), today_iso())
    selected_class = workspace['selected_class']

    if not selected_class:
        conn.close()
        flash('Select a class before generating predictions.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0))

    cursor.execute(
        '''
        DELETE FROM Attendance_Predictions
        WHERE timetable_id = ? AND predicted_on = ?
        ''',
        (selected_class['timetable_id'], today_iso()),
    )
    cursor.execute(
        '''
        DELETE FROM Timetable_Recommendations
        WHERE timetable_id = ? AND status = 'open'
        ''',
        (selected_class['timetable_id'],),
    )

    prediction_target_date = (date.today() + timedelta(days=7)).isoformat()
    for row in workspace['roster_metrics']:
        confidence_score = round(min(98, 55 + (row['session_count'] * 4)), 1)
        cursor.execute(
            '''
            INSERT INTO Attendance_Predictions
                (student_id, timetable_id, predicted_on, predicted_for_date, predicted_percentage,
                 risk_level, confidence_score, recommendation, model_version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''',
            (
                row['student_id'],
                selected_class['timetable_id'],
                today_iso(),
                prediction_target_date,
                row['predicted_percentage'],
                row['risk_level'],
                confidence_score,
                row['recommendation'],
                'teacher-ai-v1',
            ),
        )

    for recommendation in workspace['recommendations'][:6]:
        cursor.execute(
            '''
            INSERT INTO Timetable_Recommendations
                (dept_id, semester, section, timetable_id, recommendation_type, priority, details, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'open', CURRENT_TIMESTAMP)
            ''',
            (
                selected_class['dept_id'],
                selected_class['semester'],
                selected_class['section'],
                selected_class['timetable_id'],
                recommendation['type'],
                recommendation['priority'],
                recommendation['details'],
            ),
        )

    log_activity(
        cursor,
        'prediction_refresh',
        'Attendance_Predictions',
        selected_class['timetable_id'],
        f"Teacher prediction model refreshed for {selected_class['subject_name']} ({selected_class['section']}).",
        json.dumps({'timetable_id': selected_class['timetable_id']}),
    )
    conn.commit()
    conn.close()

    flash('Prediction model refreshed and recommendations stored.', 'success')
    return redirect(
        url_for(
            'teacher_workspace',
            teacher_id=teacher_id or 0,
            timetable_id=selected_class['timetable_id'],
            register_from=today_iso(),
            register_to=today_iso(),
        )
    )


@app.route('/teacher/attendance/bulk', methods=['POST'])
def bulk_mark_teacher_attendance():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    teacher_id = resolve_teacher_id(cursor, parse_int_value(request.form.get('teacher_id'), 0))
    timetable_id = parse_int_value(request.form.get('timetable_id'), 0)
    attendance_date = request.form.get('attendance_date', today_iso())
    teacher_classes = fetch_teacher_classes(cursor, teacher_id) if teacher_id else []
    selected_class = next((row for row in teacher_classes if row['timetable_id'] == timetable_id), None)

    if not selected_class:
        conn.close()
        flash('The selected class is not available for this teacher.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0))

    cursor.execute(
        '''
        SELECT student_id, student_name, roll_no
        FROM Students
        WHERE dept_id = ? AND semester = ? AND section = ?
        ORDER BY roll_no
        ''',
        (selected_class['dept_id'], selected_class['semester'], selected_class['section']),
    )
    roster = cursor.fetchall()
    attendance_session_id = ensure_attendance_session(cursor, timetable_id, attendance_date)
    user_id = get_current_user_id(cursor)
    location_status = evaluate_location_status(get_client_ip())
    updated_count = 0

    for student in roster:
        status = request.form.get(f"status_{student['student_id']}", 'Present')
        participation_score = max(0, min(100, parse_int_value(request.form.get(f"participation_{student['student_id']}"), 70)))
        attention_score = max(0, min(100, parse_int_value(request.form.get(f"attention_{student['student_id']}"), 70)))
        remark = request.form.get(f"remark_{student['student_id']}", '').strip()
        attendance_score = 100 if status == 'Present' else 0
        engagement_score = round((attendance_score * 0.5) + (participation_score * 0.25) + (attention_score * 0.25), 1)

        cursor.execute(
            '''
            INSERT INTO Attendance
                (student_id, timetable_id, session_id, attend_date, status, marked_by_user_id,
                 location_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, timetable_id, attend_date) DO UPDATE SET
                session_id=excluded.session_id,
                status=excluded.status,
                marked_by_user_id=excluded.marked_by_user_id,
                location_status=excluded.location_status,
                updated_at=CURRENT_TIMESTAMP
            ''',
            (
                student['student_id'],
                timetable_id,
                attendance_session_id,
                attendance_date,
                status,
                user_id,
                location_status,
            ),
        )
        cursor.execute(
            '''
            INSERT INTO Student_Engagement
                (student_id, timetable_id, session_id, engagement_date, attendance_score,
                 participation_score, attention_score, engagement_score, remark,
                 recorded_by_user_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, timetable_id, engagement_date) DO UPDATE SET
                session_id=excluded.session_id,
                attendance_score=excluded.attendance_score,
                participation_score=excluded.participation_score,
                attention_score=excluded.attention_score,
                engagement_score=excluded.engagement_score,
                remark=excluded.remark,
                recorded_by_user_id=excluded.recorded_by_user_id,
                created_at=CURRENT_TIMESTAMP
            ''',
            (
                student['student_id'],
                timetable_id,
                attendance_session_id,
                attendance_date,
                attendance_score,
                participation_score,
                attention_score,
                engagement_score,
                remark,
                user_id,
            ),
        )
        updated_count += 1

    log_activity(
        cursor,
        'bulk_attendance_marked',
        'Attendance',
        timetable_id,
        f"Bulk attendance captured for {selected_class['subject_name']} on {attendance_date}.",
        json.dumps({'timetable_id': timetable_id, 'count': updated_count, 'location_status': location_status}),
    )
    conn.commit()
    conn.close()

    flash(f'Bulk attendance saved for {updated_count} students.', 'success')
    return redirect(
        url_for(
            'teacher_workspace',
            teacher_id=teacher_id or 0,
            timetable_id=timetable_id,
            register_from=attendance_date,
            register_to=attendance_date,
        )
    )


@app.route('/teacher/lesson', methods=['POST'])
def save_teacher_lesson():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    teacher_id = resolve_teacher_id(cursor, parse_int_value(request.form.get('teacher_id'), 0))
    timetable_id = parse_int_value(request.form.get('timetable_id'), 0)
    lesson_date = request.form.get('lesson_date', today_iso())
    teacher_classes = fetch_teacher_classes(cursor, teacher_id) if teacher_id else []
    selected_class = next((row for row in teacher_classes if row['timetable_id'] == timetable_id), None)

    if not selected_class:
        conn.close()
        flash('Select a valid class before saving lesson tracking.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0))

    attendance_session_id = ensure_attendance_session(cursor, timetable_id, lesson_date)
    user_id = get_current_user_id(cursor)
    topic_name = request.form.get('topic_name', '').strip()
    if not topic_name:
        conn.close()
        flash('Topic name is required for lesson tracking.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0, timetable_id=timetable_id))

    cursor.execute(
        '''
        INSERT INTO Lesson_Tracker
            (timetable_id, session_id, lesson_date, unit_name, topic_name, learning_outcome,
             resource_link, homework, syllabus_progress, recorded_by_user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(timetable_id, lesson_date, topic_name) DO UPDATE SET
            session_id=excluded.session_id,
            unit_name=excluded.unit_name,
            learning_outcome=excluded.learning_outcome,
            resource_link=excluded.resource_link,
            homework=excluded.homework,
            syllabus_progress=excluded.syllabus_progress,
            recorded_by_user_id=excluded.recorded_by_user_id,
            updated_at=CURRENT_TIMESTAMP
        ''',
        (
            timetable_id,
            attendance_session_id,
            lesson_date,
            request.form.get('unit_name', '').strip(),
            topic_name,
            request.form.get('learning_outcome', '').strip(),
            request.form.get('resource_link', '').strip(),
            request.form.get('homework', '').strip(),
            max(0, min(100, parse_int_value(request.form.get('syllabus_progress'), 0))),
            user_id,
        ),
    )
    log_activity(
        cursor,
        'lesson_tracked',
        'Lesson_Tracker',
        timetable_id,
        f"Lesson tracker updated for {selected_class['subject_name']} on {lesson_date}.",
        json.dumps({'topic_name': topic_name, 'lesson_date': lesson_date}),
    )
    conn.commit()
    conn.close()

    flash('Lesson tracking updated successfully.', 'success')
    return redirect(
        url_for(
            'teacher_workspace',
            teacher_id=teacher_id or 0,
            timetable_id=timetable_id,
            register_from=lesson_date,
            register_to=lesson_date,
        )
    )


@app.route('/teacher/substitute', methods=['POST'])
def assign_teacher_substitute():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    teacher_id = resolve_teacher_id(cursor, parse_int_value(request.form.get('teacher_id'), 0))
    timetable_id = parse_int_value(request.form.get('timetable_id'), 0)
    absence_date = request.form.get('absence_date', today_iso())
    reason = request.form.get('reason', '').strip() or 'Planned leave'

    target_class, substitute_row = find_available_substitute(cursor, teacher_id, timetable_id, absence_date)
    if not target_class:
        conn.close()
        flash('The selected class is not mapped to this teacher.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0))
    if not substitute_row:
        conn.close()
        flash('No free substitute teacher is available for that slot.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0, timetable_id=timetable_id))

    user_id = get_current_user_id(cursor)
    cursor.execute(
        '''
        INSERT INTO Teacher_Absences
            (teacher_id, absence_date, reason, status, replacement_needed, created_by_user_id, created_at)
        VALUES (?, ?, ?, 'planned', 1, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(teacher_id, absence_date) DO UPDATE SET
            reason=excluded.reason,
            status='planned',
            replacement_needed=1,
            created_by_user_id=excluded.created_by_user_id
        ''',
        (teacher_id, absence_date, reason, user_id),
    )
    cursor.execute(
        '''
        SELECT absence_id
        FROM Teacher_Absences
        WHERE teacher_id = ? AND absence_date = ?
        ''',
        (teacher_id, absence_date),
    )
    absence_row = cursor.fetchone()

    allocation_note = (
        f"Auto-assigned because {reason.lower()}. {substitute_row['teacher_name']} is free during the slot."
    )
    cursor.execute(
        '''
        INSERT INTO Substitute_Allocations
            (absence_id, timetable_id, allocation_date, original_teacher_id, substitute_teacher_id,
             status, note, created_by_user_id, created_at)
        VALUES (?, ?, ?, ?, ?, 'assigned', ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(timetable_id, allocation_date) DO UPDATE SET
            absence_id=excluded.absence_id,
            original_teacher_id=excluded.original_teacher_id,
            substitute_teacher_id=excluded.substitute_teacher_id,
            status='assigned',
            note=excluded.note,
            created_by_user_id=excluded.created_by_user_id
        ''',
        (
            absence_row['absence_id'] if absence_row else None,
            timetable_id,
            absence_date,
            teacher_id,
            substitute_row['teacher_id'],
            allocation_note,
            user_id,
        ),
    )
    log_activity(
        cursor,
        'substitute_assigned',
        'Substitute_Allocations',
        timetable_id,
        f"Substitute assigned for {target_class['subject_name']} on {absence_date}: {substitute_row['teacher_name']}.",
        json.dumps({'substitute_teacher_id': substitute_row['teacher_id'], 'absence_date': absence_date}),
    )
    conn.commit()
    conn.close()

    flash(f"Substitute assigned successfully to {substitute_row['teacher_name']}.", 'success')
    return redirect(
        url_for(
            'teacher_workspace',
            teacher_id=teacher_id or 0,
            timetable_id=timetable_id,
            register_from=absence_date,
            register_to=absence_date,
        )
    )


@app.route('/teacher/reminders/generate', methods=['POST'])
def generate_teacher_reminders():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect

    conn = get_connection()
    cursor = conn.cursor()
    teacher_id = resolve_teacher_id(cursor, parse_int_value(request.form.get('teacher_id'), 0))
    teacher_classes = fetch_teacher_classes(cursor, teacher_id) if teacher_id else []
    cursor.execute(
        '''
        SELECT t.teacher_id, t.teacher_name, t.email, d.dept_name
        FROM Teachers t
        JOIN Department d ON t.dept_id = d.dept_id
        WHERE t.teacher_id = ?
        ''',
        (teacher_id,),
    )
    teacher_row = cursor.fetchone()

    reminder_count = queue_teacher_reminders(cursor, teacher_row, teacher_classes)
    log_activity(
        cursor,
        'reminder_queue_updated',
        'Reminder_Queue',
        teacher_id,
        f"{reminder_count} smart reminders queued for {teacher_row['teacher_name'] if teacher_row else 'teacher'}.",
        json.dumps({'teacher_id': teacher_id, 'created': reminder_count}),
    )
    conn.commit()
    conn.close()

    flash(f'{reminder_count} reminders queued for upcoming classes.', 'success')
    return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0))


@app.route('/teacher/backup/create', methods=['POST'])
def create_database_backup():
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if session.get('role') != 'admin':
        flash('Only admin can manage backup operations.', 'error')
        return redirect(url_for('teacher_workspace'))

    teacher_id = parse_int_value(request.form.get('teacher_id'), 0)
    timetable_id = parse_int_value(request.form.get('timetable_id'), 0)
    db_path = Path(__file__).resolve().parent / 'timetable.db'
    BACKUP_DIR.mkdir(exist_ok=True)
    file_name = f"timetable_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destination = BACKUP_DIR / file_name

    conn = get_connection()
    cursor = conn.cursor()
    try:
        shutil.copy2(db_path, destination)
        cursor.execute(
            '''
            INSERT INTO Backup_History
                (file_name, file_path, backup_type, status, created_by_user_id, created_at, notes)
            VALUES (?, ?, 'manual', 'created', ?, CURRENT_TIMESTAMP, ?)
            ''',
            (
                file_name,
                str(destination),
                get_current_user_id(cursor),
                'Manual backup created from teacher intelligence workspace.',
            ),
        )
        log_activity(
            cursor,
            'backup_created',
            'Backup_History',
            cursor.lastrowid,
            f"Database backup created: {file_name}.",
            json.dumps({'file_name': file_name}),
        )
        conn.commit()
        flash('Database backup created successfully.', 'success')
    except Exception as exc:
        log_system_event(cursor, 'ERROR', 'backup.create', str(exc))
        conn.commit()
        flash('Backup creation failed. Check system logs.', 'error')
    finally:
        conn.close()

    return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0, timetable_id=timetable_id or None))


@app.route('/teacher/backup/restore/<int:backup_id>', methods=['POST'])
def restore_database_backup(backup_id):
    access_redirect = teacher_route_redirect()
    if access_redirect:
        return access_redirect
    if session.get('role') != 'admin':
        flash('Only admin can restore backups.', 'error')
        return redirect(url_for('teacher_workspace'))

    teacher_id = parse_int_value(request.form.get('teacher_id'), 0)
    timetable_id = parse_int_value(request.form.get('timetable_id'), 0)
    db_path = Path(__file__).resolve().parent / 'timetable.db'

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT backup_id, file_name, file_path
        FROM Backup_History
        WHERE backup_id = ?
        ''',
        (backup_id,),
    )
    backup_row = cursor.fetchone()
    conn.close()

    if not backup_row:
        flash('Selected backup could not be found.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0, timetable_id=timetable_id or None))

    backup_path = Path(backup_row['file_path'] or (BACKUP_DIR / backup_row['file_name'])).resolve()
    if not str(backup_path).startswith(str(BACKUP_DIR.resolve())):
        flash('Backup path validation failed.', 'error')
        return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0, timetable_id=timetable_id or None))

    BACKUP_DIR.mkdir(exist_ok=True)
    safety_backup = BACKUP_DIR / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    try:
        shutil.copy2(db_path, safety_backup)
        shutil.copy2(backup_path, db_path)
        create_tables()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE Backup_History
            SET status='restored', restored_at=CURRENT_TIMESTAMP
            WHERE backup_id = ?
            ''',
            (backup_id,),
        )
        cursor.execute(
            '''
            INSERT INTO Backup_History
                (file_name, file_path, backup_type, status, created_by_user_id, created_at, notes)
            VALUES (?, ?, 'automatic', 'created', ?, CURRENT_TIMESTAMP, ?)
            ''',
            (
                safety_backup.name,
                str(safety_backup),
                get_current_user_id(cursor),
                'Safety backup taken immediately before restore.',
            ),
        )
        log_activity(
            cursor,
            'backup_restored',
            'Backup_History',
            backup_id,
            f"Database restored from backup {backup_row['file_name']}.",
            json.dumps({'restored_backup_id': backup_id}),
        )
        conn.commit()
        conn.close()
        flash('Backup restored successfully.', 'success')
    except Exception as exc:
        conn = get_connection()
        cursor = conn.cursor()
        log_system_event(cursor, 'ERROR', 'backup.restore', str(exc))
        conn.commit()
        conn.close()
        flash('Restore failed. The current database was preserved in a safety backup.', 'error')

    return redirect(url_for('teacher_workspace', teacher_id=teacher_id or 0, timetable_id=timetable_id or None))

# ============================================
# RUN APP
# ============================================

if __name__ == '__main__':
    app.run(debug=True)
