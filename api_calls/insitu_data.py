####
####    Simon Kruik | IT Research | UTS
####    Created 2022-02-11, Updated 2022-02-11
####
import requests
import json

locations = {
    "A1B":"",
    "A2":"",
    "A3":"",
    "A4":""
}

sensor_lat_lons = {
    "A1B": (-34.964233, 117.955450),
    "A2": (-34.973600, 117.959117),
    "A3": (-34.972117, 117.969433),
    "A4": (-34.986217, 117.956850)
}

api_key = ""
api_url = "https://api.insitumarineoptics.com/v1/"
devices_endpoint = "devices"


def load_api_key():
    global api_key
    with open("insitu_key.secret","r") as file:
        api_key = file.read().strip()
    return api_key

def api_get(endpoint,query_params=None):
    if api_key == "":
        load_api_key()
    url = api_url + endpoint
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.request("GET", url, headers=headers,params=query_params)
    if response.status_code == 200:
        return response.text
    else:
        print("Error with API call")
        print(response.status_code)
        print(response.text)
    return None

def get_devices():
    device_id_list = []
    devices = json.loads(api_get(devices_endpoint))
    for device in devices:
        device_id_list.append(device["device_id"])
    return device_id_list

def get_historical_readings(device_id, start_date, end_date):
    query_params = [("date_from",start_date),("date_to",end_date),("format","csv")]
    endpoint = "devices/" +  device_id + "/readings"
    readings = api_get(endpoint, query_params)
    return readings

def write_months_readings(start_date,end_date):
    devices = get_devices()
    for device_id in devices:
        readings_string = get_historical_readings(device_id, start_date, end_date)
        with open('out_WA_' + device_id + "_" + start_date + "_" + end_date + '.csv','w') as file:
            file.write(readings_string)
