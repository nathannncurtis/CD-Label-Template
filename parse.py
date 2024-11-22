import sys
import os
import re
import time
import fitz
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Suppress all output
#sys.stdout = open(os.devnull, 'w')
#sys.stderr = open(os.devnull, 'w')

# Determine the directory where parse.py (or parse.exe) is located
if getattr(sys, 'frozen', False):  # Check if running in a frozen state
    script_dir = os.path.dirname(sys.executable)  # Use the directory of the frozen executable
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Determine the name of the executable or script to call
main_script = 'main.exe' if getattr(sys, 'frozen', False) else 'main.py'

# Full path to the main script or executable, ensuring it’s in the same directory as parse
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
        monitor_folder = config.get("monitor_folder")
        output_folder = config.get("output_folder")
        if not monitor_folder or not output_folder:
            raise ValueError("Both 'monitor_folder' and 'output_folder' must be specified in the config file.")
        return monitor_folder, output_folder
    except Exception as e:
        print(f"Failed to read configuration file: {e}")
        sys.exit(1)

# Call read_config() to get paths for the folders
monitor_folder, output_folder = read_config()

def wait_for_file(file_path, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(file_path):
            return True
        time.sleep(2)  # Wait briefly and re-check
    return False

def safe_delete(file_path, retries=10, delay=2):
    for attempt in range(retries):
        try:
            os.remove(file_path)
            print(f"Deleted PDF: {file_path}")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} to delete {file_path} failed: {e}")
            time.sleep(delay)
    print(f"Failed to delete {file_path} after {retries} attempts")

def defluff_re_field(re_field):
    """Removes any text after 'AKA' in the re_field, if 'AKA' is present."""
    match = re.search(r"(.+?)\s+AKA", re_field, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return re_field.strip()

class PDFHandler(FileSystemEventHandler):
    def __init__(self, folder_to_monitor):
        self.folder_to_monitor = folder_to_monitor
        self.processed_files = set()

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.pdf'):
            return
        time.sleep(1)
        if event.src_path not in self.processed_files:
            self.processed_files.add(event.src_path)
            self.process_pdf(event.src_path)

    def process_pdf(self, pdf_path, max_retries=5, retry_delay=5):
        """Extract text from each page according to the layout and pass it to main.py"""
        retries = 0
        while retries < max_retries:
            try:
                # Use `with` to open the PDF, ensuring it will close immediately after parsing
                with fitz.open(pdf_path) as doc:
                    if doc.page_count < 6:
                        print(f"PDF {pdf_path} does not contain enough pages for parsing.")
                        return

                    # Extract text for each field according to the page layout and store in variables
                    facility = doc[0].get_text().strip()
                    case_lines = doc[1].get_text().splitlines()
                    case = " ".join([line.strip() for line in case_lines if line.strip()])
                    wo_number = doc[2].get_text().strip()
                    file_number = doc[3].get_text().strip()
                    claim = doc[4].get_text().strip()
                    attn = doc[5].get_text().strip()
                    re_field = defluff_re_field(doc[6].get_text().strip()) if doc.page_count > 6 else ""
                    dob = doc[7].get_text().strip() if doc.page_count > 7 else ""

                # Prepare the arguments for the subprocess now that fitz has closed the document
                args = [
                    '--facility', facility,
                    '--case', case,
                    '--wo_number', wo_number,
                    '--file_number', file_number,
                    '--claim', claim,
                    '--attn', attn,
                    '--re_field', re_field,
                    '--dob', dob
                ]

                # Run the main executable with the parsed data
                result = subprocess.run([main_path] + args, shell=True, env=os.environ)

                if result.returncode == 0:
                    print(f"Processing of {pdf_path} completed successfully.")
                    break  # Exit the loop after successful processing
                else:
                    print(f"Processing of {pdf_path} failed with return code {result.returncode}. Retrying...")

            except Exception as e:
                print(f"Failed to process {pdf_path}: {e}. Retrying...")

            retries += 1
            time.sleep(retry_delay)

        # If all retries failed, log the issue and move the file to an error directory (optional)
        if retries == max_retries:
            print(f"Failed to process {pdf_path} after {max_retries} attempts.")
        else:
            # Ensure the PDF is released before attempting deletion
            safe_delete(pdf_path)

def start_monitoring(folder_to_monitor):
    event_handler = PDFHandler(folder_to_monitor)
    observer = Observer()
    observer.schedule(event_handler, path=folder_to_monitor, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring(monitor_folder)
