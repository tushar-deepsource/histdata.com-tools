import os
import sys
import csv
import re
from math import ceil
import multiprocessing
from datetime import datetime
import pytz
import yaml
from rich.progress import TextColumn
from rich.progress import BarColumn
from rich.progress import TimeElapsedColumn


def get_month_from_datemonth(datemonth):
    return datemonth[-2:] if datemonth is not None and len(datemonth) > 4 else ""


def get_year_from_datemonth(datemonth):
    return datemonth[:4] if datemonth is not None else ""


def get_query_string(url):
    return url.split('?')[1].split('/')


def create_full_path(path_str):
    if not os.path.exists(path_str):
        os.makedirs(path_str)


def set_working_data_dir(data_dirname):
    return f"{os.getcwd()}{os.sep}{data_dirname}{os.sep}"


def load_influx_yaml():

    if os.path.exists('influxdb.yaml'):
        with open('influxdb.yaml', 'r') as file:
            try:
                yamlfile = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
                sys.exit()
        return yamlfile

    print(""" ERROR: -I flag is used to import data to a influxdb instance...
                        there is no influxdb.yaml file in working directory.
                        did you forget to set it up?
          """)
    sys.exit()


def get_current_datemonth_gmt_plus5():
    now = datetime.now().astimezone()
    gmt_plus5 = now.astimezone(pytz.timezone("Etc/GMT+5"))
    return f"{gmt_plus5.year}{gmt_plus5.strftime('%m')}"


def get_progress_bar(progress_string):

    return \
        TextColumn(text_format=progress_string), \
        BarColumn(),\
        "[progress.percentage]{task.percentage:>3.0f}%", \
        TimeElapsedColumn()


def get_csv_dialect(csv_path):
    with open(csv_path, "r") as srccsv:
        dialect = csv.Sniffer().sniff(srccsv.read(), delimiters=",; ")
    return dialect


def replace_date_punct(datemonth_str):
    """removes year-month punctuation and returns str("000000")"""
    return re.sub("[-_.: ]", "", datemonth_str) if datemonth_str is not None else ""


def get_pool_cpu_count(count=None):

    try:
        real_vcpu_count = multiprocessing.cpu_count()

        if count is None:
            count = real_vcpu_count
        else:
            err_text_cpu_level_err = \
            f"""
                    ERROR on -c {count}  ERROR
                        * Malformed command:
                            - -c cpu must be str: low, medium, or high. or integer percent 1-200
            """
            count = str(count)
            match count:
                case "low":
                    count = ceil(real_vcpu_count / 2.5)
                case "medium":
                    count = ceil(real_vcpu_count / 1.5)
                case "high":
                    count = real_vcpu_count
                case _:
                    if count.isnumeric() and 1 <= int(count) <= 200:
                        count =  ceil(real_vcpu_count * (int(count) / 100))
                    else:
                        raise ValueError(err_text_cpu_level_err)

        return count - 1 if count > 2 else ceil(count / 2)
    except ValueError as err:
        print(err)
        sys.exit(err)