from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from db import db
from models import User
import requests

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return 'Server is running!'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({'error': 'Name and password are required'}), 400

    user = User.query.filter_by(name=name).first()

    if user and user.password == password:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid name or password'}), 401

@app.route('/test-db')
def test_db():
    try:
        # Try to query the User1 table
        users = User.query.all()
        return jsonify({"message": "Database connection successful", "user_count": len(users)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    # Validate required fields
    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password are required'}), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Create new user
    new_user = User(name=name, email=email, phone=phone, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email,
            'phone': new_user.phone
        }
    }), 201

@app.route('/get_network_data', methods=['POST'])
def get_network_data():
    req_data = request.get_json(force=True) or {}
    network_id = req_data.get('networkID', 456)
    token = req_data.get('token') or os.getenv('GB_TOKEN')
    user  = req_data.get('user')  or os.getenv('GB_USER')

    if not token or not user:
        return jsonify({"error": "Missing token or user"}), 400

    payload = {
        "jsonrpc": "2.0",
        "id": 7,
        "cred": {
            "token": token,
            "user": user
        },
        "method": "business.get_network_data",
        "params": {
            "networkID": network_id
        }
    }

    print("[DEBUG] Payload being sent:", payload)

    try:
        response = requests.post("https://apiv2.med.me/rpc", json=payload)
        print(f"[DEBUG] GBooking Status Code: {response.status_code}")
        print("[DEBUG] GBooking Response:", response.text)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 502

    data = response.json()

    if "error" in data:
        return jsonify({"error": data["error"]}), 500

    return jsonify(data.get("result", data))


if __name__ == '__main__':
    app.run(debug=True)