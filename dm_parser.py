import os
import csv
import shutil
import requests
import xml.etree.ElementTree as ET
import zipfile

# Returns xml_id, set_id, version_number, indications[]
def parse_xml(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()

	# Get the namespace
	namespace = root.tag.split('}')[0][1:]

	# Get the metadata about the drug label
	xml_id = root.find(f"{{{namespace}}}id").attrib.get('root')
	set_id = root.find(f"{{{namespace}}}setId").attrib.get('root')
	version_number = root.find(f"{{{namespace}}}versionNumber").attrib.get('value')

	indications = []

	# Find all the section with specific code
	for item in root.iter(f"{{{namespace}}}section"):
		code = item.find(f"{{{namespace}}}code")
		#TODO: iterate over the possible code values in a loop
		if code == None or (code.attrib.get('code') != '34067-9' and code.attrib.get('code') != '42229-5'):
			continue
		parag = item.find(f"{{{namespace}}}text/{{{namespace}}}paragraph")
		if parag == None:
			print(f"xml_id: {xml_id}\tset_id: {set_id}\tParagraph tag cannot found")
			continue
		if parag.text == None:
			print(f"xml_id: {xml_id}\tset_id: {set_id}\tParagraph text cannot found")
			continue
		# ! More accurate extraction methods could be used here rather than grapping the text 
		ptext = parag.text.strip()
		if len(ptext) == 0:
			print(f"xml_id: {xml_id}\tset_id: {set_id}\tParagraph text is just empty")
		else:
			indications.append(ptext)
	return xml_id, set_id, version_number, indications

def save_csv(filename, fields, row):
	with open(filename, 'w') as csvfile:
		# Creating a csv dict writer object
		writer = csv.DictWriter(csvfile, fieldnames = fields)
		writer.writeheader()
		writer.writerows(row)
	

def download_dataset(url, download_dir, zip_file_path):
	os.makedirs(download_dir, exist_ok=True)

	resp = requests.get(url)

	# Saving the zip file
	with open(zip_file_path, 'wb') as f:	
		f.write(resp.content)

def extract_dataset(zip_file_path, extraction_dir, consolidation_dir):
	extraction_dir_temp = extraction_dir + "_tmp"
	# Create the extraction and consolidation directories if they don't exist
	os.makedirs(extraction_dir, exist_ok=True)
	os.makedirs(extraction_dir_temp, exist_ok=True)
	os.makedirs(consolidation_dir, exist_ok=True)

	# Extract the zip file to the extraction directory
	with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
		zip_ref.extractall(extraction_dir_temp)

	num_zip_file = 0
	num_xml_file = 0
	# Traverse the extraction directory and locate the .zip files inside the "prescription" directory
	prescription_dir = os.path.join(extraction_dir_temp, "prescription")
	for subdir, subdirs, files in os.walk(prescription_dir):
		for file_name in files:
			if file_name.endswith('.zip'):
				num_zip_file += 1
				zip_file_path = os.path.join(subdir, file_name) 
				with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
					zip_ref.extractall(extraction_dir)

	print("Number of extracted zip file(s): " + str(num_zip_file))
	
	xml_files = [f for f in os.listdir(extraction_dir) if f.endswith('.xml')]
	for xml_file in xml_files:
		num_xml_file += 1
		xml_file_path = os.path.join(extraction_dir, xml_file)
		shutil.copy(xml_file_path, consolidation_dir)

	shutil.rmtree(extraction_dir_temp)
	shutil.rmtree(extraction_dir)
	print("Number of extracted xml file(s): " + str(num_xml_file))

if __name__ == "__main__":
	#TODO: Better naming for the directories 
	download_dir = './downloaded'
	zip_file_path = './downloaded/zipfile.zip' 
	extraction_dir = './extraction' 
	consolidation_dir = './consolidation'

	url = "https://dailymed-data.nlm.nih.gov/public-release-files/dm_spl_release_human_rx_part5.zip"

	# Download whole the dataset but keep them in the same extraction folder
	print("Downloading the DailyMed dataset...")
	download_dataset(url, download_dir, zip_file_path)

	# Extract the dataset into seperate directory 
	print("Extracting the dataset...")
	extract_dataset(zip_file_path, extraction_dir, consolidation_dir)

	# Specifying the fields for csv file
	xml_files = [os.path.join(consolidation_dir, f) for f in os.listdir(consolidation_dir) if os.path.isfile(os.path.join(consolidation_dir, f))]
	fields = ['set_id', 'xml_id', 'version_number', 'indication']

	table = []
	# Parse each .xml file inside of the newly constituted directory and save them as .csv file
	for file in xml_files:
		set_id, xml_id, version_number, indications = parse_xml(file)

		for indication in indications:
			row = {'set_id': set_id, 'xml_id': xml_id, 'version_number': version_number, 'indication': indication}
			table.append(row)
	
	csv_filename = 'result.csv'
	save_csv(csv_filename, fields, table)