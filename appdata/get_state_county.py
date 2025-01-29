import requests
import logging

def get_state_county(lat, lon):
    logging.debug(f"get_state_county called with lat: {lat}, lon: {lon}")
    try:
        query = f"https://geo.fcc.gov/api/census/block/find?latitude={lat}&longitude={lon}&format=json"
        logging.debug("Fetching state and county data...")
        response = requests.get(query)
        response.raise_for_status()

        data = response.json()
        state = data['State']['name']
        county = data['County']['name']
        logging.debug(f"State: {state}, County: {county}")
        return state, county

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None, None
    except Exception as e:
        logging.error(f"Error fetching state and county data: {e}")
        return None, None
