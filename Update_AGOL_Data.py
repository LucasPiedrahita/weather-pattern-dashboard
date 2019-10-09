

# To run this script, enter the following command in the command line:
# C:\"Program Files"\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe L:\Projects\WeatherDashboard\Update_AGOL_Data.py
# This script updates the Wake_Monthly_Weather item in ArcGIS Online to
# include the most recent data available from ncdc.noaa.gov.


import datetime
import os
import sys
import pandas as pd
import requests
from arcgis.features import FeatureLayerCollection
from arcgis.gis import GIS

climate_variables = ['pcp', 'tmax', 'tmin', 'tavg']
column_names = ['Precip_Inches', 'TempMax_DegF', 'TempMin_DegF', 'TempAvg_DegF']
today = datetime.datetime.now()
url_start = 'https://www.ncdc.noaa.gov/cag/county/time-series/NC-183-'
url_end = '-all-{0}-{1}-{2}.csv'.format(str(today.month - 1), str(today.year - 50), str(today.year))
relative_path = sys.path[0]

try:
    # Loop through each variable and get the data from ncdc.noaa.gov
    for i in range(len(climate_variables)):
        print('Getting {0} data from ncdc.noaa.gov...'.format(climate_variables[i]))
        url = '{0}{1}{2}'.format(url_start, climate_variables[i], url_end)
        response = requests.get(url)
        text = response.text.splitlines()
        lst = []
        # For the first variable, create the df and the Date, Year, and Month columns
        if i == 0:
            for line in text[4:]:
                line_list = line.split(',')
                new_line_list = [line_list[0], int(line_list[0][:4]), int(line_list[0][4:]), float(line_list[1])]
                lst.append(new_line_list)
            df = pd.DataFrame(lst, columns=['Date', 'Year', 'Month', column_names[i]])
        # For the other climate_variables, just append them to the existing df
        else:
            for line in text[4:]:
                line_list = line.split(',')
                lst.append(float(line_list[1]))
            if len(df) == len(lst):
                df[column_names[i]] = lst
except Exception as e:
    print("\tAn Error Occurred while constructing DataFrame from ncdd.noaa.gov: {0}".format(e))

# If the df creation was successful, there will be at least 600 records
if len(df) > 600:
    csv_name = 'Wake_Monthly_Weather.csv'
    csv_path = os.path.join(relative_path, csv_name)
    print('csv_path: {0}'.format(csv_path))
    try:
        # Write the df to csv
        print('Exporting DataFrame to CSV, {0}.'.format(csv_name))
        df.to_csv(csv_name, index=False)
        print('\tCSV saved here, {0}.'.format(csv_path))
    except Exception as e:
        print("\tAn Error Occurred Writing the DataFrame to a CSV File: {0}".format(e))

    # Connect to the GIS
    try:
        print('Connecting to ArcGIS Online...')
        arcgis_online = GIS('https://www.arcgis.com', os.environ.get('AGOL_USER'), os.environ.get('AGOL_PASS'))
        print('\tConnected.')

        # Get the Wake_Monthly_Weather item in AGOL
        wake_monthly_weather = arcgis_online.content.get('c0d8a9375cfd47708b598c5441ab9e86')

        # Get the item's feature layer collection and overwrite it
        print('Overwriting Wake_Monthly_Weather FeatureLayerCollection...')
        wake_monthly_weather_FLC = FeatureLayerCollection.fromitem(wake_monthly_weather)
        wake_monthly_weather_FLC.manager.overwrite(csv_path)
        print('\tOverwritten.')

        # Update the item's snippet & descriptions
        print('Updating Wake_Monthly_Weather item snippet & description...')
        weather_item_snippet = 'Monthly precipitation, max temp, min temp, and average temp in Wake County from ' \
                  'January, 1969 to {0}.'.format(datetime.date(today.year, today.month - 1, 1).strftime('%B, %Y'))
        weather_item_description = '<div><font size="3">Last updated to include data up to <b>{0}</b>.<br /></font></div><div><' \
                      'font size="3"><br /></font></div><div><font size="3"><span style="font-family: &quot;Avenir ' \
                      'Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica ' \
                      'Neue&quot;, sans-serif;">Data from </span><a href="https://www.ncdc.noaa.gov/cag/county/time-' \
                      'series">https://www.ncdc.noaa.gov/cag/county/time-series</a>, which references the <a ' \
                      'href="https://www.ncdc.noaa.gov/monitoring-references/maps/us-climate-divisions.php" target="_' \
                      'blank">US Climate Divisional Dataset</a>. </font></div><div><font size="3"><br /></font></div>' \
                      '<font size="3"><span style="font-family: &quot;Avenir Next W01&quot;, &quot;Avenir Next ' \
                      'W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif;">' \
                      'Precipitation dataset downloaded from: </span><a href="https://www.ncdc.noaa.gov/cag/county/' \
                      'time-series/NC-183-pcp{1}" target="_blank">https://www.ncdc.noaa.gov/cag/county/time-series/' \
                      'NC-183-pcp{1}</a><font face="Avenir Next W01, Avenir Next W00, Avenir Next, Avenir, Helvetica ' \
                      'Neue, sans-serif">.</font></font><div><font face="Avenir Next W01, Avenir Next W00, Avenir ' \
                      'Next, Avenir, Helvetica Neue, sans-serif" size="3"><br /></font></div><div><font size="3">' \
                      '<font face="Avenir Next W01, Avenir Next W00, Avenir Next, Avenir, Helvetica Neue, ' \
                      'sans-serif">Average Temperature dataset downloaded from </font><a href="https://www.ncdc.' \
                      'noaa.gov/cag/county/time-series/NC-183-tavg{1}">https://www.ncdc.noaa.gov/cag/county/time-' \
                      'series/NC-183-tavg{1}</a>.</font></div><div><font size="3"><br /></font></div><div><font ' \
                      'size="3"><font face="Avenir Next W01, Avenir Next W00, Avenir Next, Avenir, Helvetica Neue, ' \
                      'sans-serif">Minimum Temperature dataset downloaded from </font><a href="https://www.ncdc.' \
                      'noaa.gov/cag/county/time-series/NC-183-tmin{1}">https://www.ncdc.noaa.gov/cag/county/time-' \
                      'series/NC-183-tmin{1}</a>.</font></div><div><font size="3"><br /></font></div><div>' \
                      '<font size="3"><font face="Avenir Next W01, Avenir Next W00, Avenir Next, Avenir, ' \
                      'Helvetica Neue, sans-serif">Maximum Temperature dataset downloaded from </font><a href=' \
                      '"https://www.ncdc.noaa.gov/cag/county/time-series/NC-183-tmax{1}">https://www.ncdc.noaa.' \
                      'gov/cag/county/time-series/NC-183-tmax{1}</a>.<br /></font><div style="font-family: &quot;' \
                      'Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, ' \
                      '&quot;Helvetica Neue&quot;, sans-serif;"><font size="3"><br /></font></div><div style=' \
                      '"font-family: &quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir ' \
                      'Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif;"><font size="3">Datasets ' \
                      'brought together into one table and date column split into year and month before uploading to ' \
                      'ArcGIS Online to make dashboarding easier.</font></div>' \
                      '</div>'.replace(u'\xa0', u' ').format(datetime.date(today.year, today.month - 1,
                                                                           1).strftime('%B, %Y'), url_end)
        wake_monthly_weather.update(item_properties={'snippet': weather_item_snippet, 'description': weather_item_description})
        print('\tUpdated.')

        # Update the dashboard's description to reflect data update
        print("Updating Weather Patters in Wake County Dashboard's item description...")
        dashboard = arcgis_online.content.get('319b3bd3007543f89aaddd5e38c0d658')
        dashboard_description = 'This interactive dashboard allows the user to explore monthly precipitation' \
                      ' and temperature data for the past five decades.<div><br /></div><div>The data ' \
                      'in this dashboard are part of the US Climate Divisional Dataset and were sourced ' \
                      'from <a href="https://www.ncdc.noaa.gov/cag/county/time-series" target="_blank"' \
                      '>https://www.ncdc.noaa.gov/cag/county/time-series</a>. </div><div><br /></div>' \
                      '<div>Includes data from January, 1999 to {0}. See the <a href="http://wake.maps.arcgis.' \
                      'com/home/item.html?id=c0d8a9375cfd47708b598c5441ab9e86" target="_' \
                      'blank">Wake_Monthly_Weather</a> data details for more information on source data.' \
                      '</div>'.replace(u'\xa0', u' ').format(datetime.date(today.year, today.month - 1,
                                                                           1).strftime('%B, %Y'))
        dashboard.update(item_properties={'description': dashboard_description})
        print('\tUpdated.')
    except Exception as e:
        print("\tAn Error Occurred Interacting with ArcGIS Online: {0}".format(e))
else:
    print('constructed df has less than 600 records. df:', df)
time_end = datetime.datetime.now()
print('Execution Time: {0}.'.format(str(time_end-today)))
