####
####    Simon Kruik | IT Research | UTS
####    Created 2022-02-11, Updated 2022-02-11
####
import requests
import json
import csv
from io import StringIO # For converting string to file object to use with CSV reader
import os
import sys # For passing command line arguments
from dateutil import parser # For handling date strings

#### Goal Headers: id, MeasurementTime, SensorName, SensorDescription [location name], SesnorDetails, Type, Units, CurrentValue, Lat, Long


locations = {
    "A1B":"Oyster Harbour North",
    "A2":"Oyster Harbour Central",
    "A3":"Oyster Harbour East",
    "A3B":"Oyster Harbour East",
    "A4":"Oyster Harbour South"
}

sensor_lat_lons = {
    "A1B": (-34.964233, 117.955450),
    "A2": (-34.973600, 117.959117),
    "A3": (-34.972117, 117.969433),
    "A3B": (-34.972117, 117.969433),
    "A4": (-34.986217, 117.956850)
}

sub_folder = os.path.join(os.path.dirname(__file__),"insitu_data") # Set folder path to beside current file, in folder insitu_data
api_key = ""
api_url = "https://api.insitumarineoptics.com/v1/"
devices_endpoint = "devices"


def load_api_key():
    global api_key
    with open(os.path.join(os.path.dirname(__file__),"insitu_key.secret"),"r") as file:
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
        if "ctd" in device["device_id"]: # I can't handle PHIDO currently, talk to me later
            device_id_list.append((device["device_id"],device["station_name"]))
    return device_id_list

def get_device_endpoint(device_id):
    return "devices/" +  str(device_id) + "/readings"

def get_historical_readings(device_id, start_date, end_date):
    readings_matrix = []
    query_params = [("date_from",start_date),("date_to",end_date),("format","csv")]
    print("Getting readings from ", device_id, ", start date: ", start_date, ", end date: ", end_date)
    endpoint = get_device_endpoint(device_id)
    readings_string = api_get(endpoint, query_params)
    csv_file = StringIO(readings_string)
    reader = csv.reader(csv_file, delimiter=",")
    for row in reader:
        readings_matrix.append(row)
    return readings_matrix

def get_header_row(device_id, start_date, end_date):
    readings_matrix = []
    query_params = [("date_from",start_date),("date_to",end_date),("format","csv")]
    endpoint = get_device_endpoint(device_id)
    readings_string = api_get(endpoint, query_params)
    csv_file = StringIO(readings_string)
    reader = csv.reader(csv_file, delimiter=",")
    for row in reader:
        return row


def split_readings(row, device, endpoint, location_name, lat, long, id_index, time_index,depth_index,temp_index,conductivity_index,salinity_index,water_density_index):
    salinity_row = [row[id_index],row[time_index],device,location_name,endpoint,"salinity","parts per thousand",row[salinity_index],lat,long]
    depth_row = [row[id_index],row[time_index],device,location_name,endpoint,"depth","mH2O",row[depth_index],lat,long]
    temp_row = [row[id_index],row[time_index],device,location_name,endpoint,"temperature","degrees Celsius",row[temp_index],lat,long]
    conductivity_row = [row[id_index],row[time_index],device,location_name,endpoint,"conductivity","millisiemens per meter",row[conductivity_index],lat,long]
    water_density_row = [row[id_index],row[time_index],device,location_name,endpoint,"water density","grams per Litre",row[water_density_index],lat,long]
    return [salinity_row,depth_row,temp_row,conductivity_row,water_density_row]

def write_months_readings(start_date, end_date):
    start_date_list = start_date.split('-')
    end_date_list = end_date.split('-')
    start_year = start_date_list[0]
    start_month = int(start_date_list[1])
    end_year = int(end_date_list[0])
    end_month = int(end_date_list[1])
    year = int(start_year)
    month = start_month
    while year < end_year:
        for incremented_month in range(int(month),12):
            write_readings(parse_month_year(incremented_month, year),parse_month_year(incremented_month+1,year))
        write_readings(parse_month_year(12,year),parse_month_year(1,year+1)) # Handling the year change
        year = year + 1
        month = 1
    if (int(year) != int(start_year)): # i.e. Goes over the year break:
        for incremented_month in range(1,end_month):
            write_readings(parse_month_year(incremented_month, year),parse_month_year(incremented_month+1,year))
    else:
        for incremented_month in range(start_month,end_month):
            write_readings(parse_month_year(incremented_month, year),parse_month_year(incremented_month+1,year))

def write_readings(start_date,end_date):
    devices = get_devices()
    start_year = str(parser.parse(start_date).year)
    start_month = str(parser.parse(start_date).strftime("%B"))
    end_year = str(parser.parse(end_date).year)
    end_month = str(parser.parse(end_date).strftime("%B"))
    for device_tuple in devices:
        readings_matrix = get_historical_readings(device_tuple[0], start_date, end_date)
        if len(readings_matrix) > 0:
            header_row = readings_matrix[:1][0]
            print(header_row)
            readings_matrix = readings_matrix[1:] # Remove header row
            device_endpoint = get_device_endpoint(device_tuple[0])
            device_station = device_tuple[1]
            with open(os.path.join(sub_folder,'out_WA_' + device_station + "_" + start_month + start_year + "_" + end_month + end_year + "_RAW" + '.csv'),'w') as file:
                file.write('''Id,MeasurementTime,SensorName,SensorDescription,SensorDetails,Type,Units,CurrentValue,Lat,Long\n''')
                for original_row in readings_matrix:
                    rows = split_readings(original_row, device_station, device_endpoint,locations[device_station], sensor_lat_lons[device_station][0],sensor_lat_lons[device_station][1],header_row.index("telemetry_session_id"),header_row.index("created_at"),header_row.index("depth"),header_row.index("water_temperature"),header_row.index("conductivity"),header_row.index("salinity"),header_row.index("water_density"))
                    for new_row in rows:
                        file.write(','.join(str(col) for col in new_row))
                        file.write('\n')

def parse_month_year(month, year):
    if int(month) in range(1,13):
        if int(year) in range(1970,2100):
            if month in range(1,10):
                return str(year) + "-0" + str(int(month)) + "-01"
            else:
                return str(year) + "-" + str(month) + "-01"
        else:
            print("Year in wrong format: " + year, " should be in YYYY.")
    else:
        print("Month in wrong format: " + month, " should be in MM.")
    return None



if __name__ == "__main__":
    print("Running from command line")
    #print(sys.argv)
    print("Usage: python insitu_data.py <Start_Year [2020] > <Start_Month [4] > <End_Year [2022] > <End_Month [11] >")
    if len(sys.argv) != 5:
        print("Incorrect number of arguments present, ", len(sys.argv)," see above instructions")
    else:
        start_date = parse_month_year(sys.argv[2],sys.argv[1])
        end_date = parse_month_year(sys.argv[4],sys.argv[3])
        print("Starting from", start_date)
        print("Ending at", end_date)
        write_months_readings(start_date,end_date)
