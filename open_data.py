from rocrate.rocrate import ROCrate # for creating the metadata files
from rocrate.model.preview import Preview # For creating the HTML representation of the ROCrates
import os # for accessing the files
import openpyxl # For opening the excel
import csv # For saving the csv file
import matplotlib.pyplot as plt # For creating a diagram
from dateutil import parser # For handling ISO 8601 strings

# Plans:
# - Split into monthly csvs, from first of the month 00AM to last of the month 11:59PM -
# - Calculate max, min and avg values for readings over the month
# - Create a diagram for temperature and salinity
# - Create an RO-Crate with those values
# - Link up both the raw data and "working data" (decide whether to take readings from one or both?)
# - Include a link in the ro-crate back to the website (or DOI) where this data can be obtained
# - Add notes around the data into RO-Crates for specific sensors and dates


# Globals:
NOTES_FILE = "2020-02-20 Summary working notes on data READ FIRST.xlsx"
RAW_SHEET = "raw data" # Includes this phrase, prefixed by location
WORKING_SHEET = "Working data" # Includes this phrase, prefixed by location

def get_file_name(raw_working,sensor,start_month,start_year,end_month,end_year):
    file_name = "out_" + sensor + "_" + start_month + start_year + "_" + end_month + end_year + "_" + raw_working + ".csv"
    return file_name

def select_sheet(name_part, workbook):
    sheets = workbook.get_sheet_names()
    for sheet_name in sheets:
        if name_part in sheet_name:
            selected_sheet = sheet_name
    if selected_sheet is None:
        print("No sheet found with ",name_part, " in the name")
        return None
    else:
        return selected_sheet

def save_csv_file(sheet,header_row,start_row,end_row,file_name):
    if not os.path.exists(file_name[:-4]):
        os.mkdir(file_name[:-4])
    with open(os.path.join(file_name[:-4],file_name),'w',newline='') as csv_file:
        fw = csv.writer(csv_file)
        fw.writerow(header_row)
        for row in sheet.iter_rows(min_row=start_row, max_row=end_row):
            row_values = []
            for cell in row:
                row_values.append(cell.value)
            fw.writerow(row_values)

def package_data(temperature,salinity,depth,csv_file_name):
    avg_temp = round(sum(temperature)/len(temperature),4)
    min_temp = min(temperature)
    max_temp = max(temperature)
    avg_sal = round(sum(salinity)/len(salinity),4)
    min_sal = min(salinity)
    max_sal = max(salinity)
    avg_dep = round(sum(depth)/len(depth),4)
    min_dep = min(depth)
    max_dep = max(depth)
    plot_data(temperature, csv_file_name[:-4] + "_temperature.png")
    plot_data(depth, csv_file_name[:-4] + "_depth.png")
    plot_data(salinity, csv_file_name[:-4] + "_salinity.png")

# A method which takes in values and saves a (simple) plot of those values in the provided file_name
def plot_data(value_list, file_name):
    plt.plot(value_list)
    plt.savefig(file_name)

def create_monthly_ro_crate(temperature,salinity,depth,csv_file_name):
    crate = ROCrate()
    crate.add_file(csv_file_name) # Adds the file reference to the crate, and will cause it to be saved next to it when written to disk
    crate.write_crate(csv_file_name[:-4])
    preview = Preview(crate) # Create a preview of the crate
    preview.write(csv_file_name[:-4]) # Write that preview out to the same folder


def load_estuary_data(filepath):
    print("Loading data from: ",os.path.join(os.getcwd(),filepath))
    workbook = openpyxl.load_workbook(filepath, read_only=True) # Read-only mode so that it doesn't take up too much memory
    active_sheet_name = select_sheet(RAW_SHEET, workbook)
    if active_sheet_name is None:
        return None
    print("Using sheet: ", active_sheet_name)
    active_sheet = workbook[active_sheet_name]

    header_row = True
    headers = []
    #### Split here?
    first_row= None
    last_row = None
    start_month = None
    start_year = None
    depth = []
    temperature = []
    salinity = []
    # Need to record first row, and then last row of the month, in order to export data
    for row in active_sheet.rows:
        # Deal with the header row
        if header_row:
            print(row)
            header_row = False
            for cell in row:
                headers.append(cell.value)
        else:
            # If this is our first row, set the start values
            if start_month is None:
                start_row = row[0].row
                date = parser.parse(row[headers.index("MeasurementTime")].value)
                if (date is not None):
                    start_month = date.strftime("%B")
                    start_year = date.year
            # Otherwise we want to check if we've moved to a different month yet
            else:
                date = parser.parse(row[headers.index("MeasurementTime")].value)
                # If it is a separate month, save the previous rows
                if date.strftime("%B") != start_month:
                    end_month = date.strftime("%B")
                    end_year = date.year
                    end_row = row[0].row - 1
                    print("Saving rows: ",start_row, " to ", end_row)
                    csv_file_name = get_file_name("RAW","CH_01", str(start_month), str(start_year), str(end_month), str(end_year))
                    print("in file: ", csv_file_name)
                    save_csv_file(active_sheet,headers,start_row,end_row,csv_file_name)


                    create_monthly_ro_crate(temperature,salinity,depth,csv_file_name)
                    # Reset values for the next month
                    start_month = date.strftime("%B")
                    start_year = date.year
                    start_row = row[0].row
                    tempature = []
                    depth = []
                    salinity = []

            # Record the various values for avg, mins and max
            if row[headers.index("Type")].value == "temperature":
                temperature.append(row[headers.index("CurrentValue")].value)
            elif row[headers.index("Type")].value == "water depth":
                depth.append(row[headers.index("CurrentValue")].value)
            elif row[headers.index("Type")].value == "salinity":
                salinity.append(row[headers.index("CurrentValue")].value)
    # Handles final rows
    end_row = active_sheet.max_row
    print("Saving rows: ",start_row, " to ", end_row)
    csv_file_name = get_file_name("RAW","CH_01", str(start_month), str(start_year), str(end_month), str(end_year))
    print("in file: ", csv_file_name)
    save_csv_file(active_sheet,headers,start_row,end_row,csv_file_name)



    print("Min/Max temperature: ",min(temperature), " / ", max(temperature))
    workbook.close() # Need to close since read-only uses "lazy loading"
