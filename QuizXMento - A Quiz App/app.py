from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from forms import RegistrationForm, LoginForm
import mysql.connector
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Database connection function
def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with your MySQL username
        password='Mihir@197',  # Replace with your MySQL password
        database='quiz_app'
    )

# --- Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        hashed_password = generate_password_hash(password)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            if err.errno == 1062:
                flash('Email already registered.', 'danger')
            else:
                flash(f"Error: {err}", 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- Dashboard and Upload ---

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        file = request.files['file']
        try:
            df = pd.read_excel(file)
            conn = get_db()
            cursor = conn.cursor()
            # Clear existing answers and questions before inserting new ones
            cursor.execute("DELETE FROM answers")
            cursor.execute("DELETE FROM questions")
            for index, row in df.iterrows():
                cursor.execute(
                    "INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_ans) VALUES (%s,%s,%s,%s,%s,%s)",
                    (row['Question'], row['Option_A'], row['Option_B'], row['Option_C'], row['Option_D'], row['Correct_Ans'])
                )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard', uploaded=1))
        except Exception as e:
            return f"Error processing file: {e}"
    return render_template('upload.html')

# --- Quiz Flow ---

@app.route('/start_quiz')
def start_quiz():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Check if questions exist in the database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    question_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if question_count == 0:
        # No questions uploaded, redirect to upload page
        flash('No questions available. Please upload questions first.')
        return redirect('/upload')
    else:
        return render_template('start_quiz.html')

@app.route('/confirm', methods=['POST'])
def confirm_start():
    return redirect('/quiz')

@app.route('/quiz')
def quiz():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('quiz.html')

@app.route('/get_questions')
def get_questions():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    cursor.close()
    conn.close()
    # Send questions without correct answer
    questions_response = []
    for q in questions:
        questions_response.append({
            'id': q['id'],
            'question': q['question'],
            'option_a': q['option_a'],
            'option_b': q['option_b'],
            'option_c': q['option_c'],
            'option_d': q['option_d']
        })
    return jsonify({'questions': questions_response})

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    answers = data['answers']
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    score = 0
    for q_id_str, selected_option in answers.items():
        q_id = int(q_id_str)
        cursor.execute("SELECT correct_ans FROM questions WHERE id=%s", (q_id,))
        correct = cursor.fetchone()[0]
        is_correct = (correct == selected_option)
        if is_correct:
            score += 1
        cursor.execute(
            "INSERT INTO answers (user_id, question_id, selected_option, is_correct) VALUES (%s, %s, %s, %s)",
            (user_id, q_id, selected_option, is_correct)
        )
    conn.commit()
    cursor.close()
    conn.close()
    total_questions = len(answers)
    return jsonify({'score': score, 'total': total_questions})

@app.route('/result')
def result():
    score = request.args.get('score')
    total = request.args.get('total')
    try:
        score_int = int(score)
        total_int = int(total)
    except (TypeError, ValueError):
        score_int = 0
        total_int = 0
    incorrect = total_int - score_int
    return render_template('result.html', score=score_int, total=total_int, incorrect=incorrect)

# --- Additional Routes ---

@app.route('/quiz_end')
def quiz_end():
    # Optional: redirect after quiz completion
    return redirect(url_for('result', score=request.args.get('score'), total=request.args.get('total')))

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)