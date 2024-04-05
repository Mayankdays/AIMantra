import sqlite3

def get_pdf_link(user_input):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT chapter_link FROM combined_cbse_data WHERE chapter_name LIKE ?", (f"%{user_input}%",))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return None