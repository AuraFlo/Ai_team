import sqlite3, datetime

class PoseDB:
    def __init__(self, db_path="pose_errors.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pose_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                exercise TEXT,
                timestamp TEXT,
                joint TEXT,
                angle REAL,
                error_flag INTEGER
            )
        """)
        self.conn.commit()

    def log_error(self, session_id, exercise, joint, angle, error_flag):
        ts = datetime.datetime.now().isoformat()
        self.conn.execute(
            "INSERT INTO pose_errors (session_id, exercise, timestamp, joint, angle, error_flag) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, exercise, ts, joint, angle, int(error_flag))
        )
        self.conn.commit()

    def get_session_error_rate(self, session_id, exercise):
        cur = self.conn.execute(
            "SELECT AVG(error_flag) FROM pose_errors WHERE session_id=? AND exercise=?",
            (session_id, exercise)
        )
        rate = cur.fetchone()[0]
        return (rate or 0.0) * 100
