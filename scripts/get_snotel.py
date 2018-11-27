import pandas as pd
import fiona
import datetime


def __read_snotel_stations(json_file):
    """
    Reads the swecoord.json and creates a list of station IDs that will be used to retrieve data from the SNOTEL api.
    :param json_file: a file that contains SNOTEL station IDs and their coordinates, string
    :return: list of SNOTEL station IDs
    """

    df = pd.read_json(json_file).transpose().reset_index()
    df['index'] = df['index'].apply(str)
    df['name'] = df['index'] + ":MT:SNTL"

    names = df['name'].values.tolist()

    return names


def get_snotel(start_date, end_date, json_file="../data/swecoords.json"):
    """
    Retrieves data from the SNOTEL api and returns a pandas data frame of SWE values for all SNOTEL stations in Montana
    for a given date range
    :param start_date: start date of data retrieval, string
    :param end_date: end date of data retrieval, string
    :param json_file: a file that contains SNOTEL station IDs and their coordinates, string
    :return: pandas data frame of snotel values
    """

    stations = __read_snotel_stations(json_file)
    base_str = "https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultipleStationReport/daily/start_of_period/"

    swe_vals = pd.DataFrame()

    for station in stations:

        station_number = station.split(":")[0]

        new_str = base_str + station + "|name/" + start_date + "," + end_date + "/stationId,WTEQ::value"
        dat = pd.read_csv(new_str, header=53, names=['date', 'station_id', station_number],
                          usecols=['date', station_number],
                          date_parser=pd.to_datetime, index_col=0)

        swe_vals = pd.concat([swe_vals, dat], axis=1)

        print station

    swe_vals = swe_vals * 25.4
    swe_vals.index = pd.to_datetime(swe_vals.index, format='%Y-%m-%d')

    return swe_vals


def update_snotel(snotel_file, swe_json):
    """
    Checks if user has a snotel data frame. If they do, update it with most recent daily data. If they don't, create
    a new data frame.
    :param snotel_file: the name and output directory of the snotel csv that will be created (e.g.
     '../data/snotel_swe.csv').
    :param swe_json: a json file with the station name and numbers
    :return: Saves out a pandas csv
    """

    try:

        dat = pd.read_csv(snotel_file, index_col='date', date_parser=pd.to_datetime)

    except IOError:

        print('snotel_swe.csv does not exist in this folder. Generating snotel_swe.csv')
        dat = get_snotel("1900-01-01", str(datetime.date.today()), swe_json)
        dat.to_csv(snotel_file)

    if dat.index[-1].strftime('%Y-%m-%d') != str(datetime.date.today()):

        date_use = (dat.index[-1] + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        updated_dat = get_snotel(date_use, str(datetime.date.today()),
                                 "../data/swecoords.json")

        dat = dat.append(updated_dat)
        dat.to_csv(snotel_file)


update_snotel('../data/swe/snotel_swe.csv', '../data/swecoords.json')