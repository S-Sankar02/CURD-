from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey"

# MYSQL CONFIG
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin123'
app.config['MYSQL_DB'] = 'ai'

mysql = MySQL(app)


@app.before_request
def session_check():
    if 'user' in session and 'role' not in session:
        session.clear()
        return redirect('/login')


# HOME

@app.route('/')
def home():
    return redirect('/login')


# LOGIN PAGE

@app.route('/login')
def login():
    return render_template('login.html')


# LOGIN USER

@app.route('/login_user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", [email])
    user = cur.fetchone()
    cur.close()

    if user:

        db_password = user[4]
        role = user[5]

        if not db_password:
            return "Password not set. Please reset password."

        if check_password_hash(db_password, password):

            session['user'] = user[1]
            session['role'] = role

            if role == "admin":
                return redirect('/admin_dashboard')
            else:
                return redirect('/dashboard')

    return "Invalid Email or Password"

# REGISTER

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_user', methods=['POST'])
def register_user():

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']

    hashed = generate_password_hash(password)

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users(name, email, phone, password, role)
        VALUES(%s,%s,%s,%s,%s)
    """, (name, email, phone, hashed, "user"))

    mysql.connection.commit()
    cur.close()

    return redirect('/login')

# LOGOUT (ONLY HERE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# USER DASHBOARD

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    if session.get('role') == 'admin':
        return redirect('/admin_dashboard')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    cur.close()

    return render_template('index.html', users=data)

# ADMIN DASHBOARD

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'user' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return "Access Denied"

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    cur.close()

    return render_template('admin.html', users=data)

# ADD PAGE

@app.route('/add')
def add():

    if 'user' not in session:
        return redirect('/login')

    return render_template('add.html')


# INSERT USER

@app.route('/insert', methods=['POST'])
def insert():

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    role = request.form['role']

    cur = mysql.connection.cursor()

    #  CHECK EMAIL FIRST
    cur.execute("SELECT * FROM users WHERE email=%s", [email])
    existing_user = cur.fetchone()

    if existing_user:
        cur.close()
        return "Email already exists!"

    hashed = generate_password_hash(password)

    cur.execute("""
        INSERT INTO users(name,email,phone,password,role)
        VALUES(%s,%s,%s,%s,%s)
    """, (name,email,phone,hashed,role))

    mysql.connection.commit()
    cur.close()

    return redirect('/dashboard')

# EDIT

@app.route('/edit/<id>')
def edit(id):

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", [id])
    user = cur.fetchone()
    cur.close()

    return render_template('edit.html', user=user)


# UPDATE

@app.route('/update/<id>', methods=['POST'])
def update(id):

    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE users
        SET name=%s, email=%s, phone=%s
        WHERE id=%s
    """, (name,email,phone,id))

    mysql.connection.commit()
    cur.close()

    return redirect('/dashboard')


# DELETE

@app.route('/delete/<id>')
def delete(id):

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", [id])
    mysql.connection.commit()
    cur.close()

    return redirect('/dashboard')


@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')


# RESET PASSWORD

@app.route('/reset_password', methods=['POST'])
def reset_password():

    email = request.form['email']
    password = request.form['password']

    hashed = generate_password_hash(password)

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE users
        SET password=%s
        WHERE email=%s
    """, (hashed,email))

    mysql.connection.commit()
    cur.close()

    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)

