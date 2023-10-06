from flask import jsonify, request
import requests

def register_data(cloud_url, request):
    url = f'{cloud_url}/provider-register'
    data = request.get_json()

    # send to CNM
    data = {
        'name': data['name'], 
        'email': data['email'], 
        'password': data['password'], 
        'specialty': data['specialty'], 
        'location': data['location']
    }
    response = requests.post(url, json=data)
    return(response.json())
