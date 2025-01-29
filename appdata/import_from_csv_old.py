import csv
import time
import threading
from tkinter import filedialog, messagebox
from queue import Queue
from get_elevation import get_elevation  # Importing the get_elevation function
from get_state_county import get_state_county  # Importing the get_state_county function

# Worker function to process each record in the queue
def worker(queue, import_callback, update_status, status_var, root, progress_var, processed_counter, total_records):
    while True:
        item = queue.get()
        if item is None:
            break  # Exit the loop if a 'None' item is encountered
        label, lat, lon = item
        # Process the record using the provided callback function
        import_callback(lat, lon, label, progress_var, processed_counter, total_records, update_status, status_var, root)
        time.sleep(2)  # Delay to ensure each elevation request is spaced out
        root.update_idletasks()  # Update the GUI
        queue.task_done()  # Mark the task as done in the queue

# Callback function to process each record
def import_callback(lat, lon, label, progress_var, processed_counter, total_records, update_status, status_var, root):
    elevation = get_elevation(lat, lon, update_status, status_var, root)
    state, county = get_state_county(lat, lon)
    processed_counter[0] += 1
    progress_var.set(f"Processed {processed_counter[0]} of {total_records} records")
    root.update_idletasks()  # Update the GUI

    # Display results or handle them as needed
    print(f"Label: {label}, Latitude: {lat}, Longitude: {lon}, Elevation: {elevation}, State: {state}, County: {county}")
    # Add the results to a list or a data structure if needed

# Main function to handle CSV import
def import_from_csv(import_callback, update_status, status_var, root, progress_var):
    try:
        # Open a file dialog to select the CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')
                next(csv_reader)  # Skip the header row
                records = list(csv_reader)
                total_records = len(records)
                processed_counter = [0]  # Initialize a mutable counter

                # Update status to show the number of records being processed
                update_status(f"Processing {total_records} records...", status_var, root)
                progress_var.set(f"Processed 0 of {total_records} records")

                # Create a queue to hold the records
                queue = Queue()
                # Start a new thread to process the records in the queue
                threading.Thread(target=worker, args=(queue, import_callback, update_status, status_var, root, progress_var, processed_counter, total_records)).start()

                for row in records:
                    try:
                        # Extract label, latitude, and longitude from each row
                        label, lat, lon = row[0], float(row[1]), float(row[2])
                        queue.put((label, lat, lon))  # Add the record to the queue
                    except ValueError:
                        continue  # Skip rows that do not have the expected format

    except Exception as e:
        # Display an error message if an exception occurs
        messagebox.showerror("Import Error", f"An error occurred while importing data: {e}")
