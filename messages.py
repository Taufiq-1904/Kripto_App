from db import get_connection

def store_message(sender, receiver, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, receiver, content) VALUES (?, ?, ?)",
              (sender, receiver, content))
    conn.commit()
    conn.close()

def fetch_messages(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT id, sender, receiver, content, timestamp 
    FROM messages 
    WHERE sender=? OR receiver=? 
    ORDER BY timestamp DESC
    """, (username, username))
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_all_messages():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, sender, receiver, content, timestamp FROM messages ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_message(message_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
