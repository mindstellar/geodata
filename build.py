import glob
import json
import os

import pandas as pd


def convertCsvToJson(csvFilePath):

    df = pd.read_csv(csvFilePath, dtype={
        "s_country_code_iso2": str,
        "s_country_name": str,
        "s_country_slug": str,
        "s_region_name": str,
        "s_region_slug": str,
        "s_city_name": str,
        "s_city_slug": str
    },keep_default_na=False)

    countryDict = {}
    countryDict['s_country_code'] = df.iloc[1]['s_country_code_iso2']
    countryDict['s_country_name'] = df.iloc[1]['s_country_name']
    countryDict['s_country_slug'] = df.iloc[1]['s_country_slug']

    groupedData = df.groupby(['s_country_code_iso2', 's_country_name',
                             's_country_slug', 's_region_name', 's_region_slug'])
    regionsList = []
    for key, value in groupedData:

        regionDict = {}
        j = groupedData.get_group(key).reset_index(drop=True)
        regionDict['s_country_code'] = j.at[0, 's_country_code_iso2'].lower()
        regionDict['s_region_name'] = j.at[0, 's_region_name']
        regionDict['s_region_slug'] = j.at[0, 's_region_slug']

        citiesList = []
        for i in j.index:
            cityDict = {}
            cityDict['s_country_code'] = j.at[i, 's_country_code_iso2'].lower()
            cityDict['s_region_slug'] = j.at[i, 's_region_slug']
            cityDict['s_city_name'] = j.at[i, 's_city_name']
            cityDict['s_city_slug'] = j.at[i, 's_city_slug']

            citiesList.append(cityDict.copy())

        regionDict['cities'] = sorted(citiesList, key = lambda i: i['s_city_name'])
        regionsList.append(regionDict)
    countryDict['regions'] = sorted(regionsList, key = lambda i: i['s_region_name'])
    return countryDict


for jsonFile in glob.glob('./src/json/*.json'):
    os.remove(jsonFile)

for csvFile in glob.glob('./src/csv/*.csv'):
    csvFileBasename = os.path.basename(csvFile)
    countryJson = convertCsvToJson(csvFile)
    print('Converting CSV File ' + csvFileBasename)
    jsonFile = open(
        './src/json/' + os.path.splitext(csvFileBasename)[0]+'.json', 'w')
    jsonFile.write(json.dumps(countryJson, indent=4, sort_keys=True))
    jsonFile.close()


locationsList = []
for jsonFiles in glob.glob('./src/json/*.json'):
    jsonFile = open(jsonFiles)
    jsonData = json.load(jsonFile)
    fileBasename = os.path.basename(jsonFiles)
    locationsDict = {}
    locationsDict['s_country_code'] = jsonData['s_country_code']
    locationsDict['s_country_name'] = jsonData['s_country_name']
    locationsDict['s_country_slug'] = jsonData['s_country_slug']
    locationsDict['s_file_name']  = os.path.basename(jsonFiles)
    locationsList.append(locationsDict.copy())

locations = {}
locations['locations'] = sorted(locationsList, key = lambda i: i['s_country_name'])

print('Creating JSON list of all locations')
jsonFile = open('./src/json-list.json', 'w')
jsonFile.write(json.dumps(locations, indent=4))
jsonFile.close()
print('Done')
