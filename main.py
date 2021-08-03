import requests
import json
from auth import url, creds
import pandas as pd
from time import sleep


def read_csv(filename='address.csv'):
    """Чтение списка адресов из CSV файла"""
    address_df = pd.read_csv(filename, encoding='utf-8').fillna(False)
    address_list = address_df.to_dict(orient='records')
    return address_list


def write_to_csv(filename, list_latitude, list_longitude):
    """Запись в CSV (Долготы и широты)"""
    dfs = pd.read_csv(filename)
    dfs['Latitude'] = list_latitude
    dfs['Longitude'] = list_longitude
    dfs.to_csv(filename, index=False)


def create_session_id_geocode(address):
    """Метод создания сессии, для get запроса координат."""
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        "GeocodingTasks": [
            {
                "Address": address
            }
        ],
        "ProviderName": "google",
        "ProviderKey": "AIzaSyAafQ6lLUiHuQKkse5u7yfxzSldGgvENuc",
        "WorkerCount": 1,
        "Language": "ru",
        "DefaultCountry": "Russian"
    }

    response = requests.post(f'{url}/geocoder/api/v1', headers=headers, data=json.dumps(data))
    geocode_id = response.json()['Id']

    result = response_retry(address, geocode_id)
    return result


def response_retry(address, geocode_id):
    """Метод получения координат (Долгота, Широта)"""
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    sleep(0.5)  # Засыпаем, чтобы не пропала сессия.
    response_coordinate = requests.get(f'{url}/geocoder/api/v1?sessionId={geocode_id}', headers=headers)
    # Если не пришел словарь с координатами, повторно вызываем функцию.
    if 'Results' not in response_coordinate.json().keys():
        response_retry(address, geocode_id)
    elif response_coordinate.json().get('Results')[0]['GpsLat'] and response_coordinate.json().get('Results')[0][
        'GpsLng']:
        result = response_coordinate.json()['Results'][0]
        return [result['GpsLat'], result['GpsLng']]
    else:
        result = response_coordinate.json()['Results'][0]
        return [result['GpsLat'], result['GpsLng']]


def main():
    data = read_csv()
    list_latitude = []
    list_longitude = []

    for address in data:
        print(address)
        coords_list = create_session_id_geocode(address['Address'])
        if coords_list is None:
            coords_list = create_session_id_geocode(address['Address'])
        latitude = str(coords_list[0])
        longitude = str(coords_list[1])
        list_latitude.append(latitude)
        list_longitude.append(longitude)

    write_to_csv('address.csv', list_latitude, list_longitude)


if __name__ == '__main__':
    main()
