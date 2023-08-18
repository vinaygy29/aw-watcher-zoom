from typing import Dict
import base64
import requests
import json

zoom_oauth_url = 'https://zoom.us/oauth/token'
zoom_api_base_url = 'https://api.zoom.us/v2/'
token = ""


def get_token(config):
    global token
    if token != "":
        return token
    print("calling zoom oath api")
    account_id = config["aw-watcher-zoom"].get("account_id", None)
    client_id = config["aw-watcher-zoom"].get("client_id", None)
    client_secret = config["aw-watcher-zoom"].get("client_secret", None)

    basic_authorization = client_id + ':' + client_secret
    basic_authorization = base64.b64encode(basic_authorization.encode('ascii')).decode('ascii')

    api_url = zoom_oauth_url + "?grant_type=account_credentials&account_id=" + account_id
    headers = {"Authorization": "Basic " + basic_authorization}
    response = requests.post(api_url, data=json.dumps({}), headers=headers)
    if response.status_code == 200:
        token_ata = response.json()
        token = "Bearer " + token_ata["access_token"]
        return token
    else:
        return ""


def get_meeting(config) -> Dict:
    api_url = "https://api.zoom.us/v2/metrics/meetings?type=live"
    headers = {"Authorization": get_token(config)}
    response = requests.get(api_url, headers=headers)
    host_email = config["aw-watcher-zoom"].get("host_email", None)
    print("response.status_code{} ".format(response.status_code))
    print("response.data{} ".format(response.json()))
    if response.status_code == 200:
        data = response.json()
        print("data {}".format(data))
        meetings = data["meetings"]
        meeting = {}
        for m in meetings:
            if m['email'] == host_email:
                meeting = m
        return meeting
    elif response.status_code == 401:
        global token
        token = ""
        print("refreshing token")
        get_token(config)
        get_meeting(config)
    else:
        return {}
