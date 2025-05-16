from rasa.core.tracker_store import SQLTrackerStore
from sqlalchemy import create_engine, MetaData
from datetime import datetime
import psycopg2

class CustomSQLTrackerStore(SQLTrackerStore):
    def save_chat_message(self, user_id, session_id, sender, message):
        conn = psycopg2.connect(
            host="db.fbpgrmhqzlobmtmpprvj.supabase.co",
            port=5432,
            database="postgres",
            user="postgres",
            password="PpUxvZcvRe7yskSA"
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_queries (session_id, sender, message, created_at)
            VALUES (%s, %s, %s, %s)
        """, (session_id, sender, message, datetime.now()))
        conn.commit()
        conn.close()

    def save(self, tracker, timeout=None):
        # Call Rasa's default save method
        super().save(tracker, timeout)

        # Extract data
        user_id = tracker.sender_id
        session_id = tracker.current_session_id
        for e in tracker.events:
            if e.get("event") == "user":
                self.save_chat_message(user_id, session_id, "user", e.get("text"))
            elif e.get("event") == "bot":
                self.save_chat_message(user_id, session_id, "bot", e.get("text"))
