def display_results(result, label_var, lat_var, lon_var, utm_zone_var, utm_easting_var, utm_northing_var, state_var, county_var, elevation_var, region_var, subregion_var, subbasin_var, watershed_var, subwatershed_var, catchment_var, huc12_var, principle_meridian_var, township_var, range_var, qqsec_var, google_maps_var):
    latitude = round(float(result.get("latitude", "N/A")), 4) if result.get("latitude") != "N/A" else "N/A"
    longitude = round(float(result.get("longitude", "N/A")), 4) if result.get("longitude") != "N/A" else "N/A"
    utm_easting = round(float(result.get("utm_easting", "N/A"))) if result.get("utm_easting") != "N/A" else "N/A"
    utm_northing = round(float(result.get("utm_northing", "N/A"))) if result.get("utm_northing") != "N/A" else "N/A"
    label_var.set(result.get("label", "N/A"))
    lat_var.set(latitude)
    lon_var.set(longitude)
    utm_zone_var.set(result.get("utm_zone", "N/A"))
    utm_easting_var.set(utm_easting)
    utm_northing_var.set(utm_northing)
    state_var.set(result.get("state", "N/A"))
    county_var.set(result.get("county", "N/A"))
    elevation_var.set(result.get("elevation", "N/A"))
    region_var.set(result.get("region", "N/A"))
    subregion_var.set(result.get("subregion", "N/A"))
    subbasin_var.set(result.get("subbasin", "N/A"))
    watershed_var.set(result.get("watershed", "N/A"))
    subwatershed_var.set(result.get("subwatershed", "N/A"))
    catchment_var.set(result.get("catchment", "N/A"))
    huc12_var.set(result.get("huc12_code", "N/A"))
    principle_meridian_var.set(result.get("principle_meridian", "N/A"))
    township_var.set(result.get("township", "N/A"))
    range_var.set(result.get("range", "N/A"))
    qqsec_var.set(result.get("qqs", "N/A"))
    google_maps_var.set(result.get("google_maps", "N/A"))
