import config
from dotenv import load_dotenv
import openai
from flask import Flask, jsonify, request, session, g
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
import requests, names, random, threading, uuid, json
import argparse

from login import login_data
from profile import profile_data, patient_profile_data

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY # change this to a random string in production
cloud_url = "http://localhost:6000"
jwt = JWTManager(app)
load_dotenv()

@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        data = "hello Class!"
        return jsonify({'data': data})

@app.route('/provider-login', methods=['GET', 'POST'])
def provider_login():
    return login_data(cloud_url, request)

@app.route('/provider-profile', methods=['GET', 'POST'])
@jwt_required()
def provider_profile():
    return profile_data(cloud_url, request)

@app.route('/patient-profile', methods=['GET', 'POST'])
@jwt_required()
def patient_profile():
    return(patient_profile_data(cloud_url, request))

@app.route('/diagnose', methods = ['GET', 'POST'])
@jwt_required()
def diagnose():
    # Add a way to connect Dr with disease
    care_provider_id = get_jwt_identity()
    patient_id = request.json.get('patient_id')
    disease_name = request.json.get('disease_name')
    print("CP ID: ", care_provider_id)
    if request.method == 'POST':
        url = f'{cloud_url}/diagnose'
        data = {'patient_id': patient_id, 'disease_name': disease_name, 'care_provider_id': care_provider_id}
        response = requests.post(url, json=data)
    return jsonify("test")

@app.route('/add-patient', methods=['GET', 'POST'])
@jwt_required()
def add_patient():
    try:
        patient_id = request.json.get('input')
        # print("ID: ", patient_id)
        care_provider_id = get_jwt_identity()
        url = f'{cloud_url}/add-patient'
        data = {'patient': patient_id, 'provider': care_provider_id}
        response = requests.post(url, json=data)
        print(response.text)
        if json.loads(response.text) == {"User": []}:
            return jsonify(response.json)
        else:
            return jsonify(patient_id)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8070, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)