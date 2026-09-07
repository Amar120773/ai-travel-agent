import sqlite3
import json
from logger import logger

DB_PATH = "memory.db"

def get_connection():
    """Get a database connection with appropriate timeout and threading parameters."""
    return sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT,
                preference_key TEXT,
                preference_value TEXT,
                UNIQUE(user_id, preference_key)
            )
        ''')
        conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
    finally:
        if conn:
            conn.close()

def save_preference(user_id: str, preference_key: str, preference_value: str) -> str:
    """Save a user preference to the database."""
    # Data sanitization/validation
    if not user_id or not preference_key or not preference_value:
        logger.warning(f"Attempted to save malformed preference data. ID: {user_id}, Key: {preference_key}, Value: {preference_value}")
        return "Error: Incomplete preference data provided."
        
    logger.debug(f"Attempting to save preference: {preference_key}={preference_value} for user {user_id}")
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value)
            VALUES (?, ?, ?)
        ''', (str(user_id), str(preference_key), str(preference_value)))
        conn.commit()
        logger.info(f"Successfully saved preference: {preference_key}={preference_value} for user {user_id}")
        return f"Successfully saved {preference_key} as {preference_value} for user {user_id}."
    except sqlite3.Error as e:
        logger.error(f"Database error while saving preference: {e}")
        return f"Error: Database lock or constraint violation occurred while saving."
    finally:
        if conn:
            conn.close()

def get_user_preferences(user_id: str) -> str:
    """Retrieve all preferences for a user."""
    if not user_id:
        return "No preferences found for this user."
        
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT preference_key, preference_value FROM user_preferences WHERE user_id = ?', (str(user_id),))
        rows = cursor.fetchall()
        
        if not rows:
            logger.debug(f"No preferences found for user {user_id}")
            return "No preferences found for this user."
        
        prefs = {key: value for key, value in rows}
        logger.debug(f"Retrieved preferences for user {user_id}: {prefs}")
        return json.dumps(prefs)
    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving preferences: {e}")
        return "{}"
    finally:
        if conn:
            conn.close()

init_db()
