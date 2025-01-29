import csv
import time
import threading
from tkinter import filedialog, messagebox
from queue import Queue
import logging

# Setup basic logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Worker function to process each record in the queue
def worker(queue, import_callback, update_status, status_var, root, progress_var, processed_counter, total_records):
    while True:
        try:
            item = queue.get()
            if item is None:
                logging.debug("Worker received exit signal")
                queue.task_done()
                break  # Exit the loop if a 'None' item is encountered
            label, lat, lon = item
            logging.debug(f"Worker processing: {label}, {lat}, {lon}")
            import_callback(lat, lon, label, progress_var, processed_counter, total_records, update_status, status_var, root)
            root.after(0, root.update_idletasks)  # Update the GUI in the main thread
            queue.task_done()
            logging.debug("Task done")
        except Exception as e:
            logging.error(f"Error in worker thread: {e}", exc_info=True)
            queue.task_done()

# Mock callback function for testing
def import_callback(lat, lon, label, progress_var, processed_counter, total_records, update_status, status_var, root):
    try:
        logging.debug(f"Import callback processing record: Label={label}, Lat={lat}, Lon={lon}")

        # Mock processing logic: Increment the processed counter
        processed_counter[0] += 1
        # progress_var.set(f"Processed {processed_counter[0]} of {total_records} records")
        # Log completion
        logging.info(f"Completed processing: Label={label}, Latitude={lat}, Longitude={lon}")
        
        # Simulate processing delay
        time.sleep(1)

        # Ensure task completion is logged
        logging.debug("Task done inside import_callback")
    except Exception as e:
        logging.error(f"Error in import_callback: {e}", exc_info=True)



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

                # Start worker threads
                num_worker_threads = 5  # Adjust the number of threads as needed
                threads = []
                for _ in range(num_worker_threads):
                    t = threading.Thread(target=worker, args=(queue, import_callback, update_status, status_var, root, progress_var, processed_counter, total_records))
                    t.start()
                    threads.append(t)

                # Enqueue records
                for row in records:
                    try:
                        # Extract label, latitude, and longitude from each row
                        label, lat, lon = row[0], float(row[1]), float(row[2])
                        logging.debug(f"Enqueueing record: Label={label}, Lat={lat}, Lon={lon}")
                        queue.put((label, lat, lon))  # Add the record to the queue
                    except ValueError:
                        logging.warning(f"Skipping row due to invalid data: {row}")
                        continue  # Skip rows that do not have the expected format

                # Signal all threads to exit by placing None in the queue
                for _ in range(num_worker_threads):
                    queue.put(None)

                # Wait for all threads to finish
                for t in threads:
                    t.join()
                    logging.debug("Worker thread has exited")

    except Exception as e:
        logging.error(f"Exception in import_from_csv: {e}", exc_info=True)
        messagebox.showerror("Import Error", f"An error occurred while importing data: {e}")
