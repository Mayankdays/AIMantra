from flask import Flask, render_template, request, redirect, url_for, jsonify
from pdf_linker import get_pdf_link
from backend import ai
import sqlite3
import markdown

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        if 'delete_id' in request.form:
            row_id = request.form['delete_id']
            cursor.execute("DELETE FROM combined_cbse_data WHERE id=?", (row_id,))
            conn.commit()

    # Fetch data from the database
    cursor.execute("SELECT * FROM combined_cbse_data")
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('admin.html', rows=rows)

@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        # Database Connection
        conn = connect_db()
        c = conn.cursor()

        # Data from the form
        board = request.form['field1']
        grade = request.form['field2']
        subject = request.form['field3']
        chapter = request.form['field4']
        link = request.form['field5']

        # Inserting Data
        c.execute("INSERT INTO combined_cbse_data (board_name, grade_name, subject_name, chapter_name, chapter_link) VALUES (?, ?, ?, ?, ?)", (board, grade, subject, chapter, link))

        # Close the connection
        conn.commit()
        conn.close()

        return redirect(url_for('admin'))
    return render_template('add_data.html')


questions = []

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')
    else:
        try:
            message = request.form['message']
        except KeyError:
            return jsonify({'error': 'Missing message'}), 400

        # Temp Storage for messages.
        chapter = ['Motion in a Straight Line']

        questions.append(message)
        response = ai(questions, chapter)
        response = response['output_text']
        html_response = markdown.markdown(response)
        
        questions.clear()
        return jsonify({
            'messages': questions,
            'response': html_response
        })

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # Add the user to the database
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()

    # Close the database connection
    conn.close()

    return render_template('add_user.html')

if __name__ == '__main__':
    app.run(debug=True)