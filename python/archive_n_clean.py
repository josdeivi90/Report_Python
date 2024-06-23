import getopt
import sys
import os
from shutil import copy
from datetime import datetime, timezone

from utils.json_file_da import load_json_data, write_to_json

def archive_data(data_file, audit_file, notes_file, html_file, year, month, archive_path):
    fullpath = archive_path + "/" + str(year) + "/" + str(month) + "/"
    if not os.path.exists(fullpath):
        os.makedirs(fullpath)
    copy(data_file, fullpath)
    copy(audit_file, fullpath)
    copy(notes_file, fullpath)
    copy(html_file, fullpath)


def remove_month(data, year, month):
    for block in data:
        if (block['month'] == month) and (block['year'] == year):
            data.remove(block)
    return data 

def main():
    argv = sys.argv[1:]

    data_file = "./data/json_data.json"
    audit_file = "./data/audit_data.json"
    notes_file = "./data/notes.json"
    html_file = "./report/index.html"
    archive_path = "./archive"
    archive_month = int(datetime.now(timezone.utc).strftime('%m'))
    archive_year = int(datetime.now(timezone.utc).strftime('%y'))+2000

    try:
        opts, args = getopt.getopt(argv, "d:m:y:p", ['data=', 'archive_month=', 'archive_year=', 'archive_path='])
    except getopt.GetoptError:
        print('archive_n_clean.py -d <input data>  -m <month to archive> -y <year to archive> -p <archive path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('archive_n_clean.py -d <input data>  -m <month to archive>  -y <year to archive> -p <archive path>')
            sys.exit()
        elif opt in ("-m", "--archive_month"):
            archive_month = int(arg)
        elif opt in ("-y", "--archive_year"):
            archive_year = int(arg)
        elif opt in ("-p", "--archive_path"):
            archive_path = arg

    if archive_month < 6:
        clear_year = archive_year - 1
        clear_month = archive_month + 7
    else:
        clear_year = archive_year
        clear_month = archive_month - 5

    #archive data files into archive folder
    print ("archiving data for " + str(archive_month) + "/" + str(archive_year) + " to " + archive_path)
    archive_data(data_file, audit_file, notes_file, html_file, archive_year, archive_month, archive_path)

    #remove data for 6 months ago from json_data
    data = load_json_data(data_file)
    print ("removing data for " + str(clear_month) + "/" + str(clear_year) + " from " + data_file)
    newdata = remove_month(data, clear_year, clear_month)

    utc_now_dt = datetime.now(timezone.utc).strftime("%m/%d/%Y, %H:%M:%S")
    output_dict = {
        'datetime' : utc_now_dt,
        'data' : newdata
    }

    print ("writing data to " + data_file)
    write_to_json(data_file,output_dict)


if __name__ == "__main__":
    main()
