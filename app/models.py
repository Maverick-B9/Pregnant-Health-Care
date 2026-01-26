# smart-healthcare-app/app/models.py
from flask_login import UserMixin
# from . import mysql # If you add methods that directly use mysql here

class User(UserMixin):
    def __init__(self, id, name=None, email=None, password_hash=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash # Store if fetched, useful for auth.py

    @staticmethod
    def get_by_email(email_address):
        from . import mysql # Local import for safety
        cur = mysql.connection.cursor()
        # Fetch all necessary fields, including password_hash
        cur.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email_address,))
        user_data = cur.fetchone()
        cur.close()
        if user_data:
            return User(id=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
        return None

    # get_by_id is effectively handled by load_user in __init__.py for Flask-Login
    # but can be useful for other purposes.
    @staticmethod
    def get_by_id(user_id_to_find):
        from . import mysql
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, email, password_hash FROM users WHERE id = %s", (user_id_to_find,))
        user_data = cur.fetchone()
        cur.close()
        if user_data:
            return User(id=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
        return None
        
    def __repr__(self):
        return f"<User {self.email or self.id}>"

class HealthRecord:
    CATEGORIES = {
        "Routine": [
            "Hemoglobin (Hb)", "Blood Group & Rh", "Blood Sugar (FBS/RBS/OGTT)", 
            "Thyroid Profile (TSH)", "HIV Screening", "HBsAg (Hepatitis B)", 
            "VDRL (Syphilis)", "Complete Blood Count (CBC)", "Urine Routine", "Urine Culture"
        ],
        "First Trimester": [
            "Dating Scan", "Viability Scan", "Ectopic Pregnancy Check", 
            "NT Scan", "Dual Marker Test"
        ],
        "Second Trimester": [
            "Anomaly Scan (Level-II)", "Quadruple Test"
        ],
        "Third Trimester": [
            "Growth Scan", "Doppler Ultrasound", "NST (Non-Stress Test)"
        ],
        "High Risk": [
            "Amniocentesis", "CVS (Chorionic Villus Sampling)", 
            "Fetal Echo", "TORCH Panel"
        ]
    }

    @staticmethod
    def add_record(user_id, category, test_name, value_numeric, value_text, file_path, test_date, notes):
        from . import mysql
        cur = mysql.connection.cursor()
        query = """
            INSERT INTO health_records 
            (user_id, category, test_name, value_numeric, value_text, file_path, test_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (user_id, category, test_name, value_numeric, value_text, file_path, test_date, notes))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_user_records(user_id):
        from . import mysql
        cur = mysql.connection.cursor()
        query = """
            SELECT id, category, test_name, value_numeric, value_text, file_path, test_date, notes 
            FROM health_records 
            WHERE user_id = %s 
            ORDER BY test_date DESC
        """
        cur.execute(query, (user_id,))
        rows = cur.fetchall()
        cur.close()
        
        # Structure data by category for easier template rendering
        records = {}
        for row in rows:
            cat = row[1]
            if cat not in records:
                records[cat] = []
            records[cat].append({
                'id': row[0],
                'test_name': row[2],
                'value_numeric': row[3],
                'value_text': row[4],
                'file_path': row[5],
                'test_date': row[6],
                'notes': row[7]
            })
        return records

    @staticmethod
    def get_test_history(user_id, test_name):
        from . import mysql
        cur = mysql.connection.cursor()
        query = """
            SELECT test_date, value_numeric 
            FROM health_records 
            WHERE user_id = %s AND test_name = %s AND value_numeric IS NOT NULL
            ORDER BY test_date ASC
        """
        cur.execute(query, (user_id, test_name))
        rows = cur.fetchall()
        cur.close()
        return [{'date': r[0].strftime('%Y-%m-%d'), 'value': r[1]} for r in rows]