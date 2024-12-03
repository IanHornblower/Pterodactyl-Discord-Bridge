import requests
from keys import *
from server import Server

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def get_raw_json():
    url = f'{PANEL_URL}/api/client'
    response = requests.get(url, headers=headers)
    return response.json()

def get_servers_json():
    return get_raw_json()['data']

def get_server_status(server_id):
    url = f'{PANEL_URL}/api/client/servers/{server_id}/resources'
    response = requests.get(url, headers=headers)
    return response.json()

def get_servers():
    servers = []

    servers_json = get_servers_json()

    for json in servers_json:
        servers.append(Server(json, get_server_status))

    return servers

def start_server(server_id):
    response = requests.post(f"{PANEL_URL}/api/client/servers/{server_id}/power", headers=headers, json={"signal": "start"})

    return response.status_code

def stop_server(server_id):
    response = requests.post(f"{PANEL_URL}/api/client/servers/{server_id}/power", headers=headers, json={"signal": "stop"})

    return response.status_code

def kill_server(server_id):
    response = requests.post(f"{PANEL_URL}/api/client/servers/{server_id}/power", headers=headers, json={"signal": "kill"})

    return response.status_code