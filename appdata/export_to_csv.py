import csv
from tkinter import filedialog, messagebox

# Function to export cumulative results to a CSV file
def export_to_csv(cumulative_results):
    # Debug print to confirm function call
    print("Export function called with cumulative_results:", cumulative_results)
    
    # Check if there are any results to export
    if not cumulative_results:
        messagebox.showwarning("Export Warning", "No data to export.")
        return

    try:
        # Open a file dialog to select the save location for the CSV file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(
                    csvfile,
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )
                
                # Write the header row to the CSV file
                csv_writer.writerow([
                    "Label",
                    "Latitude",
                    "Longitude",
                    "UTM Zone",
                    "UTM Easting",
                    "UTM Northing",
                    "State",
                    "County",
                    "Elevation",
                    "Region",
                    "Subregion",
                    "Sub-Basin",
                    "Watershed",
                    "Sub-Watershed",
                    "Catchment",
                    "HUC12 Code",
                    "Principle Meridian",
                    "Township",
                    "Range",
                    "Section",            # <-- NEW
                    "Quarter Section",     # <-- NEW
                    "Quarter Quarter Section",
                    "Google Maps"
                ])
                
                # Write each result to the CSV file
                for result in cumulative_results:
                    # Debug print to confirm each result being exported
                    print("Exporting Result:", result)
                    
                    # Round latitude and longitude to 4 decimal places if they exist
                    latitude = (
                        round(float(result.get("latitude", 0)), 4)
                        if result.get("latitude") else ""
                    )
                    longitude = (
                        round(float(result.get("longitude", 0)), 4)
                        if result.get("longitude") else ""
                    )
                    
                    # Write the result row, including the new Section and Quarter Section fields
                    csv_writer.writerow([
                        result.get("label", ""),
                        latitude,
                        longitude,
                        result.get("utm_zone", ""),
                        result.get("utm_easting", ""),
                        result.get("utm_northing", ""),
                        result.get("state", ""),
                        result.get("county", ""),
                        result.get("elevation", ""),
                        result.get("region", ""),
                        result.get("subregion", ""),
                        result.get("subbasin", ""),
                        result.get("watershed", ""),
                        result.get("subwatershed", ""),
                        result.get("catchment", ""),
                        result.get("huc12_code", ""),
                        result.get("principle_meridian", ""),
                        result.get("township", ""),
                        result.get("range", ""),
                        result.get("section", ""),     # Matches "Section"
                        result.get("qsec", ""),        # Matches "Quarter Section"
                        result.get("qqs", ""),         # "Quarter Quarter Section"
                        result.get("google_maps", "")
                    ])
            
            # Debug print to confirm successful CSV export
            print(f"CSV successfully written to: {file_path}")
            # Show success message
            messagebox.showinfo("Export Successful", "Data has been successfully exported to CSV.")
    
    except Exception as e:
        # Debug print to confirm error during CSV export
        print(f"Error during CSV export: {e}")
        # Show error message
        messagebox.showerror("Export Error", f"An error occurred while exporting data: {e}")
