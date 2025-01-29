import requests
import time
import logging

def get_watershed_info(lat, lon, update_status, status_var, root):
    logging.debug(f"get_watershed_info called with lat: {lat}, lon: {lon}")
    try:
        base_url = "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer"

        def fetch_data(layer, lat, lon):
            logging.debug(f"Fetching data for layer {layer}...")
            url = f"{base_url}/{layer}/query"
            params = {
                'f': 'json',
                'geometry': f'{lon},{lat}',
                'geometryType': 'esriGeometryPoint',
                'inSR': '4326',
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': '*',
                'returnGeometry': 'false'
            }
            response = requests.get(url, params=params)
            logging.debug(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'features' in data and len(data['features']) > 0:
                    logging.debug(f"Data fetched for layer {layer}: {data['features'][0]['attributes']}")
                    return data['features'][0]['attributes']
            return None

        layers = [(1, "HUC2"), (2, "HUC4"), (3, "HUC6"), (4, "HUC8"), (5, "HUC10"), (6, "HUC12")]
        results = {}
        
        for layer, name in layers:
            update_status(f"Fetching {name} watershed data...", status_var, root)
            data = fetch_data(layer, lat, lon)
            logging.debug(f"Pausing for .1 seconds after {name}...")
            time.sleep(.1)
            if name == "HUC2":
                results["Region"] = data.get('name', 'Unknown') if data else 'Unknown'
            elif name == "HUC4":
                results["Subregion"] = data.get('name', 'Unknown') if data else 'Unknown'
            elif name == "HUC6":
                results["Sub-Basin"] = data.get('name', 'Unknown') if data else 'Unknown'
            elif name == "HUC8":
                results["Watershed"] = data.get('name', 'Unknown') if data else 'Unknown'
            elif name == "HUC10":
                results["Sub-Watershed"] = data.get('name', 'Unknown') if data else 'Unknown'
            elif name == "HUC12":
                results["Catchment"] = data.get('name', 'Unknown') if data else 'Unknown'
                results["HUC12 Code"] = data.get('huc12', 'Unknown') if data else 'Unknown'

        logging.debug(f"Watershed info result: {results}")
        return results

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None
    except Exception as e:
        logging.error(f"Error fetching watershed data: {e}")
        return None
