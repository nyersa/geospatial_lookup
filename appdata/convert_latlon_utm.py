import utm
from tkinter import messagebox

def convert_latlon_utm(lat, lon, utm_zone, utm_easting, utm_northing):
    if lat and lon:
        try:
            lat = round(float(lat), 4)
            lon = round(float(lon), 4)
            utm_coords = utm.from_latlon(lat, lon)
            return lat, lon, utm_coords[2], round(utm_coords[0]), round(utm_coords[1])
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid latitude and longitude.")
            return None, None, None, None, None
    elif utm_zone and utm_easting and utm_northing:
        try:
            utm_zone = int(utm_zone)
            utm_easting = round(float(utm_easting))
            utm_northing = round(float(utm_northing))
            latlon_coords = utm.to_latlon(utm_easting, utm_northing, utm_zone, 'N')
            return round(latlon_coords[0], 4), round(latlon_coords[1], 4), utm_zone, utm_easting, utm_northing
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid UTM coordinates.")
            return None, None, None, None, None
    else:
        messagebox.showerror("Input Error", "Please enter either latitude/longitude or UTM coordinates.")
        return None, None, None, None, None
