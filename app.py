from flask import Flask, render_template, redirect, request, session, url_for
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['rajvanshi_cricket_club']
users_collection = db['users']
payments_collection = db['payments']

# Function to serialize ObjectId
def serialize_objectid(data):
    if isinstance(data, list):
        for item in data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
    elif '_id' in data:
        data['_id'] = str(data['_id'])
    return data

# Home Route
@app.route('/')
def home():
    return render_template('login.html')

# Route to send a new payment request
@app.route('/send_payment_request', methods=['POST'])
def send_payment_request():
    if 'role' in session and session['role'] == 'admin':
        student_id = request.form['student']
        note = request.form['note']
        amount = float(request.form['amount'])
        due_date = request.form['due_date']

        # Create a new payment request for the selected student
        payments_collection.insert_one({
            'student_id': ObjectId(student_id),
            'note': note,
            'amount': amount,
            'status': 'Unpaid',
            'due_date': due_date,
        })

        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        password = request.form['password']
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            'name': name,
            'email': email,
            'phone': phone,
            'role': role,
            'password': hashed_password  # Store hashed password
        })
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = users_collection.find_one({'email': email})

        if user and check_password_hash(user['password'], password):  # Verify the password
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return "Invalid email or password"  # Simple error message
    return render_template('login.html')

# Admin Dashboard
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        # Get filter choice from the dropdown
        filter_status = request.args.get('status', 'all')  # Default to 'all' if not selected
        filter_user = request.args.get('user', 'all')  # Default to 'all' if not selected

        # Query for payments based on status
        if filter_status == 'all':
            if filter_user == 'all':
                payments = list(payments_collection.find())
            else:
                payments = list(payments_collection.find({'student_id': ObjectId(filter_user)}))
        else:
            if filter_user == 'all':
                payments = list(payments_collection.find({'status': filter_status}))
            else:
                payments = list(payments_collection.find({'status': filter_status, 'student_id': ObjectId(filter_user)}))

        payments = serialize_objectid(payments)
        
        # Get all users (students) for filtering purposes
        users = list(users_collection.find({'role': 'student'}))
        users = serialize_objectid(users)

        return render_template('admin_dashboard.html', payments=payments, users=users, filter_status=filter_status, filter_user=filter_user)
    return redirect(url_for('login'))

# Verify Payment by Admin
@app.route('/verify/<payment_id>')
def verify_payment(payment_id):
    if 'role' in session and session['role'] == 'admin':
        payments_collection.update_one({'_id': ObjectId(payment_id)}, {'$set': {'status': 'Verified'}})
    return redirect(url_for('admin_dashboard'))

# Student Dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        user_id = session['user_id']
        
        # Get payments for the current student (based on user ID)
        payments = list(payments_collection.find({'student_id': ObjectId(user_id)}))
        payments = serialize_objectid(payments)

        return render_template('student_dashboard.html', payments=payments)
    return redirect(url_for('login'))

# Pay Payment as Student
@app.route('/pay/<payment_id>')
def pay_payment(payment_id):
    if 'role' in session and session['role'] == 'student':
        payments_collection.update_one({'_id': ObjectId(payment_id)}, {'$set': {'status': 'Paid under verification'}})
    return redirect(url_for('student_dashboard'))

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
