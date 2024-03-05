from flask import jsonify, request
import requests

from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity

def profile_data(cloud_url, request):
    try:
        current_user = get_jwt_identity()
        url = f'{cloud_url}/provider-profile'
        data = {'identity': current_user}
        response = requests.post(url, json=data)
        current_user_info = response.json()
        current_user_data = current_user_info[0]['User'][0]['attributes']
        name = current_user_data['name']
        # Other user profile display info...

        return jsonify({'name': f'{name}'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

def patient_profile_data(cloud_url, request):
    try:
        # print("HELLO")
        url = f'{cloud_url}/profile'
        patient_id = request.json.get('patient_id')
        data = {'identity': patient_id}
        response = requests.post(url, json=data)
        current_patient_info = response.json()
        # print(current_patient_info)
        current_patient_data = current_patient_info[0]['User'][0]['attributes']
        first_name = current_patient_data['first_name']
        DOB = current_patient_data['DOB']
        events = current_patient_data['event']
        # print("EVENTS: ",events)

        return jsonify({'first_name': f'{first_name}', 'DOB': f'{DOB}', 'events': events}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def graph_visual_data(cloud_url, request):
    # print("NAME: ", request.json.get('patient_id'))
    try:
        url = f'{cloud_url}/graph-visual'
        # print("URL: ", url)
        patient_id = request.json.get('patient_id')
        # print("Patient_ID: ", patient_id)
        data = {'identity': patient_id}
        response = requests.post(url, json=data)
        # current_patient_info = response.json()
        # print("RESPONSE: ", response.json()[0])
        # print("DICT: ", response.json()[1])
        root = response.json()[0]
        leaf = response.json()[1]
        ret_list = [root, leaf]
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return ret_list

def event_visual_data(cloud_url, request):
    # print("NAME: ", request.json.get('patient_id'))
    try:
        url = f'{cloud_url}/event-visual'
        patient_id = request.json.get('patient_id')
        data = {'identity': patient_id}
        response = requests.post(url, json=data)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    # return ret_list
    return("test")