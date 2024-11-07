import os
import sys
import argparse
import logging

# Initialize logging at the top
logging.basicConfig(filename="main_log.txt", level=logging.DEBUG)
logging.debug("Starting main script")

# Supress all output
# sys.stdout = open(os.devnull, 'w')
# sys.stderr = open(os.devnull, 'w')

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--facility', type=str, required=False)
parser.add_argument('--case', type=str, required=False)
parser.add_argument('--wo_number', type=str, required=False)
parser.add_argument('--file_number', type=str, required=False)
parser.add_argument('--claim', type=str, required=False)
parser.add_argument('--attn', type=str, required=False)
parser.add_argument('--re_field', type=str, required=False)
parser.add_argument('--dob', type=str, required=False)
args = parser.parse_args()

# Function to read configuration from a text file
def read_config(file_path=".config"):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
        output_folder = config.get("output_folder")
        if not output_folder:
            raise ValueError("'output_folder' must be specified in the config file.")
        logging.debug(f"Output folder from config: {output_folder}")
        return output_folder
    except Exception as e:
        logging.error(f"Failed to read configuration file: {e}")
        sys.exit(1)  # Exit if config is not properly set

# Get output folder from config file
output_folder = read_config()

# Function to handle data insertion with either arguments or user input
def get_or_prompt(input_data, prompt_text):
    return input_data if input_data is not None else input(prompt_text)

# Read the .tdd file as binary
with open("blank.tdd", "rb") as file:
    file_data = bytearray(file.read())

# .tdd is just xml, with a png thumbnail at the top, and the logo as a jpeg in .b64
# Original offsets from the blank template (constant in the template, used as reference points in script)
# Respects order of the file structure in hexadecimal, therefore must dynamically calculate offsets in this order

"""""""""Original Offsets from Blank Template File"""""""""

facility_offset = 0x33FA       # Facility starts at 0x33FA in the blank file 
original_case_offset = 0x3690  # Case starts at 0x3690 in the blank file 
original_wo_offset = 0x3696    # WO# starts at 0x3696 in the blank file
original_file_offset = 0x369F  # File# starts at 0x369F in the blank file
original_claim_offset = 0x36A9  # Claim# starts at 0x36A9 in the blank file
original_attn_offset = 0x36B1   # Attn starts at 0x36B1 in the blank file
original_re_offset = 0x9489     # Re: starts at 0x9489 in the blank file
original_dob_offset = 0x9490    # DOB: starts at 0x9490 in the blank file

# Append carriage return and newline (CRLF) after the Facility input only (I don't know why this works, but it does)
def append_crlf_to_facility(input_string):
    return (input_string + '\r\n').encode('ascii')  # 0D 0A 

# Use arguments if provided, otherwise prompt user
facility_input = get_or_prompt(args.facility, "Enter the Facility: ")
facility_bytes = append_crlf_to_facility(facility_input)

# Insert Facility data into the correct location without overwriting existing bytes
file_data = file_data[:facility_offset] + facility_bytes + file_data[facility_offset:]

# Calculate the new offset for Case based on the length of the Facility input
facility_end_offset = facility_offset + len(facility_bytes)
new_case_offset = original_case_offset + (facility_end_offset - facility_offset)

# Case data
case_input = get_or_prompt(args.case, "Enter the Case: ")
case_bytes = case_input.encode('ascii')
file_data = file_data[:new_case_offset] + case_bytes + file_data[new_case_offset:]

# WO# data
case_end_offset = new_case_offset + len(case_bytes)
new_wo_offset = original_wo_offset + (case_end_offset - original_case_offset)
wo_input = get_or_prompt(args.wo_number, "Enter the WO#: ")
wo_bytes = wo_input.encode('ascii')
file_data = file_data[:new_wo_offset] + wo_bytes + file_data[new_wo_offset:]

# File# data
wo_end_offset = new_wo_offset + len(wo_bytes)
new_file_offset = original_file_offset + (wo_end_offset - original_wo_offset)
file_input = get_or_prompt(args.file_number, "Enter the File#: ")
file_bytes = file_input.encode('ascii')
file_data = file_data[:new_file_offset] + file_bytes + file_data[new_file_offset:]

# Claim# data
file_end_offset = new_file_offset + len(file_bytes)
new_claim_offset = original_claim_offset + (file_end_offset - original_file_offset)
claim_input = get_or_prompt(args.claim, "Enter the Claim: ")
claim_bytes = claim_input.encode('ascii')
file_data = file_data[:new_claim_offset] + claim_bytes + file_data[new_claim_offset:]

# Attn data
claim_end_offset = new_claim_offset + len(claim_bytes)
new_attn_offset = original_attn_offset + (claim_end_offset - original_claim_offset)
attn_input = get_or_prompt(args.attn, "Enter the Attn: ")
attn_bytes = attn_input.encode('ascii')
file_data = file_data[:new_attn_offset] + attn_bytes + file_data[new_attn_offset:]

# Re: data
attn_end_offset = new_attn_offset + len(attn_bytes)
new_re_offset = original_re_offset + (attn_end_offset - original_attn_offset)
re_input = get_or_prompt(args.re_field, "Enter the Re: ")
re_bytes = re_input.encode('ascii')
file_data = file_data[:new_re_offset] + re_bytes + file_data[new_re_offset:]

# DOB data
re_end_offset = new_re_offset + len(re_bytes)
new_dob_offset = original_dob_offset + (re_end_offset - original_re_offset)
dob_input = get_or_prompt(args.dob, "Enter the DOB: ")
dob_bytes = dob_input.encode('ascii')
file_data = file_data[:new_dob_offset] + dob_bytes + file_data[new_dob_offset:]

# Write the modified file data back to a new .tdd file
output_filename = os.path.join(output_folder, f"{re_input}.tdd")
with open(output_filename, "wb") as file:
    file.write(file_data)

print(f"Facility inserted at {hex(facility_offset)}, Case inserted at {hex(new_case_offset)}, WO# inserted at {hex(new_wo_offset)}, File# inserted at {hex(new_file_offset)}, Claim inserted at {hex(new_claim_offset)}, Attn inserted at {hex(new_attn_offset)}, Re: inserted at {hex(new_re_offset)}, DOB inserted at {hex(new_dob_offset)}")

