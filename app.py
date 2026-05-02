from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"  # needed for session

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yash@1234",
    database="student_achievement_db"
)

# 🧠 helper to store query logs
def log_query(q):
    if "queries" not in session:
        session["queries"] = []
    session["queries"].insert(0, q)
    session.modified = True


# 🏠 HOME
@app.route('/')
def home():
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT 
        a.achievement_id,
        s.first_name,
        s.last_name,
        a.title,
        a.type,
        a.status
    FROM achievement a
    JOIN student s ON s.net_id = a.student_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    log_query(query)

    cursor.execute("SELECT net_id, first_name FROM student")
    students = cursor.fetchall()

    # 🔥 faculties
    cursor.execute("SELECT net_id, first_name FROM faculty_advisor")
    faculties = cursor.fetchall()

    return render_template(
        "index.html",
        data=data,
        students=students,
        faculties=faculties,
        queries=session.get("queries", [])
    )


# ➕ ADD STUDENT
@app.route('/add-student', methods=['POST'])
def add_student():
    net_id = request.form['net_id']
    first = request.form['first_name']
    last = request.form['last_name']
    email = request.form['email']
    dob = request.form['dob']
    faculty = request.form['faculty_id']

    query = f"""
    INSERT INTO student VALUES
    ('{net_id}','{first}','{last}','{email}','{dob}','{faculty}')
    """

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO student VALUES (%s,%s,%s,%s,%s,%s)
    """, (net_id, first, last, email, dob, faculty))

    db.commit()
    log_query(query)

    return redirect('/')


# ➕ ADD ACHIEVEMENT
@app.route('/add', methods=['POST'])
def add():
    student_id = request.form['student_id']
    title = request.form['title']
    type_ = request.form['type']

    query = f"""
    INSERT INTO achievement (student_id, title, type, date, status)
    VALUES ('{student_id}','{title}','{type_}', CURDATE(), 'Pending')
    """

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO achievement (student_id, title, type, date, status)
        VALUES (%s,%s,%s,CURDATE(),'Pending')
    """, (student_id, title, type_))

    db.commit()
    log_query(query)

    return redirect('/')


# 🔍 FILTER
@app.route('/filter/<status>')
def filter(status):
    cursor = db.cursor(dictionary=True)

    query = f"""
    SELECT 
        a.achievement_id,
        s.first_name,
        s.last_name,
        a.title,
        a.type,
        a.status
    FROM achievement a
    JOIN student s ON s.net_id = a.student_id
    WHERE a.status = '{status}'
    """

    cursor.execute("""
        SELECT 
            a.achievement_id,
            s.first_name,
            s.last_name,
            a.title,
            a.type,
            a.status
        FROM achievement a
        JOIN student s ON s.net_id = a.student_id
        WHERE a.status = %s
    """, (status,))

    data = cursor.fetchall()
    log_query(query)

    cursor.execute("SELECT net_id, first_name FROM student")
    students = cursor.fetchall()

    cursor.execute("SELECT net_id, first_name FROM faculty_advisor")
    faculties = cursor.fetchall()

    return render_template(
    "index.html",
    data=data,
    students=students,
    faculties=faculties,
    queries=session.get("queries", [])
)


# ✅ UPDATE STATUS
@app.route('/update/<int:id>/<status>')
def update(id, status):
    query = f"""
    UPDATE achievement
    SET status = '{status}'
    WHERE achievement_id = {id}
    """

    cursor = db.cursor()
    cursor.execute("""
        UPDATE achievement SET status=%s WHERE achievement_id=%s
    """, (status, id))

    db.commit()
    log_query(query)

    return redirect('/')


# ❌ DELETE
@app.route('/delete/<int:id>')
def delete(id):
    query = f"DELETE FROM achievement WHERE achievement_id = {id}"

    cursor = db.cursor()
    cursor.execute("DELETE FROM achievement WHERE achievement_id=%s", (id,))
    db.commit()

    log_query(query)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)