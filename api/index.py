from flask import Flask, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

file_path = os.path.join(os.path.dirname(__file__), 'class_pred.pickle')
with open(file_path, 'rb') as f:
    model1 = pickle.load(f)

file_path = os.path.join(os.path.dirname(__file__), 'class_pred.pickle')
with open(file_path, 'rb') as f:
    model2 = pickle.load(f)

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

    if not all([region, num_of_bedrooms, num_of_bathrooms, apartment_space]):
        return jsonify({'error': 'Missing input parameters'}), 400

    try:
        region = int(region)
        num_of_bedrooms = int(num_of_bedrooms)
        num_of_bathrooms = int(num_of_bathrooms)
        apartment_space = float(apartment_space)
        predicted_price = predict_price(region, num_of_bedrooms, num_of_bathrooms, apartment_space)
        if predicted_price is not None:
            return jsonify({'predicted_price': f'{int(predicted_price):,}'})
        else:
            return jsonify({'error': 'Prediction failed'}), 500
    except ValueError:
        return jsonify({'error': 'Invalid input types'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
