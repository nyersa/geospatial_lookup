import time
import requests
import logging

def get_elevation(lat, lon, update_status, status_var, root):
    logging.debug(f"get_elevation called with lat: {lat}, lon: {lon}")
    try:
        query_elevation = f"https://api.opentopodata.org/v1/ned10m?locations={lat},{lon}"
        update_status("Fetching elevation data...", status_var, root)

        while True:
            logging.debug(f"Requesting elevation data for lat: {lat}, lon: {lon}")
            response_elevation = requests.get(query_elevation)
            logging.debug(f"Response status code: {response_elevation.status_code}")
            if response_elevation.status_code == 200:
                break
            elif response_elevation.status_code == 429:
                retry_after = int(response_elevation.headers.get('Retry-After', 1.5))  # Default to retry after 1.5 second
                update_status(f"Elevation data timeout, retrying in {retry_after} second(s)...", status_var, root)
                time.sleep(retry_after)
            else:
                response_elevation.raise_for_status()  # Raise for other errors

        elevation_data = response_elevation.json()
        if elevation_data['results'][0]['elevation'] is not None:
            elevation = round(elevation_data['results'][0]['elevation'], 1)
            logging.debug(f"Elevation data fetched: {elevation}")
        else:
            elevation = 'N/A'
        
        # Update GUI in the main thread
        root.after(0, lambda: update_status("Elevation Data Gathered, press a key to continue...", status_var, root))

        # Adding a 5-second delay after fetching the elevation data
        logging.debug("Elevation request successful")
        return elevation

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return 'N/A'
    except Exception as e:
        logging.error(f"Error fetching elevation data: {e}")
        return 'N/A'
