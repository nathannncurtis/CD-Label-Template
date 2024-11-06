import os
import time
import fitz
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
                
                # Add Re: and DOB as extracted values from additional pages or text
                # Assuming page 7 is `Re:` and page 8 is `DOB:`
                re_field = doc[6].get_text().strip() if doc.page_count > 6 else ""
                dob = doc[7].get_text().strip() if doc.page_count > 7 else ""

                # Call main.py with parsed data as command-line arguments
                subprocess.run([
                    'python', 'main.py',
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
    folder_to_monitor = r'\\NAS-PROD\Production\DIGIBOX\Nathan\(00) ASSIGNMENTS'
    start_monitoring(folder_to_monitor)
