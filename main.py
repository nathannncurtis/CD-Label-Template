# Read the .tdd file as binary
with open("blank.tdd", "rb") as file:
    file_data = bytearray(file.read())

# .tdd is just xml, with a png thumbnail at the top, and the logo as a jpeg in .b64
# Original offsets from the blank template (constant in the template, used a reference points in script)
# Respects order of the file structure in hexadecimal, therefore must dynamically calculate offsets in this order

"""""""""Original Offsets from Blank Template File"""""""""

facility_offset = 0x3405       # Facility starts at 0x3405 in the blank file 
original_case_offset = 0x369A  # Case starts at 0x369A in the blank file 
original_wo_offset = 0x36A0    # WO# starts at 0x36A0 in the blank file
original_file_offset = 0x36A9  # File# starts at 0x36A9 in the blank file
original_claim_offset = 0x36B3  # Claim# starts at 0x36B3 in the blank file
original_attn_offset = 0x36BB   # Attn starts at 0x36BB in the blank file
original_re_offset = 0x9493     # Re: starts at 0x9493 in the blank file
original_dob_offset = 0x949A    # DOB: starts at 0x949A in the blank file

# Append carriage return and newline (CRLF) after the Facility input only (I don't know why this works, but it does)
def append_crlf_to_facility(input_string):
    return (input_string + '\r\n').encode('ascii')  # 0D 0A 

# Get Facility input as string and append CRLF
facility_input = input("Enter the Facility: ")
facility_bytes = append_crlf_to_facility(facility_input)

# Insert Facility data into the correct location without overwriting existing bytes
file_data = file_data[:facility_offset] + facility_bytes + file_data[facility_offset:]

# Calculate the new offset for Case based on the length of the Facility input
facility_end_offset = facility_offset + len(facility_bytes)

# Dynamically calculate where Case should go, based on how much space Facility took up
new_case_offset = original_case_offset + (facility_end_offset - facility_offset)

# Get Case input from user 
case_input = input("Enter the Case: ")
case_bytes = case_input.encode('ascii') 

# Insert Case data at the dynamically adjusted offset
file_data = file_data[:new_case_offset] + case_bytes + file_data[new_case_offset:]

# Calculate the new offset for WO# dynamically based on the length of Case input
case_end_offset = new_case_offset + len(case_bytes)

# Now dynamically adjust the new WO# offset based on where Case ends
new_wo_offset = original_wo_offset + (case_end_offset - original_case_offset)

# Get WO# input from user 
wo_input = input("Enter the WO#: ")
wo_bytes = wo_input.encode('ascii') 

# Insert WO# data at the dynamically adjusted offset
file_data = file_data[:new_wo_offset] + wo_bytes + file_data[new_wo_offset:]

# Calculate the new offset for file# dynamically based on the length of WO# input
wo_end_offset = new_wo_offset + len(wo_bytes)

# Dynamically adjust the new file# offset based on where WO# ends
new_file_offset = original_file_offset + (wo_end_offset - original_wo_offset)

# Get file# input from user 
file_input = input("Enter the File#: ")
file_bytes = file_input.encode('ascii') 

# Insert file# data at the dynamically adjusted offset
file_data = file_data[:new_file_offset] + file_bytes + file_data[new_file_offset:]

# Calculate the new offset for claim dynamically based on the length of file# input
file_end_offset = new_file_offset + len(file_bytes)

# Dynamically adjust the new claim offset based on where file# ends
new_claim_offset = original_claim_offset + (file_end_offset - original_file_offset)

# Get claim input from user 
claim_input = input("Enter the Claim: ")
claim_bytes = claim_input.encode('ascii') 

# Insert claim data at the dynamically adjusted offset
file_data = file_data[:new_claim_offset] + claim_bytes + file_data[new_claim_offset:]

# Calculate the new offset for attn dynamically based on the length of claim input
claim_end_offset = new_claim_offset + len(claim_bytes)

# Dynamically adjust the new attn offset based on where claim ends
new_attn_offset = original_attn_offset + (claim_end_offset - original_claim_offset)

# Get attn input from user 
attn_input = input("Enter the Attn: ")
attn_bytes = attn_input.encode('ascii') 

# Insert attn data at the dynamically adjusted offset
file_data = file_data[:new_attn_offset] + attn_bytes + file_data[new_attn_offset:]

# Calculate the new offset for re: dynamically based on the length of attn input
attn_end_offset = new_attn_offset + len(attn_bytes)

# Dynamically adjust the new re: offset based on where attn ends
new_re_offset = original_re_offset + (attn_end_offset - original_attn_offset)

# Get re: input from user 
re_input = input("Enter the Re: ")
re_bytes = re_input.encode('ascii') 

# Insert re: data at the dynamically adjusted offset
file_data = file_data[:new_re_offset] + re_bytes + file_data[new_re_offset:]

# Calculate the new offset for dob: dynamically based on the length of re: input
re_end_offset = new_re_offset + len(re_bytes)

# Dynamically adjust the new dob: offset based on where re: ends
new_dob_offset = original_dob_offset + (re_end_offset - original_re_offset)

# Get dob: input from user 
dob_input = input("Enter the DOB: ")
dob_bytes = dob_input.encode('ascii') 

# Insert dob: data at the dynamically adjusted offset
file_data = file_data[:new_dob_offset] + dob_bytes + file_data[new_dob_offset:]

# Write the modified file data back to a new .tdd file
output_filename = f"{re_input}.tdd"
with open(output_filename, "wb") as file:
    file.write(file_data)

print(f"Facility inserted at {hex(facility_offset)}, Case inserted at {hex(new_case_offset)}, WO# inserted at {hex(new_wo_offset)}, File# inserted at {hex(new_file_offset)}, Claim inserted at {hex(new_claim_offset)}, Attn inserted at {hex(new_attn_offset)}, Re: inserted at {hex(new_re_offset)}, DOB inserted at {hex(new_dob_offset)}")
