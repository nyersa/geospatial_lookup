import time
from shapely.geometry import Point
import requests
import logging

def get_plss_data(lat, lon, gdf, update_status, status_var, root, query_cache):
    logging.debug(f"get_plss_data called with lat: {lat}, lon: {lon}")
    try:
        update_status("Fetching PLSS data...", status_var, root)

        if (lat, lon) in query_cache:
            cached_data = query_cache[(lat, lon)]
            logging.debug(f"Using cached PLSS data: {cached_data}")
            return cached_data

        point = Point(lon, lat)

        def fetch_plss_online(lat, lon):
            try:
                logging.debug(f"Fetching PLSS data online for lat: {lat}, lon: {lon}")
                fields = ','.join(['PRINMER', 'TWNSHPLAB', 'FRSTDIVNO', 'QSEC', 'QQSEC'])
                query_url = (
                    "https://gis.blm.gov/arcgis/rest/services/Cadastral/"
                    "BLM_Natl_PLSS_CadNSDI/MapServer/3/query?"
                    "where=1%3D1"
                    f"&geometry={lon},{lat}"
                    "&geometryType=esriGeometryPoint"
                    "&inSR=4326"
                    "&spatialRel=esriSpatialRelIntersects"
                    f"&outFields={fields}"
                    "&f=json"
                )
                response = requests.get(query_url)
                response.raise_for_status()
                data = response.json()

                plss_info = {}
                if data.get('features'):
                    attributes = data['features'][0]['attributes']
                    plss_info['Principle Meridian'] = attributes.get('PRINMER', 'N/A').replace(' Meridian', '')
                    twshplab = attributes.get('TWNSHPLAB', 'N/A')
                    if ' ' in twshplab:
                        township, rng = twshplab.split(' ', 1)
                    else:
                        township, rng = twshplab, 'N/A'
                    township = township.replace('T', '')
                    rng = rng.replace('R', '')
                    plss_info['Township'] = township
                    plss_info['Range'] = rng
                    plss_info['Section'] = attributes.get('FRSTDIVNO', 'N/A') or 'N/A'
                    quarter = attributes.get('QSEC', 'N/A')
                    qqsec = attributes.get('QQSEC', 'N/A')
                    if qqsec not in [None, '', 'N/A']:
                        plss_info['Quarter Quarter Section'] = qqsec
                    else:
                        plss_info['Quarter Quarter Section'] = 'N/A'
                    plss_info['Quarter Section'] = quarter if quarter else 'N/A'
                else:
                    plss_info = {
                        'Principle Meridian': 'N/A',
                        'Township': 'N/A',
                        'Range': 'N/A',
                        'Section': 'N/A',
                        'Quarter Section': 'N/A',
                        'Quarter Quarter Section': 'N/A'
                    }
                time.sleep(0.25)
                logging.debug(f"PLSS data fetched: {plss_info}")
                return plss_info

            except requests.exceptions.HTTPError as http_err:
                logging.error(f"HTTP error occurred: {http_err}")
                return None
            except Exception as e:
                logging.error(f"Error fetching PLSS data: {e}")
                return None

        plss_info = fetch_plss_online(lat, lon)
        query_cache[(lat, lon)] = plss_info
        logging.debug(f"Returning PLSS data: {plss_info}")
        return plss_info

    except Exception as e:
        logging.error(f"Error fetching PLSS data: {e}")
        return None
