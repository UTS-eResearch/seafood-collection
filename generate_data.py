import os
import re

from templates.ro_crate_template import RO_CRATE_TEMPLATE
from templates.file_template import FILE_TEMPLATE

MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
MONTH_NUMBERS = {"January":"01","February":"02","March":"03","April":"04","May":"05","June":"06","July":"07","August":"08","September":"09","October":"10","November":"11","December":"12"}
YEARS = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020"]
PLACES = ["Camden Haven","Clyde River","Georges River","Hawkesbury River","Hastings River","Manning River","Pambula Lake","Pambula Lake","Port Stephens","Shoalhaven Crookhaven Rivers","Wagonga Inlet","Wallis Lake","Wonboyn Lake","Wapengo Lake"]
PLACE_CODES = {"Camden Haven":"CH","Clyde River":"CLY","Georges River":"GR","Hawkesbury River":"HR","Hastings River":"HR","Manning River":"Man","Pambula Lake":"PAM","Port Stephens":"PS","Shoalhaven Crookhaven Rivers":"SH","Wagonga Inlet":"WAG","Wallis Lake":"WAL","Wonboyn Lake":"WON","Wapengo Lake":"WPG"}
PLACE_LOCATIONS = {"Camden Haven":"https://sws.geonames.org/8210175/","Clyde River":"https://sws.geonames.org/2171249/","Georges River":"https://sws.geonames.org/2205884/","Hawkesbury River":"https://sws.geonames.org/2205605/","Hastings River":"https://sws.geonames.org/2163834/","Manning River":"https://sws.geonames.org/2158850/","Pambula Lake":"https://sws.geonames.org/8594508/","Port Stephens":"https://sws.geonames.org/9409163/","Shoalhaven Crookhaven Rivers":"https://sws.geonames.org/2149595/","Wagonga Inlet":"https://sws.geonames.org/2207090/","Wallis Lake":"https://sws.geonames.org/8539070/","Wonboyn Lake":"https://sws.geonames.org/8210771/","Wapengo Lake":"https://sws.geonames.org/8594517/"}
LAT_LONG = {"Camden Haven":["-31.64478","152.82822"],"Clyde River":["-35.70093","150.13341"],"Georges River":["-34.02245","151.176"],"Hawkesbury River":["-33.5443","151.1365167"],"Hastings River":["-31.40406","152.89172"],"Manning River":["-31.89088","152.63981"],"Pambula Lake":["-36.96811903","149.884795"],"Port Stephens":["-32.7196","152.06093"],"Shoalhaven Crookhaven Rivers":["-34.9118","150.74158"],"Wagonga Inlet":["-36.22161","150.07128"],"Wallis Lake":["-32.18268","152.47556"],"Wonboyn Lake":["-37.24121","149.92724"],"Wapengo Lake":["-36.60182","150.01678"]}


def write_new_data(directory):
    for year in YEARS:
        for month in MONTHS:
            for place in PLACES:
                folder_name = "Estuary Data - " + year + " " + month + " - " + place
                folder_name = os.path.join(directory,folder_name)
                if not os.path.isdir(folder_name):
                    os.mkdir(folder_name)
                    file_name = write_new_data_folder(folder_name,month,MONTH_NUMBERS[month],year,place,PLACE_CODES[place])
                    ro_file_name = write_new_ro_crate_metadata_file(folder_name,year,month,MONTH_NUMBERS[month],place,file_name)


def write_new_data_folder(directory,month_name, month_number,year,place,place_code):
    folder = "Data"
    file_name = "out_NSW_" + place_code + "_01_"+ month_name + year + ".csv"
    folder_path = os.path.join(directory,folder)
    file_path = os.path.join(directory,folder, file_name)
    os.mkdir(folder_path)
    with open(file_path,'w') as file:
        data = FILE_TEMPLATE
        data = re.sub(r'2020-06', year + "-" + month_number,data)
        data = re.sub(r'NSW_CH_01',"NSW_" + place_code +"_01", data)
        data = re.sub(r'Camden Haven',place,data) # Should also replace lat's and longs
        file.write(data)
    return file_name

def write_new_ro_crate_metadata_file(directory, year, month_name,month_number, place_name, data_file_name):
    file_name = "ro-crate-metadata.json"
    file_path = os.path.join(directory,file_name)
    lat = LAT_LONG[place_name][0]
    long = LAT_LONG[place_name][1]

    with open(file_path,'w') as file:
        data = RO_CRATE_TEMPLATE
        data = re.sub(r'2020-07-15',year + "-" + month_number + "-30",data)
        data = re.sub(r'Camden Haven', place_name, data)
        data = re.sub(r'June 2020', month_name+" " + year, data)
        data = re.sub(r'2020-06',year + "-" + month_number,data)
        data = re.sub(r'August',month_name,data)
        data = re.sub(r'out_NSW_CH_01_June2020\.csv', data_file_name, data)
        data = re.sub(r'https://sws.geonames.org/8210175/',PLACE_LOCATIONS[place_name],data)
        data = re.sub(r'-31\.6485',lat,data)
        data = re.sub(r'152\.8346',long,data)
        file.write(data)
    return file_name


if __name__ == "__main__":
    directory = os.getcwd()
    generated_data_dir = 'sensor-data'
    os.mkdir(generated_data_dir)
    write_new_data(os.path.join(directory,generated_data_dir))
