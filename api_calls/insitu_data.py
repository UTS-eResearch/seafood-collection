####
####    Simon Kruik | IT Research | UTS
####    Created 2022-02-11, Updated 2022-02-11
####
import requests
import json
import csv
from io import StringIO # For converting string to file object to use with CSV reader

#### Goal Headers: id, MeasurementTime, SensorName, SensorDescription [location name], SesnorDetails, Type, Units, CurrentValue, Lat, Long


locations = {
    "A1B":"Oyster Harbour North",
    "A2":"Oyster Harbour Central",
    "A3":"Oyster Harbour East",
    "A4":"Oyster Harbour South"
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
    readings_matrix = []
    query_params = [("date_from",start_date),("date_to",end_date),("format","csv")]
    endpoint = "devices/" +  device_id + "/readings"
    readings_string = api_get(endpoint, query_params)
    csv_file = StringIO(readings_string)
    reader = csv.reader(csv_file, delimiter=",")
    for row in reader:
        readings.append(row)
    return readings_matrix

def print_header_row(device_id, start_date, end_date):
    readings_matrix = []
    query_params = [("date_from",start_date),("date_to",end_date),("format","csv")]
    endpoint = "devices/" +  device_id + "/readings"
    readings_string = api_get(endpoint, query_params)
    csv_file = StringIO(readings_string)
    reader = csv.reader(csv_file, delimiter=",")
    for row in reader:
        print(row)
        break

def split_readings(row, device, endpoint, location_name, lat, long, id_index, time_index,depth_index,temp_index,conductivity_index,salinity_index,water_density_index):
    salinity_row = [row[id_index],row[time_index],device,location_name,endpoint,"salinity","parts per thousand",row[salinity_index],lat,long]
    depth_row = [row[id_index],row[time_index],device,location_name,endpoint,"depth","mH2O",row[depth_index],lat,long]
    temp_row = [row[id_index],row[time_index],device,location_name,endpoint,"temperature","degrees Celsius",row[temp_index],lat,long]
    conductivity_row = [row[id_index],row[time_index],device,location_name,endpoint,"conductivity","millisiemens per meter",row[conductivity_index],lat,long]
    water_density_row = [row[id_index],row[time_index],device,location_name,endpoint,"water density","grams per Litre",row[water_density_index],lat,long]
    return [salinity_row,depth_row,temp_row,conductivity_row,water_density_row]

def write_months_readings(start_date,end_date):
    devices = get_devices()
    for device_id in devices:
        readings_matrix = get_historical_readings(device_id, start_date, end_date)
        with open('out_WA_' + device_id + "_" + start_date + "_" + end_date + '.csv','w') as file:
            for row in readings_matrix:
                file.write(','.join(row))
                file.write('\n')
