import os
import pymysql
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def apply_migration():
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER')
    password = os.environ.get('MYSQL_PASSWORD')
    db_name = os.environ.get('MYSQL_DB', 'smart_health_db')

    print(f"Connecting to database {db_name} at {host} with user {user}...")
    
    try:
        conn = pymysql.connect(host=host, user=user, password=password, database=db_name)
        cursor = conn.cursor()
        
        # Create user_diagnostics table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_diagnostics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            test_name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            is_completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_test (user_id, test_name)
        );
        """
        cursor.execute(create_table_sql)
        print("Table 'user_diagnostics' created successfully.")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("DB Migration completed.")
        
    except Exception as e:
        print(f"Error applying migration: {e}")
        exit(1)

if __name__ == "__main__":
    apply_migration()
