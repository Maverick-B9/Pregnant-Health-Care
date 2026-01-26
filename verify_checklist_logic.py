import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from dotenv import load_dotenv
load_dotenv() # Ensure env vars are loaded

from config import config_by_name
from app import create_app, mysql

def verify_checklist():
    print("Verifying Diagnostic Checklist Logic...")
    app = create_app(config_by_name['development'])
    
    with app.app_context():
        # Get a dummy user or existing user
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users LIMIT 1")
        user = cur.fetchone()
        cur.close()
        
        if not user:
            print("No users found to test with.")
            # Create a dummy user
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password_hash) VALUES ('Test User', 'test@example.com', 'hash')")
            mysql.connection.commit()
            user_id = cur.lastrowid
            cur.close()
            print(f"Created test user ID: {user_id}")
        else:
            user_id = user[0]
            print(f"Using test user ID: {user_id}")
            
        from app.models import DiagnosticChecklist
        
        # Test 1: Empty state
        progress = DiagnosticChecklist.get_user_progress(user_id)
        print(f"Initial Progress (Should be empty/partial): {progress}")
        
        # Test 2: Toggle ON
        test_name = "Hemoglobin (Hb)"
        print(f"Toggling '{test_name}' to TRUE...")
        DiagnosticChecklist.toggle_test(user_id, test_name, True)
        
        progress = DiagnosticChecklist.get_user_progress(user_id)
        if progress.get(test_name) is True:
            print("[PASS] Test marked as completed.")
        else:
            print(f"[FAIL] Test status is {progress.get(test_name)}")
            
        # Test 3: Toggle OFF
        print(f"Toggling '{test_name}' to FALSE...")
        DiagnosticChecklist.toggle_test(user_id, test_name, False)
        
        progress = DiagnosticChecklist.get_user_progress(user_id)
        if progress.get(test_name) is False: # Depending on implem, might be 0 or False
            print("[PASS] Test marked as incomplete.")
        else:
             print(f"[FAIL] Test status is {progress.get(test_name)}")

if __name__ == "__main__":
    verify_checklist()
