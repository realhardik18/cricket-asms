from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from creds import MONGO_DB_URI

app = Flask(__name__)

# MongoDB setup
#client = MongoClient("mongodb://localhost:27017/")
client = MongoClient(MONGO_DB_URI)
db = client['cricket_academy_db']
users_collection = db['users']

# User registration route
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')  # You can hash this password for security

    # Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({"error": "User with this email already exists"}), 400

    # Create new user
    new_user = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": password,
        "payment_history": {}
    }
    
    users_collection.insert_one(new_user)
    return jsonify({"message": "User registered successfully"}), 201

# User login route
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})

    if not user or user['password'] != password:
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful", "user": str(user['_id'])}), 200

if __name__ == '__main__':
    app.run(debug=True)
