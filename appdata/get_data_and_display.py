import threading
import time
import logging

from get_elevation import get_elevation
from get_state_county import get_state_county
from get_plss_data import get_plss_data
from get_watershed_info import get_watershed_info
from generate_google_maps_link import generate_google_maps_link
from convert_latlon_utm import convert_latlon_utm

# Lock to prevent concurrent execution of fetch_data_and_display
fetch_lock = threading.Lock()

def get_data_and_display(
    lat, lon, label, label_counter, update_status, display_results, root,
    cumulative_results, status_var, label_var, lat_var, lon_var, utm_zone_var,
    utm_easting_var, utm_northing_var, state_var, county_var, elevation_var,
    region_var, subregion_var, subbasin_var, watershed_var, subwatershed_var,
    catchment_var, huc12_var, principle_meridian_var, township_var, range_var,
    qqsec_var, google_maps_var, gdf_cache, tree, query_cache, huc12_enabled,
    status_display_var,
    section_var=None, qsec_var=None,  # StringVars for Section / Quarter Section
    progress_var=None, processed_counter=None, total_records=0
):
    def update_gui(result):
        logging.debug("Updating GUI with fetched data...")

        # Append to cumulative_results
        cumulative_results.append(result)

        # Display results in GUI text fields
        root.after(0, lambda: display_results(
            result, 
            label_var, lat_var, lon_var, utm_zone_var, utm_easting_var, 
            utm_northing_var, state_var, county_var, elevation_var, region_var, 
            subregion_var, subbasin_var, watershed_var, subwatershed_var, 
            catchment_var, huc12_var, principle_meridian_var, township_var, range_var, 
            qqsec_var, google_maps_var
        ))

        # Update the Section and Quarter Section StringVars if they exist
        if section_var is not None:
            root.after(0, lambda: section_var.set(result.get("section", "N/A")))
        if qsec_var is not None:
            root.after(0, lambda: qsec_var.set(result.get("qsec", "N/A")))

        root.after(0, lambda: update_status("Data retrieved successfully.", status_var, root))

        # Insert row into the Treeview (make sure the column order matches your main script)
        lat_val = result.get("latitude", "N/A")
        lon_val = result.get("longitude", "N/A")
        rounded_lat = round(float(lat_val), 4) if lat_val not in (None, "N/A", "") else "N/A"
        rounded_lon = round(float(lon_val), 4) if lon_val not in (None, "N/A", "") else "N/A"

        root.after(0, lambda: tree.insert("", "end", values=(
            result["label"],
            rounded_lat,
            rounded_lon,
            result["utm_zone"],
            result["utm_easting"],
            result["utm_northing"],
            result["state"],
            result["county"],
            result["elevation"],
            result["region"],
            result["subregion"],
            result["subbasin"],
            result["watershed"],
            result["subwatershed"],
            result["catchment"],
            result["huc12_code"],
            result["principle_meridian"],
            result["township"],
            result["range"],
            result["section"],    # Section
            result["qsec"],       # Quarter Section
            result["qqs"],        # Quarter Quarter Section
            result["google_maps"]
        )))

        # Increment processed_counter if provided
        if processed_counter is not None:
            current_count = processed_counter.get()
            processed_counter.set(current_count + 1)
            root.after(0, lambda: progress_var.set(
                f"Processed {processed_counter.get()} of {total_records} records"
            ))

        # Reset status_display_var
        root.after(0, lambda: status_display_var.set("Waiting for Input"))

    def fetch_data_and_display():
        with fetch_lock:
            try:
                root.after(0, lambda: status_display_var.set("Fetching elevation..."))
                time.sleep(1)
                elevation = get_elevation(lat, lon, update_status, status_var, root)

                root.after(0, lambda: status_display_var.set("Fetching state and county data..."))
                state, county = get_state_county(lat, lon)

                root.after(0, lambda: status_display_var.set("Fetching watershed data..."))
                watershed_info = get_watershed_info(lat, lon, update_status, status_var, root)

                root.after(0, lambda: status_display_var.set("Fetching PLSS data..."))
                plss_info = get_plss_data(lat, lon, None, update_status, status_var, root, query_cache)

                root.after(0, lambda: status_display_var.set("Converting lat/lon to UTM..."))
                _, _, utm_zone, utm_easting, utm_northing = convert_latlon_utm(lat, lon, None, None, None)

                root.after(0, lambda: status_display_var.set("Generating Google Maps link..."))
                google_maps_link = generate_google_maps_link(lat, lon)

                result = {
                    "label": label,
                    "latitude": lat,
                    "longitude": lon,
                    "utm_zone": utm_zone,
                    "utm_easting": utm_easting,
                    "utm_northing": utm_northing,
                    "state": state if state else 'N/A',
                    "county": county if county else 'N/A',
                    "elevation": elevation,
                    "region": watershed_info.get('Region', 'N/A'),
                    "subregion": watershed_info.get('Subregion', 'N/A'),
                    "subbasin": watershed_info.get('Sub-Basin', 'N/A'),
                    "watershed": watershed_info.get('Watershed', 'N/A'),
                    "subwatershed": watershed_info.get('Sub-Watershed', 'N/A'),
                    "catchment": watershed_info.get('Catchment', 'N/A'),
                    "huc12_code": watershed_info.get('HUC12 Code', 'N/A'),
                    "principle_meridian": plss_info.get('Principle Meridian', 'N/A') if plss_info else 'N/A',
                    "township": plss_info.get('Township', 'N/A') if plss_info else 'N/A',
                    "range": plss_info.get('Range', 'N/A') if plss_info else 'N/A',
                    "section": plss_info.get('Section', 'N/A') if plss_info else 'N/A',
                    "qsec": plss_info.get('Quarter Section', 'N/A') if plss_info else 'N/A',
                    "qqs": plss_info.get('Quarter Quarter Section', 'N/A') if plss_info else 'N/A',
                    "google_maps": google_maps_link
                }

                logging.debug("Updating GUI with the result...")
                root.after(0, lambda: update_gui(result))

            except Exception as e:
                logging.error(f"Error occurred while fetching data: {e}")
                root.after(0, lambda: update_status("Error occurred while fetching data.", status_var, root))

    if fetch_lock.locked():
        logging.debug("Data fetching is already in progress...")
    else:
        logging.debug("Starting a new thread to fetch and display data...")
        threading.Thread(target=fetch_data_and_display).start()
