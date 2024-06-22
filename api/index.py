from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import json
import os
from passlib.context import CryptContext

app = Flask(__name__)
CORS(app, supports_credentials=True, allow_headers=["Content-Type"])

# Load models
with open('api/class_pred.pickle', 'rb') as f:
    model1 = pickle.load(f)

with open('api/dt_model.pickle', 'rb') as f:
    model2 = pickle.load(f)


# Define a function to predict the price
def predict_price(region, num_of_bedrooms, num_of_bathrooms, apartment_space):
    try:
        X_new = np.array([[region, num_of_bedrooms, num_of_bathrooms, apartment_space]])
        class_prediction = model1.predict(X_new)[0]
        X_new = np.array([[region, num_of_bedrooms, num_of_bathrooms, apartment_space, class_prediction]])
        predicted_price = model2.predict(X_new)[0]
        return predicted_price
    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return None


@app.route('/predict', methods=['GET'])
def predict():
    region = request.args.get('region')
    num_of_bedrooms = request.args.get('num_of_bedrooms')
    num_of_bathrooms = request.args.get('num_of_bathrooms')
    apartment_space = request.args.get('apartment_space')
    floors = request.args.get('floors')
    school_Distance = request.args.get('school_Distance')
    clinic_Distance = request.args.get('clinic_Distance')	
    restaurant_Distance = request.args.get('restaurant_Distance') 
    pharmacy_Distance = request.args.get('pharmacy_Distance')
    Air_conditioned = request.args.get('Air_conditioned')	

    if not all([region, num_of_bedrooms, num_of_bathrooms, apartment_space]):
        return jsonify({'error': 'Missing input parameters'}), 400

    try:
        region = int(region)
        num_of_bedrooms = int(num_of_bedrooms)
        num_of_bathrooms = int(num_of_bathrooms)
        apartment_space = float(apartment_space)
        predicted_price = predict_price(region, num_of_bedrooms, num_of_bathrooms, apartment_space)
        if predicted_price is not None:
            response = jsonify({'predicted_price': f'{int(predicted_price):,}'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            return jsonify({'error': 'Prediction failed'}), 500
    except ValueError:
        return jsonify({'error': 'Invalid input types'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Setup password context
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
USER_DATA_FILE = 'users.json'


def read_users():
    if not os.path.exists(USER_DATA_FILE):
        return []
    with open(USER_DATA_FILE, 'r') as f:
        return json.load(f)


def write_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def hash_password(password: str):
    return password_context.hash(password)


def verify_user_credentials(user_email: str, user_password: str):
    users = read_users()
    user = next((u for u in users if u['user_email'] == user_email), None)
    if user and password_context.verify(user_password, user['user_password']):
        return True
    return False


def register_user(user_name: str, user_password: str, user_email: str, user_phone: str):
    users = read_users()
    users.append({
        'user_name': user_name,
        'user_password': hash_password(user_password),
        'user_email': user_email,
        'user_phone': user_phone
    })
    write_users(users)


def delete_user(user_email: str):
    users = read_users()
    users = [user for user in users if user['user_email'] != user_email]
    write_users(users)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user_name = data.get('user_name')
    user_password = data.get('user_password')
    user_email = data.get('user_email')
    user_phone = data.get('user_phone')

    if any(u['user_email'] == user_email for u in read_users()):
        response= jsonify({'error': 'Username already registered'}), 400
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    register_user(user_name, user_password, user_email, user_phone)
    response= jsonify({'message': 'Registration successful'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_email = data.get('user_email')
    user_password = data.get('user_password')

    if not verify_user_credentials(user_email, user_password):
        
        response= jsonify({
            'error': 'Invalid credentials'
        }), 401
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    response= jsonify({'message': 'Login successful'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response




@app.route("/password/reset", methods=["PUT"])
def reset_password():
    data = request.get_json()
    user_email = data.get('user_email')
    new_password = data.get('new_password')

    # Check if user_email and new_password are provided and valid
    if not (user_email and new_password):
        return jsonify({'error': 'Invalid user data'}), 400

    users = read_users()
    for user in users:
        if user['user_email'] == user_email:
            user['user_password'] = hash_password(new_password)
            write_users(users)
            return jsonify({'message': 'Password reset successful'})

    return jsonify({'error': 'Invalid user data'}), 400


@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(debug=True)
