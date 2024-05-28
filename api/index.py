from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/sum', methods=['POST'])
def sum_numbers():
    data = request.get_json()
    a = data.get('a', 0)
    b = data.get('b', 0)
    c = data.get('c', 0)
    result = a + b + c
    return jsonify({'sum': result})

# Export the app
if __name__ == "__main__":
    app.run()
