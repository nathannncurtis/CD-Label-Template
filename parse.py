import sys
import os
import re
import time
import fitz
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Supress all output
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Determine the directory where parse.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Determine the name of the executable or script to call
main_script = 'main.py' if not getattr(sys, 'frozen', False) else 'main.exe'

# Full path to the main script or executable, relative to parse.py's location
main_path = os.path.join(script_dir, main_script)

# Function to read configuration from a text file
def read_config(file_path=".config"):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
        # Extract specific folders from the config
        monitor_folder = config.get("monitor_folder")
        output_folder = config.get("output_folder")
        if not monitor_folder or not output_folder:
            raise ValueError("Both 'monitor_folder' and 'output_folder' must be specified in the config file.")
        return monitor_folder, output_folder
    except Exception as e:
        print(f"Failed to read configuration file: {e}")
        sys.exit(1)  # Exit if config is not properly set

# Call read_config() to get paths for the folders
monitor_folder, output_folder = read_config()

def defluff_re_field(re_field):
    """Removes any text after 'AKA' in the re_field, if 'AKA' is present."""
    # Use regex to find ' AKA ' and capture everything before it
    match = re.search(r"(.+?)\s+AKA", re_field, re.IGNORECASE)
    if match:
        return match.group(1).strip()  # Return text before ' AKA '
    return re_field.strip()  # If 'AKA' not found, return the original string

class PDFHandler(FileSystemEventHandler):
    def __init__(self, folder_to_monitor):
        self.folder_to_monitor = folder_to_monitor
        self.processed_files = set()

    def on_created(self, event):
        # Ignore directories and non-PDF files
        if event.is_directory or not event.src_path.endswith('.pdf'):
            return

        # Wait a moment to ensure the file is fully written
        time.sleep(1)

        # Process the PDF if it's not already processed
        if event.src_path not in self.processed_files:
            self.processed_files.add(event.src_path)
            self.process_pdf(event.src_path)

    def process_pdf(self, pdf_path):
        """Extract text from each page according to the layout and pass it to main.py"""
        try:
            with fitz.open(pdf_path) as doc:
                if doc.page_count < 6:
                    print(f"PDF {pdf_path} does not contain enough pages for parsing.")
                    return

                # Extract text for each field according to the page layout
                facility = doc[0].get_text().strip()  # Page 1
                case_lines = doc[1].get_text().splitlines()
                case = " ".join([line.strip() for line in case_lines if line.strip()])  # Page 2
                wo_number = doc[2].get_text().strip()  # Page 3
                file_number = doc[3].get_text().strip()  # Page 4
                claim = doc[4].get_text().strip()  # Page 5
                attn = doc[5].get_text().strip()  # Page 6
                re_field = defluff_re_field(doc[6].get_text().strip()) if doc.page_count > 6 else ""
                dob = doc[7].get_text().strip() if doc.page_count > 7 else ""

                # Call main with parsed data as command-line arguments
                subprocess.run([
                    sys.executable, main_path,
                    '--facility', facility,
                    '--case', case,
                    '--wo_number', wo_number,
                    '--file_number', file_number,
                    '--claim', claim,
                    '--attn', attn,
                    '--re_field', re_field,
                    '--dob', dob
                ])

        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")

        # Delete PDF after parsing and passing, regardless of success or failure
        try:
            os.remove(pdf_path)
            print(f"Deleted PDF: {pdf_path}")
        except Exception as e:
            print(f"Failed to delete {pdf_path}: {e}")

def start_monitoring(folder_to_monitor):
    """Set up folder monitoring for new PDF files."""
    event_handler = PDFHandler(folder_to_monitor)
    observer = Observer()
    observer.schedule(event_handler, path=folder_to_monitor, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Define the folder to monitor (update this path as needed)
    folder_to_monitor = monitor_folder
    start_monitoring(folder_to_monitor)
