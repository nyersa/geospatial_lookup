import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, IntVar, ttk, font
import threading
import webbrowser
import utm
import geopandas as gpd
import os
import logging

# Custom module imports
from get_plss_data import get_plss_data
from get_elevation import get_elevation
from get_state_county import get_state_county
from clear_results import clear_results
from get_watershed_info import get_watershed_info
from generate_google_maps_link import generate_google_maps_link
from get_data_and_display import get_data_and_display
from export_to_csv import export_to_csv
from import_from_csv import import_from_csv
from update_status import update_status
from display_results import display_results
from convert_latlon_utm import convert_latlon_utm

class StatusWindowHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_entry = self.format(record)
        # Remove the log level prefix (e.g., "DEBUG - ")
        log_entry = log_entry.split(" - ", 1)[-1]
        self.text_widget.config(state='normal')
        self.text_widget.insert(tk.END, log_entry + '\n')
        self.text_widget.config(state='disabled')
        self.text_widget.yview(tk.END)

# Global variables
cumulative_results = []
headings_printed = False
auto_increment_label = 1
gdf_cache = {}
query_cache = {}

def close_application():
    root.quit()
    root.destroy()

def clear_history(tree, label_counter, processed_counter, total_records, progress_var):
    """Clears the Treeview and resets counters."""
    for row in tree.get_children():
        tree.delete(row)
    label_counter.set(1)
    processed_counter.set(0)
    total_records.set(0)
    progress_var.set("")

def show_loading_popup():
    loading_popup = Toplevel()
    loading_popup.title("Loading databases, please wait...")
    loading_popup.geometry("400x100")
    loading_popup.attributes('-topmost', True)
    tk.Label(loading_popup, text="Loading databases, please wait...").pack(pady=20)
    loading_popup.update_idletasks()
    return loading_popup

def close_loading_popup(popup):
    popup.destroy()

def on_submit(
    entry_lat, entry_lon, entry_utm_zone, entry_utm_easting, entry_utm_northing,
    entry_label, root, update_status, get_data_and_display, status_var, label_var,
    lat_var, lon_var, utm_zone_var, utm_easting_var, utm_northing_var,
    state_var, county_var, elevation_var, region_var, subregion_var, subbasin_var,
    watershed_var, subwatershed_var, catchment_var, huc12_var, principle_meridian_var,
    township_var, range_var, qqsec_var, google_maps_var,
    gdf_cache, tree, query_cache, huc12_enabled,
    status_display_var,
    section_var, qsec_var,           # NEW fields
    label_counter, processed_counter, total_records, progress_var
):
    global auto_increment_label, cumulative_results

    lat = entry_lat.get().strip()
    lon = entry_lon.get().strip()
    utm_zone = entry_utm_zone.get().strip()
    utm_easting = entry_utm_easting.get().strip()
    utm_northing = entry_utm_northing.get().strip()
    label = entry_label.get().strip()

    logging.debug(f"on_submit called with lat={lat}, lon={lon}, utm_zone={utm_zone}, label={label}")

    # Validate input
    if (lat and lon) and (utm_zone and utm_easting and utm_northing):
        messagebox.showerror("Input Error", "Please provide either lat/lon or UTM coords, not both.")
        return
    elif not ((lat and lon) or (utm_zone and utm_easting and utm_northing)):
        messagebox.showerror("Input Error", "Please provide either lat/lon or UTM coords.")
        return

    # Convert UTM -> lat/lon if needed
    if utm_zone and utm_easting and utm_northing:
        try:
            utm_zone = int(utm_zone)
            utm_easting = float(utm_easting)
            utm_northing = float(utm_northing)
            lat, lon = utm.to_latlon(utm_easting, utm_northing, utm_zone, northern=True)
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid UTM coordinates: {e}")
            return

    lat_var.set(str(lat))
    lon_var.set(str(lon))
    utm_zone_var.set(str(utm_zone))
    utm_easting_var.set(str(utm_easting))
    utm_northing_var.set(str(utm_northing))

    # Auto-increment label if none given
    if not label:
        label = str(auto_increment_label)
        auto_increment_label += 1

    get_data_and_display(
        lat, lon, label,
        label_counter, update_status, display_results,
        root, cumulative_results, status_var, label_var, lat_var, lon_var,
        utm_zone_var, utm_easting_var, utm_northing_var,
        state_var, county_var, elevation_var,
        region_var, subregion_var, subbasin_var, watershed_var, subwatershed_var, catchment_var,
        huc12_var, principle_meridian_var, township_var, range_var, qqsec_var, google_maps_var,
        gdf_cache, tree, query_cache, huc12_enabled,
        status_display_var,
        section_var, qsec_var,             # pass new vars
        progress_var, processed_counter, total_records
    )

# -----------------------
# Initialize the main GUI
# -----------------------
root = tk.Tk()
root.withdraw()
root.geometry("1625x400")

loading_popup = show_loading_popup()
close_loading_popup(loading_popup)
root.deiconify()
root.title("Geospatial Lookup")

# Use IntVar so we can do processed_counter.get()/set()
label_counter = IntVar(value=1)
huc12_enabled = IntVar(value=1)
processed_counter = IntVar(value=0)
total_records = IntVar(value=0)

bold_font = font.Font(root, weight='bold', size=8)

top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X)
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

spacer_frame = tk.Frame(bottom_frame, height=20)
spacer_frame.pack(side=tk.TOP, fill=tk.X)

# Define all StringVars in the same style
label_var = tk.StringVar()
lat_var = tk.StringVar()
lon_var = tk.StringVar()
utm_zone_var = tk.StringVar()
utm_easting_var = tk.StringVar()
utm_northing_var = tk.StringVar()
state_var = tk.StringVar()
county_var = tk.StringVar()
elevation_var = tk.StringVar()
region_var = tk.StringVar()
subregion_var = tk.StringVar()
subbasin_var = tk.StringVar()
watershed_var = tk.StringVar()
subwatershed_var = tk.StringVar()
catchment_var = tk.StringVar()
huc12_var = tk.StringVar()
principle_meridian_var = tk.StringVar()
township_var = tk.StringVar()
range_var = tk.StringVar()
qqsec_var = tk.StringVar()
google_maps_var = tk.StringVar()
status_var = tk.StringVar()          # define status_var
status_display_var = tk.StringVar()
progress_var = tk.StringVar()

# NEW: Section & Quarter Section
section_var = tk.StringVar()
qsec_var = tk.StringVar()

# Treeview columns (add "section" & "qsec" before "qqs")
columns = [
    "label", "latitude", "longitude", "utm_zone", "utm_easting", "utm_northing",
    "state", "county", "elevation", "region", "subregion", "subbasin",
    "watershed", "sub-watershed", "catchment", "huc12_code", "principle_meridian",
    "township", "range", "section", "qsec", "qqs", "google_maps"
]
tree = ttk.Treeview(bottom_frame, columns=columns, show='headings')

vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=tree.yview)
vsb.pack(side='right', fill='y')
tree.configure(yscrollcommand=vsb.set)

hsb = ttk.Scrollbar(bottom_frame, orient="horizontal", command=tree.xview)
hsb.pack(side='bottom', fill='x')
tree.configure(xscrollcommand=hsb.set)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

headers = [
    "Label", "Latitude", "Longitude", "UTM Zone", "UTM Easting", "UTM Northing",
    "State", "County", "Elevation", "Region", "Subregion", "Sub-Basin",
    "Watershed", "Sub-Watershed", "Catchment", "HUC12 Code", "Principle Meridian",
    "Township", "Range", "Section", "1/4 Sec", "1/4 1/4 Sec", "Google Maps"
]

width_factors = {
    "latitude": 0.6, "longitude": 0.6, "utm_zone": 0.6,
    "utm_easting": 0.6, "utm_northing": 0.6,
    "state": 0.6, "elevation": 0.6, "township": 0.6,
    "range": 0.6, "section": 0.6, "qsec": 0.6,
    "qqs": 0.6, "google_maps": 1.5
}

for col, header in zip(columns, headers):
    if col in width_factors:
        width = int(font.Font().measure(header) + 100)
        adjusted_width = int(width * width_factors[col])
        tree.column(col, width=adjusted_width, anchor=tk.CENTER)
    else:
        tree.column(col, width=font.Font().measure(header) + 100, anchor=tk.CENTER)
    tree.heading(col, text=header, anchor=tk.CENTER)

style = ttk.Style()
style.configure("Treeview.Heading", font=bold_font)

# Input fields
tk.Label(top_frame, text="Label:").grid(row=0, column=0, padx=10, pady=2, sticky="nw")
entry_label = tk.Entry(top_frame, width=20)
entry_label.grid(row=0, column=1, padx=10, pady=2, sticky="n")

tk.Label(top_frame, text="Latitude:").grid(row=1, column=0, padx=10, pady=2, sticky="nw")
entry_lat = tk.Entry(top_frame, width=20)
entry_lat.grid(row=1, column=1, padx=10, pady=2, sticky="n")

tk.Label(top_frame, text="Longitude:").grid(row=2, column=0, padx=10, pady=2, sticky="nw")
entry_lon = tk.Entry(top_frame, width=20)
entry_lon.grid(row=2, column=1, padx=10, pady=2, sticky="n")

tk.Label(top_frame, text="UTM Zone:").grid(row=3, column=0, padx=10, pady=2, sticky="nw")
entry_utm_zone = tk.Entry(top_frame, width=20)
entry_utm_zone.grid(row=3, column=1, padx=10, pady=2, sticky="n")

tk.Label(top_frame, text="UTM Easting:").grid(row=4, column=0, padx=10, pady=2, sticky="nw")
entry_utm_easting = tk.Entry(top_frame, width=20)
entry_utm_easting.grid(row=4, column=1, padx=10, pady=2, sticky="n")

tk.Label(top_frame, text="UTM Northing:").grid(row=5, column=0, padx=10, pady=2, sticky="nw")
entry_utm_northing = tk.Entry(top_frame, width=20)
entry_utm_northing.grid(row=5, column=1, padx=10, pady=2, sticky="n")

submit_button = tk.Button(
    top_frame, text="Submit",
    command=lambda: on_submit(
        entry_lat, entry_lon, entry_utm_zone, entry_utm_easting, entry_utm_northing,
        entry_label, root, update_status, get_data_and_display, status_var, label_var,
        lat_var, lon_var, utm_zone_var, utm_easting_var, utm_northing_var,
        state_var, county_var, elevation_var, region_var, subregion_var, subbasin_var,
        watershed_var, subwatershed_var, catchment_var, huc12_var, principle_meridian_var,
        township_var, range_var, qqsec_var, google_maps_var,
        gdf_cache, tree, query_cache, huc12_enabled,
        status_display_var,
        section_var, qsec_var,               # NEW
        label_counter, processed_counter, total_records, progress_var
    )
)
submit_button.grid(row=6, column=0, columnspan=2, padx=10, pady=1, sticky="nw")

# Output fields (second column)
tk.Label(top_frame, text="Label:").grid(row=0, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=label_var, state='readonly', width=40).grid(row=0, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Latitude:").grid(row=1, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=lat_var, state='readonly', width=40).grid(row=1, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Longitude:").grid(row=2, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=lon_var, state='readonly', width=40).grid(row=2, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="UTM Zone:").grid(row=3, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=utm_zone_var, state='readonly', width=40).grid(row=3, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="UTM Easting:").grid(row=4, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=utm_easting_var, state='readonly', width=40).grid(row=4, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="UTM Northing:").grid(row=5, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=utm_northing_var, state='readonly', width=40).grid(row=5, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="State:").grid(row=6, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=state_var, state='readonly', width=40).grid(row=6, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="County:").grid(row=7, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=county_var, state='readonly', width=40).grid(row=7, column=3, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Elevation:").grid(row=8, column=2, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=elevation_var, state='readonly', width=40).grid(row=8, column=3, padx=10, pady=2, sticky="w")

# Third column (watershed, etc.) ...
tk.Label(top_frame, text="Region:").grid(row=0, column=4, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=region_var, state='readonly', width=40).grid(row=0, column=5, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Subregion:").grid(row=1, column=4, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=subregion_var, state='readonly', width=40).grid(row=1, column=5, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Sub-Basin:").grid(row=2, column=4, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=subbasin_var, state='readonly', width=40).grid(row=2, column=5, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Watershed:").grid(row=3, column=4, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=watershed_var, state='readonly', width=40).grid(row=3, column=5, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Sub-Watershed:").grid(row=4, column=4, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=subwatershed_var, state='readonly', width=40).grid(row=4, column=5, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Catchment:").grid(row=5, column=4, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=catchment_var, state='readonly', width=40).grid(row=5, column=5, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="HUC12 Code:").grid(row=6, column=4, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=huc12_var, state='readonly', width=40).grid(row=6, column=5, padx=10, pady=2, sticky="w")

# Fourth column (PLSS, Google Maps, etc.)
tk.Label(top_frame, text="Principle Meridian:").grid(row=0, column=6, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=principle_meridian_var, state='readonly', width=40).grid(row=0, column=7, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Township:").grid(row=1, column=6, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=township_var, state='readonly', width=40).grid(row=1, column=7, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Range:").grid(row=2, column=6, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=range_var, state='readonly', width=40).grid(row=2, column=7, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Quarter Quarter Section:").grid(row=3, column=6, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=qqsec_var, state='readonly', width=40).grid(row=3, column=7, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Section:").grid(row=4, column=6, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=section_var, state='readonly', width=40).grid(row=4, column=7, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Quarter Section:").grid(row=5, column=6, padx=10, pady=2, sticky="w")
tk.Entry(top_frame, textvariable=qsec_var, state='readonly', width=40).grid(row=5, column=7, padx=10, pady=2, sticky="w")

tk.Label(top_frame, text="Google Maps:").grid(row=6, column=6, padx=10, pady=2, sticky="w")
google_maps_label = tk.Label(top_frame, textvariable=google_maps_var, fg="blue", cursor="hand2")
google_maps_label.grid(row=6, column=7, padx=10, pady=2, sticky="w")
google_maps_label.bind("<Button-1>", lambda event: webbrowser.open_new(google_maps_var.get()))

status_text = tk.Text(top_frame, height=4, width=83, state='disabled', wrap='word')
status_text.grid(row=7, column=5, columnspan=3, rowspan=2, padx=10, pady=2, sticky="w")
status_handler = StatusWindowHandler(status_text)
formatter = logging.Formatter('%(levelname)s - %(message)s')
status_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(status_handler)
logger.setLevel(logging.DEBUG)

export_button = tk.Button(top_frame, text="Export to CSV", command=lambda: export_to_csv(cumulative_results))
export_button.grid(row=7, column=0, padx=10, pady=1, sticky="w")

import_button = tk.Button(
    top_frame,
    text="Import coordinates from CSV (expects label,lat,long)",
    command=lambda: import_from_csv(
        lambda lat, lon, label, progress_var, processed_counter, total_records, update_status, status_var, root: get_data_and_display(
            lat, lon, label, 
            label_counter, update_status, display_results, root, cumulative_results,
            status_var, label_var, lat_var, lon_var, utm_zone_var, utm_easting_var, utm_northing_var,
            state_var, county_var, elevation_var, region_var, subregion_var, subbasin_var, watershed_var,
            subwatershed_var, catchment_var, huc12_var, principle_meridian_var, township_var, range_var,
            qqsec_var, google_maps_var,
            gdf_cache, tree, query_cache, huc12_enabled,
            status_display_var,
            section_var, qsec_var,  # NEW
            progress_var, processed_counter, total_records
        ),
        update_status,
        status_var,
        root,
        progress_var,
        processed_counter  # <-- ADDED here
    )
)

import_button.grid(row=7, column=1, padx=10, pady=1, sticky="w")

clear_button = tk.Button(
    top_frame, text="Clear Results",
    command=lambda: clear_results(
        entry_label, entry_lon, entry_lat, entry_utm_zone, entry_utm_easting, entry_utm_northing,
        label_var, lat_var, lon_var, utm_zone_var, utm_easting_var, utm_northing_var,
        state_var, county_var, elevation_var, region_var, subregion_var, subbasin_var,
        watershed_var, subwatershed_var, catchment_var, huc12_var, principle_meridian_var,
        township_var, range_var, qqsec_var, google_maps_var,
        section_var, qsec_var
    )
)
clear_button.grid(row=8, column=0, padx=10, pady=1, sticky="w")

clear_history_button = tk.Button(
    top_frame,
    text="Clear History",
    command=lambda: clear_history(tree, label_counter, processed_counter, total_records, progress_var)
)
clear_history_button.grid(row=8, column=1, padx=10, pady=1, sticky="w")

status_bar = tk.Label(root, bd=1, relief=tk.SUNKEN, anchor=tk.W, textvariable=status_var)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.protocol("WM_DELETE_WINDOW", close_application)
root.mainloop()
