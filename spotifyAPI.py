import requests as rq
import json
import os
import base64
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def request_auth():
    auth_string = client_id + ':' +client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'grant_type': 'client_credentials'
    }
    res = rq.post(url, headers=headers, data=params)
    json_res = json.loads(res.content)
    token = json_res['access_token']
    return token
