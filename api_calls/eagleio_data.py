####
####    Simon Kruik | IT Research | UTS
####    Created 2022-02-11, Updated 2022-02-11
####
import requests
import json



locations = {
    "mncm2l303": "Camden Haven",
    "mncm2l306": "Georges River - Botany Bay",
    "mncm2l302": "Hastings River",
    "mncm2l301": "Macleay River",
    "mncm2l304": "Manning River",
    "mncm2l30a": "Merimbula Lake",
    "mncm2l30c": "Pambula Lake",
    "mncm2l30b": "Pambula Lake",
    "mncm2l305": "Port Stephens",
    "mncm2l307": "Shoalhaven - Crookhaven Rivers",
    "mncm2l308": "Wagonga Inlet",
    "mncm2l309": "Wapengo Lake",
    "mncm2l30d": "Wonboyn Lake"
}

sensor_lat_lons = {
    "mncm2l303": "",
    "mncm2l306": "",
    "mncm2l302": "",
    "mncm2l301": "",
    "mncm2l304": "",
    "mncm2l30a": "",
    "mncm2l30c": "",
    "mncm2l305": "",
    "mncm2l307": "",
    "mncm2l308": "",
    "mncm2l309": "",
    "mncm2l30d": ""
}


api_key = ""
api_url = "https://api.data.ictinternational.com/api/v1/"
devices_endpoint = "nodes/"

def load_api_key():
    global api_key
    with open("eagleio_key.secret","r") as file:
        api_key = file.read().strip()
    return api_key


def api_get(endpoint,query_params=None):
    if api_key == "":
        load_api_key()
    url = api_url + endpoint
    headers = {"X-Api-Key": api_key}
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
    query_params = [("attr","name,_id"),("filter","name($match:temperature)|name($match:salinity)|name($match:H2O)")] # Filter for just temp, salinity and depth devices and show name and id
    devices = json.loads(api_get(devices_endpoint,query_params))
    for device in devices:
        device_id_list.append(device["_id"])
    return device_id_list

def check_devices(): # A function to check which devices are associated with a location, and which aren't matched to anything
    device_list = []
    unmatched_device_list = []
    total_matched_devices = 0
    query_params = [("attr","name,_id"),("filter","name($match:temperature)|name($match:salinity)|name($match:H2O)")] # Filter for just temp, salinity and depth devices and show name and id
    devices = json.loads(api_get(devices_endpoint,query_params))
    for device in devices:
        device_list.append(device["name"])
    unmatched_device_list = device_list.copy()
    for key,val in locations.items():
        #print("key",key)
        key_count = 0
        for name in device_list:
            #print("Comparing:",key,"to",name)
            if key in name:
                #print("Sensor: ", name, " matches location key: ", key)
                key_count += 1
                unmatched_device_list.remove(name)
        print(val, " count: ", key_count)
        total_matched_devices += key_count
    print("Missing devices:", len(device_list), "-",total_matched_devices,'=', len(device_list)-total_matched_devices)
    print(unmatched_device_list)
    return device_list

def get_historical_readings(device_id, start_date, end_date): ### TODO: Change from insitu to eagleio
    query_params = [("startTime",start_date),("endTime",end_date),("format","csv")]
    endpoint = "nodes/" +  device_id + "/historic"
    readings = api_get(endpoint, query_params)
    return readings
