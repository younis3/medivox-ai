from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from db import db
from models import User
import requests
from datetime import datetime
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
    user_name = data.get('user_name')
    password = data.get('password')

    if not user_name or not password:
        return jsonify({'error': 'user_name and password are required'}), 400

    user = User.query.filter_by(user_name=user_name).first()

    if user and user.password_h == password:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.user_id,
                'user_name': user.user_name
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/test-db')
def test_db():
    try:
        users = User.query.all()
        return jsonify({"message": "Database connection successful", "user_count": len(users)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    user_name = data.get('user_name')
    email = data.get('email')
    password_h = data.get('password')  # stored as hashed password
    created_at = updated_at = datetime.utcnow()

    if not all([user_name, email, password_h]):
        return jsonify({'error': 'user_name, email, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    new_user = User(
        user_name=user_name,
        email=email,
        password_h=password_h,
        created_at=created_at,
        updated_at=updated_at
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'id': new_user.user_id,
            'user_name': new_user.user_name,
            'email': new_user.email
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

@app.route('/get_profile_by_id', methods=['POST'])
def get_profile_by_id():
    req_data = request.get_json(force=True) or {}

    business_id = req_data.get('business_id')
    token = req_data.get('token') or os.getenv('GB_TOKEN')
    user = req_data.get('user') or os.getenv('GB_USER')

    if not all([business_id, token, user]):
        return jsonify({"error": "Missing required fields: business_id, token, user"}), 400

    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "cred": {
            "token": token,
            "user": user
        },
        "method": "business.get_profile_by_id",
        "params": {
            "business": {
                "id": business_id
            },
            "skip_worker_sorting": True
        }
    }

    try:
        response = requests.post("https://apiv2.med.me/rpc", json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to reach GBooking API: {str(e)}"}), 502

    data = response.json()

    if "error" in data:
        return jsonify({"error": data["error"]}), 500

    return jsonify(data.get("result", data))

@app.route('/get_slots', methods=['POST'])
def get_slots():
    req_data = request.get_json(force=True) or {}

    business_id = req_data.get('business_id')
    taxonomy_id = req_data.get('taxonomy_id')
    resource_id = req_data.get('resource_id')
    date_from = req_data.get('from')  # Format: 2025-04-11T00:00:00.000Z
    date_to = req_data.get('to')      # Format: 2025-04-15T00:00:00.000Z

    token = req_data.get('token') or os.getenv('GB_TOKEN')
    user = req_data.get('user') or os.getenv('GB_USER')

    if not all([business_id, taxonomy_id, resource_id, date_from, date_to]):
        return jsonify({"error": "Missing required fields"}), 400

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "cred": {},  # No token needed for this endpoint in your collection
        "method": "CracSlots.GetCRACResourcesAndRooms",
        "params": {
            "business": {
                "id": business_id,
                "widget_configuration": {
                    "cracServer": "CRAC_PROD3",
                    "mostFreeEnable": True
                },
                "general_info": {
                    "timezone": "Europe/Moscow"
                }
            },
            "filters": {
                "resources": [
                    {
                        "id": resource_id,
                        "duration": 30
                    }
                ],
                "taxonomies": [taxonomy_id],
                "rooms": [],
                "date": {
                    "from": date_from,
                    "to": date_to
                }
            }
        }
    }

    try:
        response = requests.post("https://cracslots.gbooking.ru/rpc", json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to reach CRAC API: {str(e)}"}), 502

    data = response.json()

    if "error" in data:
        return jsonify({"error": data["error"]}), 500

    return jsonify(data.get("result", data))

@app.route('/add_patient', methods=['POST'])
def add_patient():
    req_data = request.get_json(force=True) or {}

    business_id = req_data.get('business_id')
    name = req_data.get('name')
    surname = req_data.get('surname')
    phone = req_data.get('phone')  # expects: {"country_code": "...", "area_code": "...", "number": "..."}
    email = req_data.get('email')  # single email as string

    token = req_data.get('token') or os.getenv('GB_TOKEN')
    user = req_data.get('user') or os.getenv('GB_USER')

    if not all([business_id, name, surname, phone, email, token, user]):
        return jsonify({"error": "Missing required fields"}), 400

    payload = {
        "jsonrpc": "2.0",
        "id": 18,
        "cred": {
            "token": token,
            "user": user
        },
        "method": "client.add_client",
        "params": {
            "business": {
                "id": business_id
            },
            "client": {
                "name": name,
                "surname": surname,
                "phone": [phone],
                "email": [email]
            }
        }
    }

    try:
        response = requests.post("https://apiv2.med.me/rpc", json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to reach GBooking API: {str(e)}"}), 502

    data = response.json()

    if "error" in data:
        return jsonify({"error": data["error"]}), 500

    return jsonify(data.get("result", data))


@app.route('/reserve_appointment', methods=['POST'])
def reserve_appointment():
    req_data = request.get_json(force=True) or {}

    business_id = req_data.get('business_id')
    taxonomy_id = req_data.get('taxonomy_id')
    resource_id = req_data.get('resource_id')
    start_time = req_data.get('start')  # Example: "2025-04-15T09:00:00"
    duration = req_data.get('duration', 15)
    price_amount = req_data.get('price', 0)
    client_appear = req_data.get('client_appear', "NONE")

    token = req_data.get('token') or os.getenv('GB_TOKEN')
    user = req_data.get('user') or os.getenv('GB_USER')

    if not all([business_id, taxonomy_id, resource_id, start_time, token, user]):
        return jsonify({"error": "Missing required fields"}), 400

    payload = {
        "jsonrpc": "2.0",
        "id": 19,
        "cred": {
            "token": token,
            "user": user
        },
        "method": "appointment.reserve_appointment",
        "params": {
            "appointment": {
                "start": start_time,
                "duration": duration,
                "price": {
                    "amount": price_amount,
                    "currency": "ILS"
                }
            },
            "source": "AI",
            "business": {
                "id": business_id
            },
            "taxonomy": {
                "id": taxonomy_id
            },
            "client_appear": client_appear,
            "resource": {
                "id": resource_id
            }
        }
    }

    try:
        response = requests.post("https://apiv2.med.me/rpc", json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to reach GBooking API: {str(e)}"}), 502

    data = response.json()

    if "error" in data:
        return jsonify({"error": data["error"]}), 500

    return jsonify(data.get("result", data))

@app.route('/confirm_appointment', methods=['POST'])
def confirm_appointment():
    req_data = request.get_json(force=True) or {}

    appointment_id = req_data.get('appointment_id')
    client_id = req_data.get('client_id')

    if not appointment_id or not client_id:
        return jsonify({"error": "Missing appointment_id or client_id"}), 400

    payload = {
        "jsonrpc": "2.0",
        "id": 19,
        "cred": {},
        "method": "appointment.client_confirm_appointment",
        "params": {
            "appointment": {
                "id": appointment_id
            },
            "client": {
                "id": client_id
            }
        }
    }

    try:
        response = requests.post("https://apiv2.med.me/rpc", json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to confirm appointment: {str(e)}"}), 502

    data = response.json()

    if "error" in data:
        return jsonify({"error": data["error"]}), 500

    return jsonify(data.get("result", data))

if __name__ == '__main__':
    app.run(debug=True)