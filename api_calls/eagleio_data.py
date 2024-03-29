####
####    Simon Kruik | IT Research | UTS
####    Created 2022-02-11, Updated 2022-02-11
####
import requests
import json
import csv
from io import StringIO # For converting string to file object to use with CSV reader
import os
import sys # For commandline usage
import uuid # Since we need to do generate IDs for rows
from dateutil import parser # For handling and formatting date strings

#### Goal Headers: id, MeasurementTime, SensorName, SensorDescription [location name], SesnorDetails, Type, Units, CurrentValue, Lat, Long

HEADERS = ["id","MeasurementTime","SensorName","SensorDescription","SensorDetails","Type","Units","CurrentValue","Lat","Long"]

locations = {
    "mncm2l301": "Macleay River",
    "mncm2l302": "Hastings River",
    "mncm2l303": "Camden Haven",
    "mncm2l304": "Manning River",
    "mncm2l305": "Port Stephens",
    "mncm2l306": "Georges River - Botany Bay",
    "mncm2l307": "Shoalhaven - Crookhaven Rivers",
    "mncm2l308": "Wagonga Inlet",
    "mncm2l309": "Wapengo Lake",
    "mncm2l30a": "Merimbula Lake",
    "mncm2l30b": "Pambula Lake",
    "mncm2l30c": "Pambula Lake",
    "mncm2l30d": "Wonboyn Lake",
    "mncm2l30bc": "Pambula Lake"
}

sensor_lat_lons = {
    "mncm2l301": (-30.87605,153.012318),
    "mncm2l302": (-31.40406,152.89172),
    "mncm2l303": (-31.64478,152.82822),
    "mncm2l304": (-31.89088,152.60981),
    "mncm2l305": (-32.680705,152.123935),
    "mncm2l306": (-34.02245,151.176),
    "mncm2l307": (-34.9118,150.74158),
    "mncm2l308": (-36.22161,150.07128),
    "mncm2l309": (-36.60182,150.01678),
    "mncm2l30a": (-36.896499,149.890421),
    "mncm2l30b": (-36.9652248,149.891757),
    "mncm2l30c": (-36.9652248,149.891757),
    "mncm2l30d": (-37.24121,149.92724),
    "mncm2l30bc": (-36.9652248,149.891757),
}


sub_folder = os.path.join(os.path.dirname(__file__),"ict_data") # Set folder path to beside current file, in folder ict_data
api_key = ""
api_url = "https://api.data.ictinternational.com/api/v1/"
devices_endpoint = "nodes/"

def get_lat_lon_from_sensor_name(sensor_name):
    for sensor_id, lat_lon in sensor_lat_lons.items():
        if sensor_id in sensor_name:
            return lat_lon
    return None

def get_location_from_sensor_name(sensor_name):
    for sensor_id, location_name in locations.items():
        if sensor_id in sensor_name:
            return location_name

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

def load_api_key():
    global api_key
    with open(os.path.join(os.path.dirname(__file__),"eagleio_key.secret"),"r") as file:
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
    query_params = [("attr","name,_id"),("filter","name($match:temperature)|name($match:salinity)|name($match:H2O)|name($match:DO)|name($match:pH)|name($match:Rainfall)|name($match:Temperature)")] # Filter for just temp, salinity and depth devices and show name and id
    devices = json.loads(api_get(devices_endpoint,query_params))
    for device in devices:
        device_id_list.append((device["_id"],device["name"]))
    return device_id_list

def check_devices(): # A function to check which devices are associated with a location, and which aren't matched to anything
    device_list = []
    unmatched_device_list = []
    total_matched_devices = 0
    query_params = [("attr","name,_id"),("filter","name($match:temperature)|name($match:salinity)|name($match:H2O)|name($match:DO)|name($match:pH)|name($match:Rainfall)|name($match:Temperature)")] # Filter for just temp, salinity and depth devices and show name and id
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

def get_device_endpoint(device_id):
    return "nodes/" +  device_id + "/historic"

def get_historical_readings(device_id, start_date, end_date): ### TODO: Change from insitu to eagleio
    readings_matrix = []
    #print("startTime",start_date)
    #print("endTime",end_date)
    query_params = [("startTime",start_date),("endTime",end_date),("format","csv")]
    endpoint = get_device_endpoint(device_id)
    readings_string = api_get(endpoint, query_params)
    csv_file = StringIO(readings_string)
    reader = csv.reader(csv_file, delimiter=",")
    for row in reader:
        readings_matrix.append(row)
    return readings_matrix

def get_multiple_readings(start_date, end_date, device_list, location_name): # Expects device_list in format [(dev_id, name), (dev_id,name)]
    results_dict = {}
    for (device_id, name) in device_list:
        name = name.lower()
        results = get_historical_readings(device_id, start_date, end_date)
        if "air temp" in name:
            results_dict["amb_temp"] = results
        elif "salinity" in name:
            results_dict["salinity"] = results
        elif "mh2o" in name and "AHD" not in name and "TIDE" not in name:
            results_dict["water_level"] = results
        elif "oxygen mgl" in name:
            results_dict["DO"] = results
        elif "temp" in name:
            results_dict["temp"] = results
        elif "ph" in name:
            results_dict["pH"] = results
        elif "rainfall last 24 hrs" in name:
            results_dict["rainfall"] = results
    print("Results includes ", results_dict.keys())
    readings_list = join_readings(location_name, HEADERS,results_dict.get("temp"),results_dict.get("salinity"),results_dict.get("water_level"),results_dict.get("amb_temp"),results_dict.get("rainfall"),results_dict.get("pH"),results_dict.get("DO"))
    return readings_list

def build_row(header_row, time_value_row, sensor_name, endpoint, units, reading_type):
    indexes = {}
    result_row = []
    indexes[header_row.index("id")] = uuid.uuid4().int
    indexes[header_row.index("MeasurementTime")] = time_value_row[0]
    indexes[header_row.index("SensorName")] = sensor_name
    indexes[header_row.index("SensorDescription")] = get_location_from_sensor_name(sensor_name)
    indexes[header_row.index("SensorDetails")] = endpoint
    indexes[header_row.index("Type")] = reading_type
    indexes[header_row.index("Units")] = units
    #print(units)
    indexes[header_row.index("CurrentValue")] = time_value_row[1]
    (lat, lon) = get_lat_lon_from_sensor_name(sensor_name)
    indexes[header_row.index("Lat")] = lat
    indexes[header_row.index("Long")] = lon
    new_dict = dict(sorted(indexes.items()))
    for index, value in new_dict.items():
        result_row.insert(index,value)
    return result_row


def join_readings(location_name, header_row, temp, salinity, water_level, amb_temp=None, rainfall=None, pH=None, DO=None):
    # Need to add all of them, sort by date_time, and then spit it all out in a CSV
    readings_matrix = []
    if temp:
        for row in temp[3:]:
            new_row = build_row(HEADERS, row, temp[1][1], get_device_endpoint(temp[0][1]), temp[2][1], "temperature")
            readings_matrix.append(new_row)

    if salinity:
        for row in salinity[3:]:
            new_row = build_row(HEADERS, row, salinity[1][1], get_device_endpoint(salinity[0][1]), salinity[2][1], "salinity")
            readings_matrix.append(new_row)
    if water_level:
        for row in water_level[3:]:
            #print(water_level[1])
            new_row = build_row(HEADERS, row, water_level[1][1], get_device_endpoint(water_level[0][1]), water_level[2][1], "depth")
            readings_matrix.append(new_row)
    if amb_temp:
        for row in amb_temp[3:]:
            new_row = build_row(HEADERS, row, amb_temp[1][1], get_device_endpoint(amb_temp[0][1]), amb_temp[2][1], "air temperature")
            readings_matrix.append(new_row)
    if rainfall:
        for row in rainfall[3:]:
            new_row = build_row(HEADERS, row, rainfall[1][1], get_device_endpoint(rainfall[0][1]), rainfall[2][1], "rainfall 24hrs")
            readings_matrix.append(new_row)
    if pH:
        for row in pH[3:]:
            new_row = build_row(HEADERS, row, pH[1][1], get_device_endpoint(pH[0][1]), pH[2][1], "pH")
            readings_matrix.append(new_row)
    if DO:
        for row in DO[3:]:
            new_row = build_row(HEADERS, row, DO[1][1], get_device_endpoint(DO[0][1]), DO[2][1], "DO")
            readings_matrix.append(new_row)
    readings_matrix = sorted(readings_matrix, key=lambda x:x[1])
    readings_matrix.insert(0,HEADERS)
    return readings_matrix


def write_months_readings_old(start_date,end_date):
    devices = get_devices()
    for device_tuple in devices:
        readings_matrix = get_historical_readings(device_tuple[0], start_date, end_date)
        header_rows = readings_matrix[:3]
        readings_matrix = readings_matrix[3:] # Remove header rows
        device_endpoint = get_device_endpoint(device_tuple[0])
        device_name = device_tuple[1]
        with open(os.path.join(sub_folder,'out_' + device_name + "_" + start_date + "_" + end_date + '.csv'),'w',encoding="utf-8-sig") as file: # Was trying encodings to get of Â prepended to degree symbol in file
            #file.write('''Id,MeasurementTime,SensorName,SensorDescription,SensorDetails,Type,Units,CurrentValue,Lat,Long\n''')
            for row in header_rows:
                file.write(','.join(str(col) for col in row))
                file.write('\n')
            for original_row in readings_matrix:
            #rows = split_readings(original_row, device_station, device_endpoint,locations[device_station], sensor_lat_lons[device_station][0],sensor_lat_lons[device_station][1],1,0,4,5,6,7,8)
                file.write(','.join(str(col) for col in original_row))
                file.write('\n')

def list_sensors():
    devices = get_devices()
    loc_devices = {}
    for sensor_code, loc_name in locations.items():
        loc_devices[sensor_code] = []
    for device_id, device_name in devices:
        for sensor_code, loc in locations.items():
            if sensor_code in device_name:
                loc_devices[sensor_code].append((device_id, device_name))
    for key, val in loc_devices.items():
        print("Location",locations[key])
        for id,name in val:
            print("  ","Sensor_type",name,"id",id)

def write_months_readings(start_date,end_date):
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
            write_readings(parse_month_year(incremented_month,year),parse_month_year(incremented_month+1,year))
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
    start_year = str(parser.parse(start_date).year)
    start_month = str(parser.parse(start_date).strftime("%B"))
    end_year = str(parser.parse(end_date).year)
    end_month = str(parser.parse(end_date).strftime("%B"))
    start_date = str(parser.parse(start_date).isoformat()) + "Z" # Converts to full ISO 8601 Timestamp for API compatibility
    end_date = str(parser.parse(end_date).isoformat()) + "Z" # Converts to full ISO 8601 Timestamp for API compatibility
    devices = get_devices()
    loc_devices = {}
    for sensor_code, loc_name in locations.items():
        loc_devices[sensor_code] = []
    for device_id, device_name in devices:
        for sensor_code, loc in locations.items():
            if sensor_code in device_name:
                loc_devices[sensor_code].append((device_id, device_name))

    # Needed because pambula lake has both mncm2l30b and mncm2l30c
    loc_devices["mncm2l30bc"] = loc_devices["mncm2l30b"] + loc_devices["mncm2l30c"]
    loc_devices.pop("mncm2l30b")
    loc_devices.pop("mncm2l30c")

    for key, val in loc_devices.items():
        print("Fetching device readings for ",locations[key])
        location_readings = get_multiple_readings(start_date, end_date, val, key)
        print("Writing CSV for: ", locations[key])

        with open(os.path.join(sub_folder,'out_NSW_' + key + "_" + start_month + start_year + "_" + end_month + end_year + "_RAW" + '.csv'),'w') as file:
            for row in location_readings:
                file.write(','.join(str(col) for col in row))
                file.write('\n')
        #for id,name in val:
            #print("  ","Sensor_type",name,"id",id)
    #print(loc_devices)
    #
    #
    # for device_tuple in devices:
    #     readings_matrix = get_historical_readings(device_tuple[0], start_date, end_date)
    #     header_rows = readings_matrix[:3]
    #     readings_matrix = readings_matrix[3:] # Remove header rows
    #     device_endpoint = get_device_endpoint(device_tuple[0])
    #     device_name = device_tuple[1]
    #     with open(os.path.join(sub_folder,'out_' + device_name + "_" + start_date + "_" + end_date + '.csv'),'w') as file:
    #         #file.write('''Id,MeasurementTime,SensorName,SensorDescription,SensorDetails,Type,Units,CurrentValue,Lat,Long\n''')
    #         for row in header_rows:
    #             file.write(','.join(str(col) for col in row))
    #             file.write('\n')
    #         for original_row in readings_matrix:
    #         #rows = split_readings(original_row, device_station, device_endpoint,locations[device_station], sensor_lat_lons[device_station][0],sensor_lat_lons[device_station][1],1,0,4,5,6,7,8)
    #             file.write(','.join(str(col) for col in original_row))
    #             file.write('\n')

if __name__ == "__main__":
    print("Running from command line")
    #print(sys.argv)
    print("Usage: python eagleio_data.py <Start_Year [2020] > <Start_Month [4] > <End_Year [2022] > <End_Month [11] >")
    if len(sys.argv) != 5:
        print("Incorrect number of arguments present, ", len(sys.argv)," see above instructions")
    else:
        start_date = parse_month_year(sys.argv[2],sys.argv[1])
        end_date = parse_month_year(sys.argv[4],sys.argv[3])
        print("Starting from", start_date)
        print("Ending at", end_date)

        write_months_readings(start_date,end_date)
        #join_readings()
