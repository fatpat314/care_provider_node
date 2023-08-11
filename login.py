from flask import jsonify, request
import requests

from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity

def login_data(cloud_url, request):
    email = request.json.get('email')
    password = request.json.get('password')
    url = f'{cloud_url}/provider-login'
    data = {'email': email, 'password': password}
    response = requests.post(url, json=data)
    response = response.json()
    if response == {'User': []}:
        print("RESULT: ", response)
        return jsonify({"status":"error", "message": "Invalid email or password"}), 401
    v_id = response['User'][0]['v_id']
    access_token = create_access_token(identity=v_id)
    return jsonify({'access_token': access_token}), 200