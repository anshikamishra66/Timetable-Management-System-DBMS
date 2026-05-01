import os
import sqlite3

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:
    pymysql = None
    DictCursor = None


DB_PATH = os.path.join(os.path.dirname(__file__), "timetable.db")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "timetable_app")
SCHEMA_VERSION = "2026.04.10.teacher-intelligence"

STUDENT_GENERATE_DATE = "2025-01-31"
STUDENT_GENERATE_TIME = "22:41:29"

STUDENT_RECORDS = [
    ("1NT24AD001", "ABHINAY K N",  "2024033611"),
    ("1NT24AD002", "ABHISHEK RAJU CHAVAN", "2024069218"),
    ("1NT24AD003", "ADHITHISRIEE P J", "2024024978"),
    ("1NT24AD004", "ADIT JAIN", "2024024972"),
    ("1NT24AD005", "ADITYA RAVINDRA PATIL",  "2024038584"),
    ("1NT24AD006", "ADITYA TRIPATHI", "2024025145"),
    ("1NT24AD007", "ANJALI H R",  "2024027676"),
    ("1NT24AD008", "ANJALI S CHAVAN", "2024060198"),
    ("1NT24AD009", "ANSHIKA MISHRA",  "2024109765"),
    ("1NT24AD010", "ANUSKA SINGH",  "2024036539"),
    ("1NT24AD011", "ARJUN K",  "2024025124"),
    ("1NT24AD012", "ARSHPREET KAUR",  "2024099581"),
    ("1NT24AD013", "ARVIND PATEL",  "2024109228"),
    ("1NT24AD014", "B KRUTHICK SACHIN S",  "2024047440"),
    ("1NT24AD015", "BHAGYAJYOTHI",  "2024050805"),
    ("1NT24AD016", "CHETHAN K M",  "2024034925"),
    ("1NT24AD017", "CHETHAN KUMAR S", "2024078582"),
    ("1NT24AD018", "CHINMAY V HUDEDAMANI",  "2024101118"),
    ("1NT24AD019", "DAVID KUMAR",  "2024103610"),
    ("1NT24AD020", "DHANUSHKA K",  "2024103289"),
    ("1NT24AD021", "EADA SRI VARSHITHA",  "2024103733"),
    ("1NT24AD022", "GOLLA SRI RANGA HARSHITH",  "2024102393"),
    ("1NT24AD023", "GORANTA ABHINASREE",  "2024101385"),
    ("1NT24AD024", "GOWTHAM SAI TEJ A", "2024084696"),
    ("1NT24AD025", "HARDIK",  "2024110220"),
    ("1NT24AD026", "HARISH BALESH MAVANURI", "2024088365"),
    ("1NT24AD027", "HARSHITH Y N",  "2024080561"),
    ("1NT24AD028", "HEEDA HURAIN SIDDIQUI",  "2024028994"),
    ("1NT24AD029", "JAGRITI KESARWANI",  "2024101892"),
    ("1NT24AD030", "JOEL AUSTIN SALINS",  "2024025064"),
    ("1NT24AD031", "KALEPU AKASH",  "2024100880"),
    ("1NT24AD032", "KHUSHI MURTHY",  "2024036202"),
    ("1NT24AD033", "KONKA MOKSHAGNA",  "2024080353"),
    ("1NT24AD034", "LIKHITHA A",  "2024032292"),
    ("1NT24AD035", "MAMIDI VENKATA YASWANTH REDDY",  "2024103796"),
    ("1NT24AD036", "MELINGI GIRIHAS M",  "2024096704"),
    ("1NT24AD037", "MIZBA KHANUM", "2024052803"),
    ("1NT24AD038", "MOHAMMAD AYAN",  "2024040572"),
    ("1NT24AD039", "N S SHAMIKA",  "2024087249"),
    ("1NT24AD040", "NAMRATHA V T",  "2024043104"),
    ("1NT24AD041", "PANGA KEERTHI",  "2024026008"),
    ("1NT24AD042", "PAVAN KALYAN R",  "2024109417"),
    ("1NT24AD043", "PRADWIN M R",  "2024077820"),
    ("1NT24AD044", "PRAGATHI",  "2024095614"),
    ("1NT24AD045", "PRATIK KUMAR", "2024044131"),
    ("1NT24AD046", "PREM KUMAR S",  "2024115166"),
    ("1NT24AD047", "R SANKEERTH",  "2024082375"),
    ("1NT24AD048", "RACHITA SHARMA",  "2024025591"),
    ("1NT24AD049", "RAKSHIT KHANNA",  "2024098142"),
    ("1NT24AD050", "RISHAB KASHYAP", "2024096587"),
    ("1NT24AD051", "SAHANASHREE M",  "2024043284"),
    ("1NT24AD052", "SAMEEKSHA SATYANARAYAN BHAT",  "2024083563"),
    ("1NT24AD053", "SANCHALI PARIKH",  "2024103081"),
    ("1NT24AD054", "SANTHA SATHVIKHA REDDY S", "2024098802"),
    ("1NT24AD055", "SHREYAS R", "2024042713"),
    ("1NT24AD056", "SIDDESH H", "2024025744"),
    ("1NT24AD057", "SPANDANA N R",  "2024073983"),
    ("1NT24AD058", "STAVY SANTAN FERNANDES",  "2024025126"),
    ("1NT24AD059", "SUNIL",  "2024055404"),
    ("1NT24AD060", "TANZEEM ULLA KHAN",  "2024084061"),
    ("1NT24AD061", "TARUN S VAIDYAM M",  "2024097145"),
    ("1NT24AD062", "THUNGA ANUSHA",  "2024103881"),
    ("1NT24AD063", "VIVEK H",  "2024084062"),
]

STUDENT_EMAILS = {
    "1NT24AD001": "1nt24ad001.abhinay@nmit.ac.in",
    "1NT24AD002": "1nt24ad002.abhishek@nmit.ac.in",
    "1NT24AD003": "1nt24ad003.adhithisriee@nmit.ac.in",
    "1NT24AD004": "1nt24ad004.adit@nmit.ac.in",
    "1NT24AD005": "1nt24ad005.aditya@nmit.ac.in",
    "1NT24AD006": "1nt24ad006.aditya@nmit.ac.in",
    "1NT24AD007": "1nt24ad007.anjali@nmit.ac.in",
    "1NT24AD008": "1nt24ad008.anjali@nmit.ac.in",
    "1NT24AD009": "1nt24ad009.anshika@nmit.ac.in",
    "1NT24AD010": "1nt24ad010.anuska@nmit.ac.in",
    "1NT24AD011": "1nt24ad011.arjun@nmit.ac.in",
    "1NT24AD012": "1nt24ad012.arshpreet@nmit.ac.in",
    "1NT24AD013": "1nt24ad013.arvind@nmit.ac.in",
    "1NT24AD014": "1nt24ad014.kruthick@nmit.ac.in",
    "1NT24AD015": "1nt24ad015.bhagyajyothi@nmit.ac.in",
    "1NT24AD016": "1nt24ad016.chethan@nmit.ac.in",
    "1NT24AD017": "1nt24ad017.chethan@nmit.ac.in",
    "1NT24AD018": "1nt24ad018.chinmay@nmit.ac.in",
    "1NT24AD019": "1nt24ad019.david@nmit.ac.in",
    "1NT24AD020": "1nt24ad020.dhanushka@nmit.ac.in",
    "1NT24AD021": "1nt24ad021.eada@nmit.ac.in",
    "1NT24AD022": "1nt24ad022.golla@nmit.ac.in",
    "1NT24AD023": "1nt24ad023.goranta@nmit.ac.in",
    "1NT24AD024": "1nt24ad024.gowtham@nmit.ac.in",
    "1NT24AD025": "1nt24ad025.hardik@nmit.ac.in",
    "1NT24AD026": "1nt24ad026.harish@nmit.ac.in",
    "1NT24AD027": "1nt24ad027.harshith@nmit.ac.in",
    "1NT24AD028": "1nt24ad028.heeda@nmit.ac.in",
    "1NT24AD029": "1nt24ad029.jagriti@nmit.ac.in",
    "1NT24AD030": "1nt24ad030.joel@nmit.ac.in",
    "1NT24AD031": "1nt24ad031.kalepu@nmit.ac.in",
    "1NT24AD032": "1nt24ad032.khushi@nmit.ac.in",
    "1NT24AD033": "1nt24ad033.konka@nmit.ac.in",
    "1NT24AD034": "1nt24ad034.likhitha@nmit.ac.in",
    "1NT24AD035": "1nt24ad035.mamidi@nmit.ac.in",
    "1NT24AD037": "1nt24ad037.mizba@nmit.ac.in",
    "1NT24AD038": "1nt24ad038.mohammad@nmit.ac.in",
    "1NT24AD039": "1nt24ad039.shamika@nmit.ac.in",
    "1NT24AD040": "1nt24ad040.namratha@nmit.ac.in",
    "1NT24AD041": "1nt24ad041.keerthi@nmit.ac.in",
    "1NT24AD042": "1nt24ad042.pavan@nmit.ac.in",
    "1NT24AD043": "1nt24ad043.pradwin@nmit.ac.in",
    "1NT24AD044": "1nt24ad044.pragathi@nmit.ac.in",
    "1NT24AD045": "1nt24ad045.pratik@nmit.ac.in",
    "1NT24AD046": "1nt24ad046.prem@nmit.ac.in",
    "1NT24AD047": "1nt24ad047.sankeerth@nmit.ac.in",
    "1NT24AD048": "1nt24ad048.rachita@nmit.ac.in",
    "1NT24AD049": "1nt24ad049.rakshit@nmit.ac.in",
    "1NT24AD050": "1nt24ad050.rishab@nmit.ac.in",
    "1NT24AD051": "1nt24ad051.sahanashree@nmit.ac.in",
    "1NT24AD052": "1nt24ad052.sameeksha@nmit.ac.in",
    "1NT24AD053": "1nt24ad053.sanchali@nmit.ac.in",
    "1NT24AD054": "1nt24ad054.santha@nmit.ac.in",
    "1NT24AD055": "1nt24ad055.shreyas@nmit.ac.in",
    "1NT24AD056": "1nt24ad056.siddesh@nmit.ac.in",
    "1NT24AD057": "1nt24ad057.spandana@nmit.ac.in",
    "1NT24AD058": "1nt24ad058.stavy@nmit.ac.in",
    "1NT24AD059": "1nt24ad059.sunil@nmit.ac.in",
    "1NT24AD060": "1nt24ad060.tanzeem@nmit.ac.in",
    "1NT24AD061": "1nt24ad061.tarun@nmit.ac.in",
    "1NT24AD062": "1nt24ad062.anusha@nmit.ac.in",
    "1NT24AD063": "1nt24ad063.vivek@nmit.ac.in",
}

TEACHER_RECORDS = [
    (4, "Dr. Dhananjaya Murthy", 3, "dhananjayamurthy.b@nmit.ac.in", "9843596001"),
    (5, "Mrs. Sowmya M", 3, "sowmya.m@nmit.ac.in", "9843596002"),
    (6, "Dr. Archana Mathur", 3, "archana.mathur@nmit.ac.in", "9843596003"),
    (7, "Dr. R Vadivel", 3, "vadivel.r@nmit.ac.in", "9843596004"),
    (8, "Dr. Meenakshi", 3, "meenakshi.ho.kateel@nmit.ac.in", "9843596005"),
    (9, "Dr. Lakshmana", 3, "lakshmana.b@nmit.ac.in", "9843596006"),
    (10, "Mr. R Palanivel", 3, "palanivelr@nmit.ac.in", "9843596006"),
    (11, "Dr. Govramma", 3, "govramma.t@nmit.ac.in", "9843596007"),
    (12, "Ms. Kousalya Konila", 3, "kousalya.k@nmit.ac.in", "9843596008"),
    (13, "Ms. Nisha / Ms. Amala Raghu", 3, "cdc.strainers3@nmit.ac.in", "9843596009"),
]

SUBJECT_RECORDS = [
    (4, "Applied Discrete Mathematical Structures and Graph Theory", "22MAT41A", 3, 4, "Theory"),
    (5, "Artificial Intelligence", "22ADA2", 3, 4, "Theory"),
    (6, "Machine Learning", "22AD43", 3, 4, "Theory"),
    (7, "Database Management Systems", "22ADG44", 3, 4, "Theory"),
    (8, "Machine Learning Lab", "22ADL45", 3, 2, "Lab"),
    (9, "Software Engineering and Project Management", "22ADE461", 3, 3, "Theory"),
    (10, "JAVA Programming", "22ADA472", 3, 3, "Theory"),
    (11, "Biology for Engineers", "22ADB48", 3, 2, "Theory"),
    (12, "Universal Human Values", "22UHV410", 3, 2, "Theory"),
    (13, "Samskruthika/Balike Kannada", "22K(S/B)49", 3, 1, "Theory"),
    (14, "Developing Interpersonal Skills", "22INS4A", 3, 1, "Activity"),
    (15, "Soft Skills", "22TP412B1", 3, 1, "Activity"),
    (16, "Artificial Intelligence - TTL", "22AD42", 3, 1, "Activity"),
    (17, "Term Paper", "TERM-PAPER", 3, 1, "Activity"),
    (18, "Mentoring", "MENTORING", 3, 1, "Activity"),
    (19, "Library", "LIBRARY", 3, 1, "Activity"),
    (20, "DBMS Integrated Lab", "22ADG44-LAB", 3, 2, "Lab"),
    (21, "EL/Mini Project", "EL-MINI-PROJECT", 3, 2, "Project"),
    (22, "LA/PD", "LA-PD", 3, 1, "Activity"),
]

CLASSROOM_RECORDS = [
    (3, "166 C", 70, "Classroom"),
]

TIME_SLOT_RECORDS = [
    (1, "Monday", "09:00", "09:55", 1),
    (2, "Monday", "10:05", "11:00", 2),
    (3, "Monday", "11:00", "11:55", 3),
    (4, "Monday", "12:35", "13:30", 4),
    (5, "Monday", "13:30", "14:25", 5),
    (6, "Monday", "14:25", "15:20", 6),
    (7, "Tuesday", "09:00", "09:55", 1),
    (8, "Tuesday", "10:05", "11:00", 2),
    (9, "Tuesday", "11:00", "11:55", 3),
    (10, "Tuesday", "12:35", "13:30", 4),
    (11, "Tuesday", "13:30", "14:25", 5),
    (12, "Tuesday", "14:25", "15:20", 6),
    (13, "Wednesday", "09:00", "09:55", 1),
    (14, "Wednesday", "10:05", "11:00", 2),
    (15, "Wednesday", "11:00", "11:55", 3),
    (16, "Wednesday", "12:35", "13:30", 4),
    (17, "Wednesday", "13:30", "14:25", 5),
    (18, "Wednesday", "14:25", "15:20", 6),
    (19, "Thursday", "09:00", "09:55", 1),
    (20, "Thursday", "10:05", "11:00", 2),
    (21, "Thursday", "11:00", "11:55", 3),
    (22, "Thursday", "12:35", "13:30", 4),
    (23, "Thursday", "13:30", "14:25", 5),
    (24, "Thursday", "14:25", "15:20", 6),
    (25, "Friday", "09:00", "09:55", 1),
    (26, "Friday", "10:05", "11:00", 2),
    (27, "Friday", "11:00", "11:55", 3),
    (28, "Friday", "12:35", "13:30", 4),
    (29, "Friday", "13:30", "14:25", 5),
    (30, "Friday", "14:25", "15:20", 6),
    (31, "Saturday", "09:00", "09:55", 1),
    (32, "Saturday", "10:05", "11:00", 2),
    (33, "Saturday", "11:00", "11:55", 3),
    (34, "Saturday", "12:35", "13:30", 4),
    (35, "Saturday", "13:30", "14:25", 5),
    (36, "Saturday", "14:25", "15:20", 6),
]

TIMETABLE_RECORDS = [
    (1, 3, 6, 6, 3, 1, 4, "A", "2026-2027"),
    (2, 3, 4, 4, 3, 2, 4, "A", "2026-2027"),
    (3, 3, 9, 9, 3, 3, 4, "A", "2026-2027"),
    (4, 3, 8, 8, 3, 4, 4, "A", "2025-2026"),
    (5, 3, 13, 15, 3, 6, 4, "A", "2025-2026"),
    (6, 3, 5, 5, 3, 7, 4, "A", "2025-2026"),
    (7, 3, 6, 6, 3, 8, 4, "A", "2025-2026"),
    (8, 3, 7, 7, 3, 9, 4, "A", "2025-2026"),
    (9, 3, 8, 8, 3, 10, 4, "A", "2025-2026"),
    (10, 3, 11, 13, 3, 11, 4, "A", "2025-2026"),
    (11, 3, 10, 17, 3, 12, 4, "A", "2025-2026"),
    (12, 3, 7, 7, 3, 13, 4, "A", "2025-2026"),
    (13, 3, 5, 5, 3, 14, 4, "A", "2025-2026"),
    (14, 3, 4, 4, 3, 15, 4, "A", "2025-2026"),
    (15, 3, 5, 10, 3, 16, 4, "A", "2025-2026"),
    (16, 3, 11, 13, 3, 17, 4, "A", "2025-2026"),
    (17, 3, 10, 18, 3, 18, 4, "A", "2025-2026"),
    (18, 3, 4, 4, 3, 19, 4, "A", "2025-2026"),
    (19, 3, 7, 7, 3, 20, 4, "A", "2025-2026"),
    (20, 3, 6, 6, 3, 21, 4, "A", "2025-2026"),
    (21, 3, 9, 9, 3, 22, 4, "A", "2025-2026"),
    (22, 3, 5, 10, 3, 23, 4, "A", "2025-2026"),
    (23, 3, 10, 19, 3, 24, 4, "A", "2025-2026"),
    (24, 3, 8, 11, 3, 25, 4, "A", "2025-2026"),
    (25, 3, 9, 9, 3, 26, 4, "A", "2025-2026"),
    (26, 3, 5, 5, 3, 27, 4, "A", "2025-2026"),
    (27, 3, 4, 4, 3, 28, 4, "A", "2025-2026"),
    (28, 3, 7, 20, 3, 29, 4, "A", "2025-2026"),
    (29, 3, 12, 14, 3, 30, 4, "A", "2025-2026"),
    (30, 3, 10, 12, 3, 31, 4, "A", "2025-2026"),
    (31, 3, 10, 16, 3, 32, 4, "A", "2025-2026"),
    (32, 3, 10, 21, 3, 34, 4, "A", "2025-2026"),
    (33, 3, 10, 22, 3, 35, 4, "A", "2025-2026"),
]

ROLE_PERMISSION_RECORDS = [
    ("admin", "manage_dashboard", "View admin dashboard cards and previews", 1),
    ("admin", "manage_timetable", "Create, update, and delete timetable slots", 1),
    ("admin", "manage_teachers", "Maintain teacher master data", 1),
    ("admin", "manage_students", "Maintain student master data", 1),
    ("admin", "mark_attendance", "Record and update attendance for any student", 1),
    ("admin", "view_analytics", "Open attendance insights and predictions", 1),
    ("admin", "manage_substitutions", "Plan leave and substitute faculty allocation", 1),
    ("admin", "manage_backups", "Create and restore database backups", 1),
    ("admin", "view_logs", "Inspect audit and system logs", 1),
    ("teacher", "view_timetable", "Read timetable for assigned classes", 1),
    ("teacher", "mark_attendance", "Mark and revise attendance", 1),
    ("teacher", "update_lessons", "Track lessons and syllabus progress", 1),
    ("teacher", "manage_engagement", "Record participation and engagement", 1),
    ("teacher", "view_analytics", "See attendance trends and alerts", 1),
    ("student", "view_timetable", "Open the personal timetable", 1),
    ("student", "view_attendance", "Open personal attendance history", 1),
    ("student", "view_profile", "Open the student profile page", 1),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def mysql_users_enabled():
    return bool(MYSQL_HOST and MYSQL_USER and pymysql)


def get_users_connection():
    if mysql_users_enabled():
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            cursorclass=DictCursor,
            autocommit=False,
        )
    return get_connection()


def ensure_users_table():
    conn = get_users_connection()
    try:
        cursor = conn.cursor()
        if mysql_users_enabled():
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    google_id VARCHAR(255) UNIQUE,
                    role VARCHAR(50) DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Users (
                    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    username    TEXT UNIQUE,
                    password    TEXT,
                    role        TEXT DEFAULT 'admin',
                    email       TEXT UNIQUE,
                    name        TEXT,
                    google_id   TEXT UNIQUE,
                    auth_provider TEXT DEFAULT 'local',
                    is_active   INTEGER DEFAULT 1,
                    last_login_at TEXT,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            _ensure_column(cursor, "Users", "email", "TEXT")
            _ensure_column(cursor, "Users", "name", "TEXT")
            _ensure_column(cursor, "Users", "google_id", "TEXT")
            _ensure_column(cursor, "Users", "auth_provider", "TEXT DEFAULT 'local'")
            _ensure_column(cursor, "Users", "is_active", "INTEGER DEFAULT 1")
            _ensure_column(cursor, "Users", "last_login_at", "TEXT")
            _ensure_column(cursor, "Users", "created_at", "TEXT")
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_users_connection()
    try:
        cursor = conn.cursor()
        if mysql_users_enabled():
            cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        else:
            cursor.execute("SELECT * FROM Users WHERE email=?", (email,))
        return cursor.fetchone()
    finally:
        conn.close()


def upsert_google_user(email, name, google_id, role):
    conn = get_users_connection()
    try:
        cursor = conn.cursor()
        if mysql_users_enabled():
            cursor.execute(
                """
                INSERT INTO Users (email, name, google_id, role)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name=VALUES(name),
                    google_id=VALUES(google_id),
                    role=VALUES(role)
                """,
                (email, name, google_id, role),
            )
            cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        else:
            cursor.execute("SELECT user_id FROM Users WHERE email=?", (email,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    """
                    UPDATE Users
                    SET name=?, google_id=?, role=?, username=?, auth_provider=?, last_login_at=CURRENT_TIMESTAMP
                    WHERE email=?
                    """,
                    (name, google_id, role, email, "google", email),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO Users (email, name, google_id, role, username, password, auth_provider, last_login_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (email, name, google_id, role, email, "google-oauth", "google"),
                )
            cursor.execute(
                "SELECT * FROM Users WHERE email=?",
                (email,),
            )
        conn.commit()
        return cursor.fetchone()
    finally:
        conn.close()


def get_student_by_email(email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Students WHERE LOWER(email)=LOWER(?)", (email,))
        return cursor.fetchone()
    finally:
        conn.close()


def _ensure_column(cursor, table_name, column_name, definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row["name"] for row in cursor.fetchall()}
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def _ensure_columns(cursor, table_name, definitions):
    for column_name, definition in definitions.items():
        _ensure_column(cursor, table_name, column_name, definition)


def _index_exists(cursor, index_name):
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?",
        (index_name,),
    )
    return cursor.fetchone() is not None


def _ensure_index(cursor, index_name, table_name, columns, unique=False):
    if _index_exists(cursor, index_name):
        return True

    column_sql = ", ".join(columns)
    if unique:
        cursor.execute(
            f"""
            SELECT {column_sql}, COUNT(*) AS row_count
            FROM {table_name}
            GROUP BY {column_sql}
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
        if cursor.fetchone():
            return False

    unique_sql = "UNIQUE " if unique else ""
    cursor.execute(
        f"CREATE {unique_sql}INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_sql})"
    )
    return True


def _ensure_feature_tables(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS App_Metadata (
            meta_key    TEXT PRIMARY KEY,
            meta_value  TEXT NOT NULL,
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Role_Permissions (
            role_name      TEXT NOT NULL,
            permission_key TEXT NOT NULL,
            description    TEXT,
            is_allowed     INTEGER DEFAULT 1,
            PRIMARY KEY (role_name, permission_key)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Student_Engagement (
            engagement_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id         INTEGER NOT NULL,
            timetable_id       INTEGER,
            session_id         INTEGER,
            engagement_date    TEXT NOT NULL,
            attendance_score   REAL DEFAULT 0,
            participation_score REAL DEFAULT 0,
            attention_score    REAL DEFAULT 0,
            engagement_score   REAL DEFAULT 0,
            remark             TEXT,
            recorded_by_user_id INTEGER,
            created_at         TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id),
            FOREIGN KEY (session_id) REFERENCES Attendance_Sessions(session_id),
            FOREIGN KEY (recorded_by_user_id) REFERENCES Users(user_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Attendance_Predictions (
            prediction_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id            INTEGER NOT NULL,
            timetable_id          INTEGER,
            predicted_on          TEXT NOT NULL,
            predicted_for_date    TEXT NOT NULL,
            predicted_percentage  REAL NOT NULL,
            risk_level            TEXT NOT NULL,
            confidence_score      REAL,
            recommendation        TEXT,
            model_version         TEXT,
            created_at            TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Teacher_Absences (
            absence_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id          INTEGER NOT NULL,
            absence_date        TEXT NOT NULL,
            reason              TEXT,
            status              TEXT DEFAULT 'planned',
            replacement_needed  INTEGER DEFAULT 1,
            created_by_user_id  INTEGER,
            created_at          TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
            FOREIGN KEY (created_by_user_id) REFERENCES Users(user_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Substitute_Allocations (
            allocation_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            absence_id            INTEGER,
            timetable_id          INTEGER NOT NULL,
            allocation_date       TEXT NOT NULL,
            original_teacher_id   INTEGER,
            substitute_teacher_id INTEGER NOT NULL,
            status                TEXT DEFAULT 'assigned',
            note                  TEXT,
            created_by_user_id    INTEGER,
            created_at            TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (absence_id) REFERENCES Teacher_Absences(absence_id),
            FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id),
            FOREIGN KEY (original_teacher_id) REFERENCES Teachers(teacher_id),
            FOREIGN KEY (substitute_teacher_id) REFERENCES Teachers(teacher_id),
            FOREIGN KEY (created_by_user_id) REFERENCES Users(user_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Reminder_Queue (
            reminder_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            timetable_id    INTEGER,
            session_id      INTEGER,
            remind_at       TEXT NOT NULL,
            target_role     TEXT DEFAULT 'teacher',
            target_user_id  INTEGER,
            channel         TEXT DEFAULT 'in_app',
            status          TEXT DEFAULT 'pending',
            message         TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
            sent_at         TEXT,
            FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id),
            FOREIGN KEY (session_id) REFERENCES Attendance_Sessions(session_id),
            FOREIGN KEY (target_user_id) REFERENCES Users(user_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Lesson_Tracker (
            lesson_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timetable_id         INTEGER NOT NULL,
            session_id           INTEGER,
            lesson_date          TEXT NOT NULL,
            unit_name            TEXT,
            topic_name           TEXT NOT NULL,
            learning_outcome     TEXT,
            resource_link        TEXT,
            homework             TEXT,
            syllabus_progress    REAL DEFAULT 0,
            recorded_by_user_id  INTEGER,
            created_at           TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at           TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id),
            FOREIGN KEY (session_id) REFERENCES Attendance_Sessions(session_id),
            FOREIGN KEY (recorded_by_user_id) REFERENCES Users(user_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Timetable_Recommendations (
            recommendation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_id             INTEGER,
            semester            INTEGER,
            section             TEXT,
            timetable_id        INTEGER,
            recommendation_type TEXT NOT NULL,
            priority            TEXT DEFAULT 'medium',
            details             TEXT NOT NULL,
            status              TEXT DEFAULT 'open',
            created_at          TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at         TEXT,
            FOREIGN KEY (dept_id) REFERENCES Department(dept_id),
            FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Activity_Log (
            log_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER,
            actor_email    TEXT,
            action_type    TEXT NOT NULL,
            entity_type    TEXT NOT NULL,
            entity_id      INTEGER,
            description    TEXT,
            ip_address     TEXT,
            metadata_json  TEXT,
            created_at     TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS System_Log (
            system_log_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            log_level      TEXT NOT NULL,
            source         TEXT NOT NULL,
            message        TEXT NOT NULL,
            stack_trace    TEXT,
            created_at     TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Backup_History (
            backup_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name           TEXT NOT NULL,
            file_path           TEXT,
            backup_type         TEXT DEFAULT 'manual',
            status              TEXT DEFAULT 'created',
            created_by_user_id  INTEGER,
            created_at          TEXT DEFAULT CURRENT_TIMESTAMP,
            restored_at         TEXT,
            notes               TEXT,
            FOREIGN KEY (created_by_user_id) REFERENCES Users(user_id)
        )
        """
    )


def _ensure_feature_columns(cursor):
    _ensure_columns(
        cursor,
        "Users",
        {
            "email": "TEXT",
            "name": "TEXT",
            "google_id": "TEXT",
            "auth_provider": "TEXT DEFAULT 'local'",
            "is_active": "INTEGER DEFAULT 1",
            "last_login_at": "TEXT",
            "created_at": "TEXT",
        },
    )
    _ensure_columns(
        cursor,
        "Teachers",
        {
            "employee_code": "TEXT",
            "specialization": "TEXT",
            "is_active": "INTEGER DEFAULT 1",
            "availability_status": "TEXT DEFAULT 'available'",
        },
    )
    _ensure_columns(
        cursor,
        "Subjects",
        {
            "attendance_threshold": "REAL DEFAULT 75",
            "total_hours": "INTEGER",
            "is_active": "INTEGER DEFAULT 1",
        },
    )
    _ensure_columns(
        cursor,
        "Timetable",
        {
            "is_active": "INTEGER DEFAULT 1",
            "delivery_mode": "TEXT DEFAULT 'offline'",
        },
    )
    _ensure_columns(
        cursor,
        "Students",
        {
            "father_name": "TEXT",
            "admission_id": "TEXT",
            "generate_date": "TEXT",
            "generate_time": "TEXT",
            "guardian_phone": "TEXT",
            "is_active": "INTEGER DEFAULT 1",
        },
    )
    _ensure_columns(
        cursor,
        "Attendance",
        {
            "session_id": "INTEGER",
            "marked_by_user_id": "INTEGER",
            "participation_score": "REAL DEFAULT 0",
            "remarks": "TEXT",
            "location_status": "TEXT DEFAULT 'not_checked'",
            "created_at": "TEXT",
            "updated_at": "TEXT",
        },
    )


def _ensure_feature_indexes(cursor):
    _ensure_index(cursor, "idx_teachers_dept_id", "Teachers", ["dept_id"])
    _ensure_index(cursor, "idx_subjects_dept_id", "Subjects", ["dept_id"])
    _ensure_index(cursor, "idx_students_dept_sem_section", "Students", ["dept_id", "semester", "section"])
    _ensure_index(cursor, "idx_students_email", "Students", ["email"])
    _ensure_index(cursor, "idx_timetable_lookup", "Timetable", ["dept_id", "semester", "section"])
    _ensure_index(cursor, "idx_timetable_teacher_slot", "Timetable", ["teacher_id", "slot_id"])
    _ensure_index(cursor, "idx_timetable_room_slot", "Timetable", ["room_id", "slot_id"])
    _ensure_index(cursor, "idx_attendance_student_date", "Attendance", ["student_id", "attend_date"])
    _ensure_index(cursor, "idx_attendance_timetable_date", "Attendance", ["timetable_id", "attend_date"])
    _ensure_index(cursor, "idx_activity_log_entity", "Activity_Log", ["entity_type", "entity_id"])
    _ensure_index(cursor, "idx_activity_log_created_at", "Activity_Log", ["created_at"])
    _ensure_index(cursor, "idx_engagement_student_date", "Student_Engagement", ["student_id", "engagement_date"])
    _ensure_index(cursor, "idx_predictions_student_date", "Attendance_Predictions", ["student_id", "predicted_for_date"])
    _ensure_index(cursor, "idx_absence_teacher_date", "Teacher_Absences", ["teacher_id", "absence_date"])
    _ensure_index(cursor, "idx_reminder_status_time", "Reminder_Queue", ["status", "remind_at"])
    _ensure_index(cursor, "idx_recommendation_status_priority", "Timetable_Recommendations", ["status", "priority"])
    _ensure_index(cursor, "uq_time_slots_day_period", "Time_Slots", ["day_name", "period_no"], unique=True)
    _ensure_index(cursor, "uq_timetable_slot", "Timetable", ["dept_id", "semester", "section", "slot_id"], unique=True)
    _ensure_index(cursor, "uq_attendance_record", "Attendance", ["student_id", "timetable_id", "attend_date"], unique=True)
    _ensure_index(cursor, "uq_attendance_session", "Attendance_Sessions", ["timetable_id", "session_date"], unique=True)
    _ensure_index(cursor, "uq_engagement_record", "Student_Engagement", ["student_id", "timetable_id", "engagement_date"], unique=True)
    _ensure_index(cursor, "uq_prediction_record", "Attendance_Predictions", ["student_id", "timetable_id", "predicted_for_date"], unique=True)
    _ensure_index(cursor, "uq_teacher_absence", "Teacher_Absences", ["teacher_id", "absence_date"], unique=True)
    _ensure_index(cursor, "uq_substitute_allocation", "Substitute_Allocations", ["timetable_id", "allocation_date"], unique=True)
    _ensure_index(cursor, "uq_lesson_tracker", "Lesson_Tracker", ["timetable_id", "lesson_date", "topic_name"], unique=True)


def _seed_role_permissions(cursor):
    for permission in ROLE_PERMISSION_RECORDS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO Role_Permissions
                (role_name, permission_key, description, is_allowed)
            VALUES (?, ?, ?, ?)
            """,
            permission,
        )


def create_tables():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        ensure_users_table()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username       TEXT UNIQUE NOT NULL,
                password       TEXT NOT NULL,
                role           TEXT DEFAULT 'admin',
                email          TEXT UNIQUE,
                name           TEXT,
                google_id      TEXT UNIQUE,
                auth_provider  TEXT DEFAULT 'local',
                is_active      INTEGER DEFAULT 1,
                last_login_at  TEXT,
                created_at     TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Department (
                dept_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                dept_name TEXT NOT NULL,
                hod_name  TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Teachers (
                teacher_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name        TEXT NOT NULL,
                dept_id             INTEGER,
                email               TEXT,
                contact_no          TEXT,
                employee_code       TEXT,
                specialization      TEXT,
                is_active           INTEGER DEFAULT 1,
                availability_status TEXT DEFAULT 'available',
                FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Subjects (
                subject_id            INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name          TEXT NOT NULL,
                subject_code          TEXT UNIQUE,
                dept_id               INTEGER,
                credits               INTEGER,
                type                  TEXT,
                attendance_threshold  REAL DEFAULT 75,
                total_hours           INTEGER,
                is_active             INTEGER DEFAULT 1,
                FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Classrooms (
                room_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT,
                capacity  INTEGER,
                room_type TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Time_Slots (
                slot_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                day_name   TEXT,
                start_time TEXT,
                end_time   TEXT,
                period_no  INTEGER
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Timetable (
                timetable_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                dept_id       INTEGER,
                teacher_id    INTEGER,
                subject_id    INTEGER,
                room_id       INTEGER,
                slot_id       INTEGER,
                semester      INTEGER,
                section       TEXT,
                academic_year TEXT,
                is_active     INTEGER DEFAULT 1,
                delivery_mode TEXT DEFAULT 'offline',
                FOREIGN KEY (dept_id)    REFERENCES Department(dept_id),
                FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
                FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id),
                FOREIGN KEY (room_id)    REFERENCES Classrooms(room_id),
                FOREIGN KEY (slot_id)    REFERENCES Time_Slots(slot_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Attendance_Sessions (
                session_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timetable_id       INTEGER NOT NULL,
                session_date       TEXT NOT NULL,
                room_id            INTEGER,
                topic_covered      TEXT,
                syllabus_progress  REAL DEFAULT 0,
                attendance_mode    TEXT DEFAULT 'manual',
                location_required  INTEGER DEFAULT 0,
                location_latitude  REAL,
                location_longitude REAL,
                ip_address         TEXT,
                notes              TEXT,
                marked_by_user_id  INTEGER,
                created_at         TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at         TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id),
                FOREIGN KEY (room_id) REFERENCES Classrooms(room_id),
                FOREIGN KEY (marked_by_user_id) REFERENCES Users(user_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Students (
                student_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name   TEXT NOT NULL,
                roll_no        TEXT UNIQUE,
                dept_id        INTEGER,
                semester       INTEGER,
                section        TEXT,
                email          TEXT,
                father_name    TEXT,
                admission_id   TEXT,
                generate_date  TEXT,
                generate_time  TEXT,
                guardian_phone TEXT,
                is_active      INTEGER DEFAULT 1,
                FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id    INTEGER,
                timetable_id  INTEGER,
                session_id    INTEGER,
                attend_date   TEXT,
                status        TEXT,
                marked_by_user_id INTEGER,
                participation_score REAL DEFAULT 0,
                remarks       TEXT,
                location_status TEXT DEFAULT 'not_checked',
                created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at    TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id)   REFERENCES Students(student_id),
                FOREIGN KEY (timetable_id) REFERENCES Timetable(timetable_id),
                FOREIGN KEY (session_id) REFERENCES Attendance_Sessions(session_id),
                FOREIGN KEY (marked_by_user_id) REFERENCES Users(user_id)
            )
            """
        )

        _ensure_feature_tables(cursor)
        _ensure_feature_columns(cursor)
        _ensure_feature_indexes(cursor)
        _seed_role_permissions(cursor)
        cursor.execute(
            """
            INSERT INTO App_Metadata (meta_key, meta_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(meta_key) DO UPDATE SET
                meta_value=excluded.meta_value,
                updated_at=CURRENT_TIMESTAMP
            """,
            ("schema_version", SCHEMA_VERSION),
        )

        cursor.execute(
            "INSERT OR IGNORE INTO Users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin"),
        )

        departments = [
            (1, "Computer Science and Engineering", "Dr. Ramesh Kumar"),
            (2, "Information Technology", "Dr. Priya Sharma"),
            (3, "Artificial Intelligence and Data Science", "Dr. Lakshmana"),
        ]
        for dept in departments:
            cursor.execute(
                "INSERT OR IGNORE INTO Department (dept_id, dept_name, hod_name) VALUES (?, ?, ?)",
                dept,
            )

        for teacher in TEACHER_RECORDS:
            cursor.execute(
                """
                INSERT INTO Teachers (teacher_id, teacher_name, dept_id, email, contact_no)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(teacher_id) DO UPDATE SET
                    teacher_name=excluded.teacher_name,
                    dept_id=excluded.dept_id,
                    email=excluded.email,
                    contact_no=excluded.contact_no
                """,
                teacher,
            )

        for _, teacher_name, _, email, contact_no in TEACHER_RECORDS:
            teacher_password = (contact_no or "teach123")[-4:]
            cursor.execute(
                """
                INSERT INTO Users (username, password, role, email, name)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    password=excluded.password,
                    role=excluded.role,
                    email=excluded.email,
                    name=excluded.name
                """,
                (email, teacher_password, "teacher", email, teacher_name),
            )

        for subject in SUBJECT_RECORDS:
            cursor.execute(
                """
                INSERT INTO Subjects (subject_id, subject_name, subject_code, dept_id, credits, type)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(subject_id) DO UPDATE SET
                    subject_name=excluded.subject_name,
                    subject_code=excluded.subject_code,
                    dept_id=excluded.dept_id,
                    credits=excluded.credits,
                    type=excluded.type
                """,
                subject,
            )

        for classroom in CLASSROOM_RECORDS:
            cursor.execute(
                """
                INSERT INTO Classrooms (room_id, room_name, capacity, room_type)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(room_id) DO UPDATE SET
                    room_name=excluded.room_name,
                    capacity=excluded.capacity,
                    room_type=excluded.room_type
                """,
                classroom,
            )

        for time_slot in TIME_SLOT_RECORDS:
            cursor.execute(
                """
                INSERT INTO Time_Slots (slot_id, day_name, start_time, end_time, period_no)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(slot_id) DO UPDATE SET
                    day_name=excluded.day_name,
                    start_time=excluded.start_time,
                    end_time=excluded.end_time,
                    period_no=excluded.period_no
                """,
                time_slot,
            )

        for timetable in TIMETABLE_RECORDS:
            cursor.execute("SELECT timetable_id FROM Timetable WHERE timetable_id = ?", (timetable[0],))
            existing_timetable = cursor.fetchone()
            if existing_timetable:
                cursor.execute(
                    """
                    UPDATE Timetable
                    SET dept_id=?,
                        teacher_id=?,
                        subject_id=?,
                        room_id=?,
                        slot_id=?,
                        semester=?,
                        section=?,
                        academic_year=?
                    WHERE timetable_id=?
                      AND NOT EXISTS (
                          SELECT 1
                          FROM Timetable
                          WHERE dept_id=?
                            AND semester=?
                            AND section=?
                            AND slot_id=?
                            AND timetable_id<>?
                      )
                    """,
                    (
                        timetable[1], timetable[2], timetable[3], timetable[4], timetable[5],
                        timetable[6], timetable[7], timetable[8], timetable[0],
                        timetable[1], timetable[6], timetable[7], timetable[5], timetable[0],
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO Timetable
                        (timetable_id, dept_id, teacher_id, subject_id, room_id, slot_id, semester, section, academic_year)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    timetable,
                )

        for student_id, student_record in enumerate(STUDENT_RECORDS, start=1):
            if len(student_record) == 4:
                usn, name, _father_name, admission_id = student_record
            elif len(student_record) == 3:
                usn, name, admission_id = student_record
            else:
                raise ValueError(f"Invalid student record at position {student_id}: {student_record!r}")

            cursor.execute(
                """
                INSERT INTO Students
                    (student_id, student_name, roll_no, dept_id, semester, section, email,
                     father_name, admission_id, generate_date, generate_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(roll_no) DO UPDATE SET
                    student_name=excluded.student_name,
                    dept_id=excluded.dept_id,
                    semester=excluded.semester,
                    section=excluded.section,
                    email=excluded.email,
                    father_name=excluded.father_name,
                    admission_id=excluded.admission_id,
                    generate_date=excluded.generate_date,
                    generate_time=excluded.generate_time
                """,
                (
                    student_id,
                    name,
                    usn,
                    3,
                    4,
                    "A",
                    STUDENT_EMAILS.get(usn, f"{usn.lower()}@nmit.ac.in"),
                    None,
                    admission_id,
                    STUDENT_GENERATE_DATE,
                    STUDENT_GENERATE_TIME,
                ),
            )

        for student_record in STUDENT_RECORDS:
            usn = student_record[0]
            cursor.execute(
                "INSERT OR IGNORE INTO Users (username, password, role) VALUES (?, ?, ?)",
                (usn, usn[-3:], "student"),
            )

        conn.commit()
        print("Database ready!")
    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
