import os
from dotenv import load_dotenv
import MySQLdb
import datetime

load_dotenv()

def verify_health_record_insert():
    try:
        # 1. Connect to Database
        db = MySQLdb.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            passwd=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DB")
        )
        cur = db.cursor()
        print("Connected to database.")

        # 2. Check if health_records table exists
        cur.execute("SHOW TABLES LIKE 'health_records'")
        if not cur.fetchone():
            print("ERROR: health_records table does not exist!")
            return

        # 3. Insert a dummy record
        user_id = 1 # Assuming user ID 1 exists
        category = "Routine"
        test_name = "Verification Test"
        value_numeric = 12.5
        value_text = "Normal"
        test_date = datetime.date.today()
        
        query = """
            INSERT INTO health_records 
            (user_id, category, test_name, value_numeric, value_text, test_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (user_id, category, test_name, value_numeric, value_text, test_date, "Automated Verification"))
        db.commit()
        print(f"Inserted record for User {user_id}.")

        # 4. Fetch it back
        cur.execute("SELECT * FROM health_records WHERE test_name = %s", (test_name,))
        row = cur.fetchone()
        if row:
            print(f"Verification Success! Retrieved: {row}")
            
            # Cleanup
            cur.execute("DELETE FROM health_records WHERE test_name = %s", (test_name,))
            db.commit()
            print("Cleanup complete.")
        else:
            print("Verification Failed: Could not retrieve record.")

        cur.close()
        db.close()

    except Exception as e:
        print(f"Verification Error: {e}")

if __name__ == "__main__":
    verify_health_record_insert()
