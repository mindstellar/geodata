import glob
import json
import os
import re
import unicodedata
import requests


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    txt_string = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return txt_string.encode('ascii', 'ignore').decode('ascii')


def slugify(inputStr):
    """ 
    Convert to ASCII. 
    Convert spaces to hyphens. Remove characters that aren't alphanumerics, underscores, or hyphens. 
    Convert to lowercase. 
    Also strip leading and trailing whitespace. 
    """
    inputStr = unicodedata.normalize('NFKD', inputStr).encode(
        'ascii', 'ignore').decode('ascii')
    inputStr = re.sub('[^\w\s-]', '', inputStr).strip().lower()
    return re.sub('[-\s]+', '-', inputStr)


# Remove old json files
for jsonFile in glob.glob('./src/json/*.json'):
    os.remove(jsonFile)

# Download raw geodata from github.com/dr5hn/countries-states-cities-database repository's master branch
url = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates%2Bcities.json'
region = requests.get(url, allow_redirects=True)
open('countries-states-cities.json', 'wb').write(region.content)
docs = json.load(open('countries-states-cities.json'))

for doc in docs:
    print('Check location data for '+doc['name'].strip())
    if not 'states' in doc or len(doc['states']) == 0:
        print('Excluding country ' +
              doc['name'].strip()+' because region list is empty')

    else:
        print('Creating JSON data for '+doc['name'].strip())
        country = {}
        countryName = str(doc['name'].strip())
        # Special rules for few countries, correct me if wrong
        if doc['iso2'] == "CD":
            countryName = "Congo Republic"
        if doc['iso2'] == "HR":
            countryName = "Croatia"
        if doc['iso2'] == "CI":
            countryName = "Ivory Coast"
        if doc['iso2'] == "HK":
            countryName = "Hong Kong"
        if doc['iso2'] == "BS":
            countryName = "Bahamas"
        if doc['iso2'] == "NL":
            countryName = "Netherlands"
        if doc['iso2'] == "GM":
            countryName = "Gambia"
        # End
        with open('src/json/'+doc['iso2'].strip()+'-'+countryName.strip()+'.json', 'w') as out:

            country['s_country_code'] = doc['iso2'].strip()
            country['s_country_name'] = countryName
            country['s_country_slug'] = slugify(countryName)

            regionsList = []
            for state in doc['states']:
                region = {}
                region['s_country_code'] = country['s_country_code'].lower()
                region['s_region_name'] = remove_accents(state['name'].strip())
                region['s_region_slug'] = slugify(region['s_region_name'])

                cityList = []
                # if region doesn't have any city than add region as city
                # Do share your suggestion.
                if not 'cities' in state or len(state['cities']) == 0:
                    city = {}
                    city['s_country_code'] = country['s_country_code'].lower()
                    city['s_region_slug'] = region['s_region_slug']
                    city['s_city_name'] = region['s_region_name']
                    city['s_city_slug'] = region['s_region_slug']
                    cityList.append(city.copy())
                else:
                    for city in state['cities']:
                        if not remove_accents(city['name'].strip()) == "":
                            cty = {}
                            cty['s_country_code'] = country['s_country_code'].lower()
                            cty['s_region_slug'] = region['s_region_slug']
                            cty['s_city_name'] = remove_accents(city['name'].strip())
                            cty['s_city_slug'] = slugify(cty['s_city_name'])
                            cityList.append(cty.copy())

                region['cities'] = sorted(cityList, key=lambda i: i['s_city_name'])
                regionsList.append(region)

            country['regions'] = sorted(
                regionsList, key=lambda i: i['s_region_name'])

            json.dump(country, out, indent=4, sort_keys=True)

locationsList = []
for jsonFiles in glob.glob('./src/json/*.json'):
    jsonFile = open(jsonFiles)
    jsonData = json.load(jsonFile)
    fileBasename = os.path.basename(jsonFiles)
    locationsDict = {}
    locationsDict['s_country_code'] = jsonData['s_country_code']
    locationsDict['s_country_name'] = jsonData['s_country_name']
    locationsDict['s_country_slug'] = jsonData['s_country_slug']
    locationsDict['s_file_name'] = os.path.basename(jsonFiles)
    locationsList.append(locationsDict.copy())

locations = {}
locations['locations'] = sorted(
    locationsList, key=lambda i: i['s_country_name'])

print('Creating JSON list of all locations')
jsonFile = open('./src/json-list.json', 'w')
jsonFile.write(json.dumps(locations, indent=4))
jsonFile.close()
print('Done')
