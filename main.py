import config
from dotenv import load_dotenv
# import openai
from flask import Flask, jsonify, request, session, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
import requests, random, threading, uuid, json
import argparse

from login import login_data
from profile import profile_data, patient_profile_data, graph_visual_data, event_visual_data
from register import register_data

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY # change this to a random string in production
CNM_url = "http://localhost:8010"
# CNM_url = "https://cognitive-network-manager-rdwl5upzra-uw.a.run.app"
jwt = JWTManager(app)
load_dotenv()

@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        data = "Care Provider Node"
        return jsonify({'data': data})

@app.route('/provider-register', methods=['POST'])
def provider_register():
    try:
        new_provider = register_data(CNM_url, request)
    except:
        return('err')
    # add event
    event_url = get_event_server()
    event_url = event_url['url']
    event_url = f'{event_url}/event-provider-register'
    data = {'provider_id': new_provider}
    event_response = requests.post(event_url, json=data)
    return('hi')

@app.route('/provider-login', methods=['GET', 'POST'])
def provider_login():
    return login_data(CNM_url, request)

@app.route('/provider-profile', methods=['GET', 'POST'])
@jwt_required()
def provider_profile():
    return profile_data(CNM_url, request)

@app.route('/patient-profile', methods=['GET', 'POST'])
@jwt_required()
def patient_profile():
    return(patient_profile_data(CNM_url, request))

@app.route('/diagnose', methods = ['GET', 'POST'])
@jwt_required()
def diagnose():
    # Add a way to connect Dr with disease
    try:
        care_provider_id = get_jwt_identity()
        patient_id = request.json.get('patient_id')
        disease_name = request.json.get('disease_name')
        print("CP ID: ", care_provider_id)
        if request.method == 'POST':
            url = f'{CNM_url}/diagnose'
            data = {'patient_id': patient_id, 'disease_name': disease_name, 'care_provider_id': care_provider_id}
            response = requests.post(url, json=data)
            disease_id = response.json()
    except:
        return('err')
    # event
    event_url = get_event_server()
    event_url = event_url['url']
    event_url = f'{event_url}/event-diagnosis'
    data = {'provider_id': care_provider_id, 'patient_id': patient_id, 'disease_id': disease_id}
    event_response = requests.post(event_url, json=data)

    return jsonify("test")

@app.route('/add-patient', methods=['GET', 'POST'])
@jwt_required()
def add_patient():
    try:
        patient_id = request.json.get('input')
        # print("ID: ", patient_id)
        care_provider_id = get_jwt_identity()
        url = f'{CNM_url}/add-patient'
        data = {'patient': patient_id, 'provider': care_provider_id}
        response = requests.post(url, json=data)
        # print(response.text)
        
        auth_header = request.headers.get("Authorization")
    
        if auth_header:
            # Extract the token from the header (assuming "Bearer" prefix)
            jwt_token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
            # print(f"JWT Token: {token}")
        else:
            print("Authorization header not found")

        if json.loads(response.text) == {"User": []}:
            return jsonify(response.json)
        else:
            event_url = get_event_server()
            event_url = event_url['url']
            print("TEST", event_url)
            event_url = f'{event_url}/event-patient-provider'
            data = {'patient_id': patient_id, 'provider_id': care_provider_id}
            headers = {
                'Authorization': f'Bearer {jwt_token}',  # Assuming "Bearer" is the prefix for your token
                'Content-Type': 'application/json'  # Assuming JSON data is being sent
            }
            event_response = requests.post(event_url, json=data, headers=headers)
            return jsonify(patient_id)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_event_server():
    event_url = f'{CNM_url}/event_server'
    response = requests.get(event_url)
    return response.json()

@app.route('/graph-root', methods=['GET', 'POST'])
@jwt_required()
def graph_root():
    root, leaf = graph_visual_data(CNM_url, request)
    return {"root": root, "leaf": leaf}

@app.route('/event-root', methods=['GET', 'POST'])
@jwt_required()
def event_root():
    root = event_visual_data(CNM_url, request)
    return(root.json())

@app.route('/event-leaf', methods=['GET', 'POST'])
@jwt_required()
def event_leaf():
    pass



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8070, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)