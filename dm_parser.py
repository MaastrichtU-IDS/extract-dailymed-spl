import os
import sys
import argparse
import requests
import gzip
import csv
import json
import yaml
from yaml.loader import SafeLoader
import time
from datetime import date
import shutil
import zipfile
import hashlib
from bs4 import BeautifulSoup
from FileMetadata import FileMetadata

def constructor(loader, node) :
    fields = loader.construct_mapping(node)
    return FileMetadata(**fields)
yaml.add_constructor('!FileMetadata', constructor)


def progressbar(it, prefix="", size=60, out=sys.stdout): 
    """ 
	A progress bar.
    
    Args:
		it: an iterable. anything that len() can be used on such as a list, a dict, or range().
		prefix: text that appears to the left of the progress bar.
		size: the size of the progress bar in characters.
		out: the stream to write to.

	Returns: 
	None
	"""
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def getCurrentDate():
	"""
	Get the current date in YYYY-MM-DD format.

	Returns
		str: The date in a YYYY-MM-DD format.
	"""
	return date.today().strftime("%Y-%m-%d")


		

def getMetadataFromFile(filepath:str) -> dict[str,FileMetadata]:
	"""
	Retrieves a metadata file at the specified filepath

	Args
		filepath:str The metadata file in yaml format to read
	
	Returns
		dict[str,FileMetadata]: A dictionary containing filenames and their metadata
	"""
	
	try:
		f = open(filepath,'r')
		with f:
			return yaml.load(f, Loader=SafeLoader)
	except OSError:
		print (f'Unable to open/read {filepath}')
	return None


def addEntryToMetadataFile(directory_path:str, filename:str, metadata:FileMetadata, metadata_filename:str = 'files.metadata.yaml') -> dict[str, FileMetadata]:
	"""
	Adds a file and its metadata to a file-based regisry of file metadata

	Args:
		directory_path:str The path to the folder to read/write a metadata file
		filename:str The name of the file for which there is metadata
		metadata:FileMetadata The metadata object
		metadata_filename:str The name of the metadata file
	
	Returns:
		The dictionary for which the metadata object was added to
	
	"""
	metadata_filename = f'{directory_path}/{metadata_filename}'
	try:
		f = open(metadata_filename,'r')
		with f:
			#metadata_dict = yaml.load(f, Loader=SafeLoader)
			metadata_dict = yaml.full_load(f)

	except OSError:
		print (f'Unable to open/read {metadata_filename}')
		metadata_dict = {}

	metadata_dict[filename] = metadata
	try:
		with open(metadata_filename,'w') as f:
			yaml.dump(metadata_dict, f, default_flow_style=False)
	except OSError:
		print (f'Unable to write to {metadata_filename}')
	return 	metadata_dict


def makeFileList():
	"""Generate a list of files to process. Parses command line argument (--files) or generates from preset Dailymed file names.
	
	Returns:
	dict:Dictionary containing FileMetadata descriptions of files
	"""
	files = {}
	args = argParser.parse_args()
	if args.files in ['all','prescription','otc']:
		if args.files in ['all','prescription']:
			for i in range (1,6):
				f = FileMetadata()
				f.filename = f'dm_spl_release_human_rx_part{i}.zip'
				files[f.filename] = f
		if args.files in ['all','otc']:
			for i in range (1,10):
				f = FileMetadata()
				f.filename = f'dm_spl_release_otc_part{i}.zip'
				files[f.filename] = f
	elif len(args.files) > 1 :
		file_list = args.files.split(",")
		for filename in file_list:
			f = FileMetadata()
			f.filename = filename
			files[f.filename] = f
	return files

def getPaths():
	""" Provides a list of of directories from the args-provided working directory.
	It names and creates the follwoing directories
	* working_dir = working directory
	* download_dir = base directory for all downloads
	* dated_download_dir = a directory that has a date in the form of YYYY-MM-DD
	* extraction_dir = a directory to contain zip-extracted files
	* result_dir = a directory to contain the results of the application
	
	Returns:
	dict:Dictionary containing application paths
	"""
	args = argParser.parse_args()
	dirs = {}
	dirs['working_dir'] = args.working_dir
	dirs['download_dir']= f'{args.working_dir}/download'
	dirs['dated_download_dir'] = f'{args.working_dir}/download/{args.date}' 
	dirs['extraction_dir']= f'{args.working_dir}/extract'
	dirs['result_dir']= f'{args.working_dir}/results'
	
	os.makedirs(dirs['download_dir'], exist_ok=True)
	os.makedirs(dirs['extraction_dir'], exist_ok=True)
	os.makedirs(dirs['result_dir'], exist_ok=True)
	# we don't create dated download dir until we need it.

	dirs['download_metadata_filename'] = f'{args.working_dir}/download/files.meta.yaml'
	return dirs

def checkFiles(files: dict[str, FileMetadata]) -> dict[str, FileMetadata]:
	"""
	A function to check whether there is existing metadata in the specified directory, and if so, return the input dict with the read object.

	Args:
		files: (Dict[str, FileMetadata]) : A dictionary with filename as string key and FileMetadata values

	Return:
		Dict[str, FileMetadata]: A dictionary with filenames as string key and FileMetadata as values
	"""
	args = argParser.parse_args()
	paths = getPaths()
	download_metadata = getMetadataFromFile(paths['download_metadata_filename'])
	
	for filename in files:
		# check in dated folder first
		file_metadata_filename = paths['dated_download_dir']+f'/{filename}.meta.yaml'	
		if(os.path.exists(file_metadata_filename) == True):
			try:
				f = open(file_metadata_filename,'r')
				with f:
					#file_metadata = yaml.load(f, Loader=SafeLoader)
					all_files_metadata = yaml.full_load(f)
					file_metadata = all_files_metadata[filename]

					# check that the file actually exists.
					if os.path.exists(file_metadata.filepath):
						files[filename] = file_metadata
					else:
						print(f'Found metadata for {filename}, but file does not exist!')

			except OSError:
				print (f'Unable to open/read {file_metadata_filename}')
				continue
		
		# check the metadata in the download folder			
		elif download_metadata != None and filename in download_metadata:
			# check that the file actually exists.
			file_metadata = download_metadata[filename]
			if os.path.exists(file_metadata.filepath):
				files[filename] = file_metadata
			else:
				print(f'Found metadata for {filename}, but file does not exist!')
		else:
			print(f'No metadata found for {filename}')
	return files

def computeMD5Hash(filepath: str):
	""" 
	Open,close, read file and calculate MD5 on its contents 

	Args:
		filepath (str): The full path to the file to compute the hash.

	Return:
		str: The MD5 hash
	"""
	with open(filepath, 'rb') as f:
		md5_returned = hashlib.md5(f.read()).hexdigest()
		return md5_returned


def download(files: dict[str, FileMetadata]) -> dict[str, FileMetadata]:
	"""
	Download the Dailymed release files.
	 
	Download the Dailymed release files if 1) they don't already exist or 2) we force re-download

	Args:
		files: a dictionary comprised of filename and their FileMetadata 

	Return:
		dict[str, FileMetadata] Updated files and their metadata
	"""
	paths = getPaths()

	for filename in files:
		file_metadata = files[filename]
		download_dir = paths['download_dir']
		dated_download_dir = paths['dated_download_dir']		
		local_file_path = f'{dated_download_dir}/{filename}'
		meta_file = f'{dated_download_dir}/{filename}.meta.yaml'
		url = f'https://dailymed-data.nlm.nih.gov/public-release-files/{filename}'

		# query the header for the ETag
		response = requests.head(url)
		remote_etag = response.headers["ETag"].strip('"')

		# check whether we have downloaded this previously
		if remote_etag == file_metadata.etag:
			# we already have this file
			print(f'Most recent eTag of {filename} is same as remote version')
			if args.force == True:
				print(f'Forcing download as commanded')
			else:
				if file_metadata.filepath != '':
					print(f'Skipping download of {filename}')
					continue
				else:
					print(f'{filename} does not exist in local filesystem')					

		# if not, download it
		print(f'Downloading the DailyMed Human Prescription File {url} to {local_file_path}...')	
		
		# Retrieve and save the file
		os.makedirs(dated_download_dir, exist_ok=True)
		#with requests.get(url, stream=True) as r:
		#	with open(local_file_path, 'wb') as f:
		#		shutil.copyfileobj(r.raw, f)
	    
		# create file metadata
		metadata = FileMetadata()
		metadata.filename = filename
		metadata.etag = remote_etag
		metadata.filepath = local_file_path
		metadata.dateCreated = getCurrentDate()
		metadata.originUrl = url
		metadata.originOrg = data_source
		metadata.script = os.path.basename(__file__)
		#metadata.md5 = computeMD5Hash(local_file_path)
		
		files[filename] = metadata

		# add to the file-specific metadata to the download folder
		addEntryToMetadataFile(dated_download_dir, filename, metadata, f'{filename}.meta.yaml')

		# add to the metadata for all files in the download folder
		addEntryToMetadataFile(download_dir, filename, metadata)
	return files

# Each release zip file contains a set of SPL specific zip files. Each SPL contains one xml file. 
# This function will extract all XML files to the extraction directory
def extract(files):
	paths = getPaths()
	download_dir = paths['download_dir']
	extraction_dir = paths['extraction_dir']

	n_package_files = 0
	n_zip_files = 0
	n_xml_files = 0
	
	for filename in files:
		meta = files[filename]
		zip_file_path = meta.filepath
		with zipfile.ZipFile(zip_file_path, 'r') as zf:
			print(f'Processing {filename}')
			n_package_files += 1
			for f in zf.namelist():
				# if zip file, then open and extract xml file
				if f.endswith(".zip"):
					with zf.open(f) as f2:
						n_zip_files += 1

						with zipfile.ZipFile(f2, 'r') as zf2:
							for f3 in zf2.namelist():
								if f3.endswith('.xml'):

									#zf2.extract(f3, extraction_dir)
									xml_fp = zf2.open(f3)
									with gzip.open(f'{extraction_dir}/{f3}.gz', 'wb') as gz_fp:
										gz_fp.write(xml_fp.read())

									n_xml_files += 1

	print("Number of package zip file(s): " + str(n_package_files))
	print("Number of extracted zip file(s): " + str(n_zip_files))
	print("Number of extracted xml file(s): " + str(n_xml_files))

def process():
	paths = getPaths()
	extraction_dir = paths['extraction_dir']
	result_dir = paths['result_dir']	
	
	hashes = {}
	indications = []
	files= os.listdir(extraction_dir)
	for i in progressbar(range(len(files)), "Computing: ", 40):
		file = files[i]
		path = f'{extraction_dir}/{file}'

		with gzip.open(path, 'rb') as f:
			xml_string = f.read() 
			soup = BeautifulSoup(xml_string, 'xml')

			set_id = soup.setId['root']
			xml_id = soup.id['root']
			version_number = soup.versionNumber['value']
			
			sections = soup.find_all('section')
			for section in sections:
				for code in section.find_all('code', attrs = {'code':'34067-9'}):
					indication = ' '.join(section.text.split())
					row = {'set_id': set_id, 'xml_id': xml_id, 'version_number': version_number, 'indication': indication}
					myhash = hash(yaml.dump(row)) 
					if myhash not in hashes: # do not include duplicates
						indications.append(row)
						hashes[hash] = True
			
			# [^.]*\b(treatment|abnormal)\b[^.]*\.
			#if i == 2: break
	
	# Creating a csv dict writer object
	with open(f'{result_dir}/indications.csv', 'w') as csvfile:	
		fields = ['set_id', 'xml_id', 'version_number', 'indication']
		writer = csv.DictWriter(csvfile, fieldnames = fields, delimiter=",")
		writer.writeheader()
		writer.writerows(indications)


if __name__ == "__main__":
	startTime = time.time()
	argParser = argparse.ArgumentParser(
			prog="Dailymed Parser",
			description="Downloads and parses Dailymed product labels"
	)
	data_source = "dailymed"
	argParser.add_argument("-w", "--working_dir", default='/data/'+data_source, help="Directory to download files into")
	argParser.add_argument("-d", "--download", default=True, help="Download content, if it hasn't already been downloaded.")
	argParser.add_argument("-f", "--force", default=False, action="store_true", help="Replace files, even if they were previously downloaded")
	argParser.add_argument("-a", "--date", default=getCurrentDate(), help=f'Use data from specified date in format of YYYY-MM-DD')
	argParser.add_argument("-s", "--files", default='prescription', help=f'Specify a comma-separated list of the files to download/process. options: all|prescription|otc')
	argParser.add_argument("-e", "--extract", default=True, help=f'Extract XML files from download files')
	argParser.add_argument("-p", "--process", default=True, help=f'Extract XML files from download files')
	args = argParser.parse_args()
	
	# get file list from command line, or the default set
	files = checkFiles(makeFileList())

	if(args.download == True):
		download(files)

	if (args.extract == True):
		extract(files)

	if(args.process == True):
		process()
	
	executionTime = (time.time() - startTime)
	print(f'Execution time: {executionTime} seconds')