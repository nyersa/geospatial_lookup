import csv
import time
import threading
from tkinter import filedialog, messagebox
from queue import Queue

from get_elevation import get_elevation
from get_state_county import get_state_county

# Worker function to process each record in the queue
def worker(
    queue,
    import_callback,
    update_status,
    status_var,
    root,
    progress_var,
    processed_counter,  # now an IntVar
    total_records
):
    while True:
        item = queue.get()
        if item is None:
            break  # Exit if a 'None' item is encountered
        label, lat, lon = item
        # Process the record using the provided callback function
        import_callback(lat, lon, label, progress_var, processed_counter, total_records, update_status, status_var, root)
        time.sleep(6)
        root.after(0, root.update_idletasks)
        queue.task_done()

# Callback function to process each record
def import_callback(
    lat, lon, label,
    progress_var,
    processed_counter,  # IntVar
    total_records,
    update_status,
    status_var,
    root
):
    # Example usage of some existing functions:
    elevation = get_elevation(lat, lon, update_status, status_var, root)
    state, county = get_state_county(lat, lon)

    # Increment the IntVar-based counter instead of processed_counter[0]
    current_value = processed_counter.get()
    processed_counter.set(current_value + 1)

    # Update the GUI with the progress
    root.after(
        0,
        lambda: progress_var.set(
            f"Processed {processed_counter.get()} of {total_records} records"
        )
    )
    root.after(0, root.update_idletasks)

    # Debug print or handle the fetched data
    print(
        f"Label: {label}, Latitude: {lat}, Longitude: {lon}, "
        f"Elevation: {elevation}, State: {state}, County: {county}"
    )

# Main function to handle CSV import
def import_from_csv(
    import_callback,
    update_status,
    status_var,
    root,
    progress_var,
    processed_counter  # Now we expect an IntVar from the caller
):
    try:
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')
                next(csv_reader)  # Skip header row

                # Convert all rows to a list for length
                records = list(csv_reader)
                total_records = len(records)

                # Reset or initialize processed_counter to 0
                processed_counter.set(0)

                update_status(f"Processing {total_records} records...", status_var, root)
                progress_var.set(f"Processed 0 of {total_records} records")

                # Create a queue for the records
                record_queue = Queue()
                # Start the worker thread
                threading.Thread(
                    target=worker,
                    args=(
                        record_queue,
                        import_callback,
                        update_status,
                        status_var,
                        root,
                        progress_var,
                        processed_counter,
                        total_records
                    ),
                    daemon=True
                ).start()

                # Enqueue each CSV row
                for row in records:
                    try:
                        label, lat, lon = row[0], float(row[1]), float(row[2])
                        record_queue.put((label, lat, lon))
                    except (ValueError, IndexError):
                        # Skip rows that do not have the correct format
                        continue

    except Exception as e:
        messagebox.showerror("Import Error", f"An error occurred while importing data: {e}")
