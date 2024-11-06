import os
import time
import fitz
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFHandler(FileSystemEventHandler):
    def __init__(self, folder_to_monitor):
        self.folder_to_monitor = folder_to_monitor
        self.processed_files = set()

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.pdf'):
            return

        # Wait a moment to ensure file is fully created
        time.sleep(1)

        if event.src_path not in self.processed_files:
            self.processed_files.add(event.src_path)
            self.process_pdf(event.src_path)

    def process_pdf(self, pdf_path):
        try:
            with fitz.open(pdf_path) as doc:
                text = ""
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    text += page.get_text()
                self.extract_data(text)
        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")

    def process_pdf(self, pdf_path):
        try:
            with fitz.open(pdf_path) as doc:
                # Map pages to each required field based on your layout
                facility, case, wo_number, file_number, claim, attn = None, None, None, None, None, None

                # Iterate through each page and extract the text
                if doc.page_count >= 6:  # Ensure there are at least 6 pages
                    facility = doc[0].get_text().strip()  # Page 1
                    # Page 2 - concatenate lines into a single string with spaces
                    case_lines = doc[1].get_text().splitlines()
                    case = " ".join([line.strip() for line in case_lines if line.strip()])
                    wo_number = doc[2].get_text().strip()  # Page 3
                    file_number = doc[3].get_text().strip()  # Page 4
                    claim = doc[4].get_text().strip()  # Page 5
                    attn = doc[5].get_text().strip()  # Page 6

                # Print only non-blank data
                print("Parsed data:")
                if facility:
                    print(f"  Facility: {facility}")
                if case:
                    print(f"  Case: {case}")
                if wo_number:
                    print(f"  WO#: {wo_number}")
                if file_number:
                    print(f"  File#: {file_number}")
                if claim:
                    print(f"  Claim#: {claim}")
                if attn:
                    print(f"  Attn: {attn}")

        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")


def start_monitoring(folder_to_monitor):
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
    folder_to_monitor = r'\\NAS-PROD\Production\DIGIBOX\Nathan\(00) ASSIGNMENTS' 
    start_monitoring(folder_to_monitor)
