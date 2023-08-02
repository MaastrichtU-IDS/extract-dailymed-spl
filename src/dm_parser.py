import os
import sys
import argparse
import requests
import gzip
import csv
import yaml
import time
from datetime import date
import shutil
import zipfile
import hashlib
from bs4 import BeautifulSoup
from FileMetadata import FileMetadata
import re


def constructor(loader, node):
    fields = loader.construct_mapping(node)
    return FileMetadata(**fields)


yaml.add_constructor("!FileMetadata", constructor)


def progressbar(it, prefix="", size=60, out=sys.stdout):
    """
        A progress bar.

    Args:
                it: an iterable. anything that len() can be used on such as a list,
                    a dict, or range().
                prefix: text that appears to the left of the progress bar.
                size: the size of the progress bar in characters.
                out: the stream to write to.

        Returns:
        None
    """
    count = len(it)

    def show(j):
        x = int(size * j / count)
        print(
            "{}[{}{}] {}/{}".format(prefix, "#" * x, "." * (size - x), j, count),
            end="\r",
            file=out,
            flush=True,
        )

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    print("\n", flush=True, file=out)


def getScriptName():
    return os.path.basename(__file__)


def getCurrentDate():
    """
    Get the current date in YYYY-MM-DD format.

    Returns
            str: The date in a YYYY-MM-DD format.
    """
    return date.today().strftime("%Y-%m-%d")


def getMetadataFromFile(filepath: str) -> dict[str, FileMetadata]:
    """
    Retrieves a metadata file at the specified filepath

    Args
            filepath:str The metadata file in yaml format to read

    Returns
            dict[str,FileMetadata]: A dictionary containing filenames and their metadata
    """

    try:
        f = open(filepath, "r")
        with f:
            return yaml.full_load(f)  # yaml.load(f, Loader=SafeLoader)
    except OSError:
        print(f"Unable to open/read {filepath}")
    return None


def addEntryToMetadataFile(
    directory_path: str,
    filename: str,
    metadata: FileMetadata,
    metadata_filename: str = "files.meta.yaml",
) -> dict[str, FileMetadata]:
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
    metadata_filename = f"{directory_path}/{metadata_filename}"
    try:
        f = open(metadata_filename, "r")
        with f:
            # metadata_dict = yaml.load(f, Loader=SafeLoader)
            metadata_dict = yaml.full_load(f)

    except OSError:
        print(f"Unable to open/read {metadata_filename}")
        metadata_dict = {}

    metadata_dict[filename] = metadata
    try:
        with open(metadata_filename, "w") as f:
            yaml.dump(metadata_dict, f, default_flow_style=False)
    except OSError:
        print(f"Unable to write to {metadata_filename}")
    return metadata_dict


def makeFileList():
    """Generate a list of files to process. Parses command line argument (--files)
        or generates from preset Dailymed file names.

    Returns:
    dict:Dictionary containing FileMetadata descriptions of files
    """
    files = {}
    args = argParser.parse_args()
    if args.files in ["all", "prescription", "otc"]:
        if args.files in ["all", "prescription"]:
            for i in range(1, 6):
                f = FileMetadata()
                f.filename = f"dm_spl_release_human_rx_part{i}.zip"
                f.status = "requested"
                files[f.filename] = f
        if args.files in ["all", "otc"]:
            for i in range(1, 10):
                f = FileMetadata()
                f.filename = f"dm_spl_release_human_otc_part{i}.zip"
                f.status = "requested"
                files[f.filename] = f
    elif len(args.files) > 1:
        file_list = args.files.split(",")
        for filename in file_list:
            f = FileMetadata()
            f.filename = filename
            f.status = "requested"
            files[f.filename] = f
    return files


def getPaths():
    """Provides a list of of directories from the args-provided working directory.
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
    dirs["working_dir"] = args.working_dir
    dirs["download_dir"] = f"{args.working_dir}/download"
    dirs["dated_download_dir"] = f"{args.working_dir}/download/{args.date}"
    dirs["extraction_dir"] = f"{args.working_dir}/extract"
    dirs["result_dir"] = f"{args.working_dir}/results"

    os.makedirs(dirs["download_dir"], exist_ok=True)
    os.makedirs(dirs["extraction_dir"], exist_ok=True)
    os.makedirs(dirs["result_dir"], exist_ok=True)
    # we don't create dated download dir until we need it.

    dirs["download_metadata_filename"] = f"{args.working_dir}/download/files.meta.yaml"
    return dirs


def checkFiles(files: dict[str, FileMetadata]) -> dict[str, FileMetadata]:
    """
    A function to check whether there is existing metadata in the specified directory,\
        and if so, return the input dict with the read object.

    Args:
            files: (Dict[str, FileMetadata]) : A dictionary with filename as string key\
                and FileMetadata values

    Return:
            Dict[str, FileMetadata]: A dictionary with filenames as string key \
                and FileMetadata as values
    """
    argParser.parse_args()
    paths = getPaths()
    download_metadata = getMetadataFromFile(paths["download_metadata_filename"])

    for filename in files:
        file_metadata = files[filename]

        # check in dated folder first
        file_metadata_filename = paths["dated_download_dir"] + f"/{filename}.meta.yaml"
        if os.path.exists(file_metadata_filename) is True:
            try:
                f = open(file_metadata_filename, "r")
                with f:
                    all_files_metadata = yaml.full_load(f)

                    try:
                        f_metadata = all_files_metadata[filename]

                        # check that the file actually exists.
                        if os.path.exists(f_metadata.filepath):
                            f_metadata.status = "file_exists"
                            files[filename] = f_metadata
                        else:
                            print(
                                f"Found metadata for {filename}, \
                                    but file does not exist!"
                            )
                            file_metadata.status = "file_does_not_exist"
                            files[filename] = file_metadata
                    except Exception:
                        print(f"{filename} not in {file_metadata_filename}")
                        file_metadata.status = "file_does_not_exist"
                        files[filename] = file_metadata
            except OSError:
                print(f"Unable to open/read {file_metadata_filename}")
                file_metadata.status = "file_does_not_exist"
                files[filename] = file_metadata
                continue

        # check the metadata in the download folder
        elif download_metadata is not None and filename in download_metadata:
            # check that the file actually exists.
            f_metadata = download_metadata[filename]
            if os.path.exists(f_metadata.filepath):
                f_metadata.status = "file_exists"
                files[filename] = f_metadata
            else:
                print(f"Found metadata for {filename}, but file does not exist!")
                f_metadata.status = "file_does_not_exist"
                files[filename] = f_metadata
        else:
            print(f"No metadata found for {filename}")
            file_metadata.status = "file_does_not_exist"
            files[filename] = file_metadata

    return files


def computeMD5Hash(filepath: str):
    """
    Open,close, read file and calculate MD5 on its contents

    Args:
            filepath (str): The full path to the file to compute the hash.

    Return:
            str: The MD5 hash
    """
    with open(filepath, "rb") as f:
        md5_returned = hashlib.md5(f.read()).hexdigest()
        return md5_returned


def download(files: dict[str, FileMetadata]) -> dict[str, FileMetadata]:
    """
    Download the Dailymed release files.

    Download the Dailymed release files if 1) they don't already exist or 2)
    we force re-download

    Args:
            files: a dictionary comprised of filename and their FileMetadata

    Return:
            dict[str, FileMetadata] Updated files and their metadata
    """
    paths = getPaths()

    for filename in files:
        file_metadata = files[filename]
        download_dir = paths["download_dir"]
        dated_download_dir = paths["dated_download_dir"]
        local_file_path = f"{dated_download_dir}/{filename}"
        url = f"https://dailymed-data.nlm.nih.gov/public-release-files/{filename}"

        # query the header for the ETag
        response = requests.head(url)
        remote_etag = None
        try:
            remote_etag = response.headers["ETag"].strip('"')
        except Exception:
            print(f"No etag for {url}")

        # check whether we have downloaded this previously
        if remote_etag is not None and remote_etag == file_metadata.etag:
            # we already have this file
            print(f"Most recent eTag of {filename} is same as remote version")
            if args.force is True:
                print("Forcing download as commanded")
            else:
                if file_metadata.filepath != "":
                    print(f"Skipping download of {filename}")
                    continue
                else:
                    print(f"{filename} does not exist in local filesystem")

        # if not, download it
        print(
            f"Downloading the DailyMed Human Prescription File {url} \
                to {local_file_path}..."
        )

        # Retrieve and save the file
        os.makedirs(dated_download_dir, exist_ok=True)
        with requests.get(url, stream=True) as r:
            with open(local_file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)

        # create file metadata
        metadata = FileMetadata()
        metadata.filename = filename
        metadata.etag = remote_etag
        metadata.filepath = local_file_path
        metadata.dateCreated = getCurrentDate()
        metadata.originUrl = url
        metadata.originOrg = data_source
        metadata.script = getScriptName()
        metadata.md5 = computeMD5Hash(local_file_path)

        files[filename] = metadata

        # add to the file-specific metadata to the download folder
        addEntryToMetadataFile(
            dated_download_dir, filename, metadata, f"{filename}.meta.yaml"
        )

        # add to the metadata for all files in the download folder
        addEntryToMetadataFile(download_dir, filename, metadata)
    return files


# Each release zip file contains a set of SPL specific zip files.
# Each SPL contains one xml file.
# This function will extract all XML files to the extraction directory
def extract(files):
    paths = getPaths()
    paths["download_dir"]
    extraction_dir = paths["extraction_dir"]

    n_package_files = 0
    n_zip_files = 0
    n_xml_files = 0
    xml_files = {}

    for filename in files:
        meta = files[filename]
        zip_file_path = meta.filepath
        with zipfile.ZipFile(zip_file_path, "r") as zf:
            print(f"Processing {filename}")
            n_package_files += 1
            for f in progressbar(zf.namelist(), "Extracting: ", 40):
                # if zip file, then open and extract xml file
                if f.endswith(".zip"):
                    with zf.open(f) as f2:
                        n_zip_files += 1

                        with zipfile.ZipFile(f2, "r") as zf2:
                            xml_file_counter = 0
                            for f3 in zf2.namelist():
                                if f3.endswith(".xml"):
                                    # zf2.extract(f3, extraction_dir)
                                    xml_fp = zf2.open(f3)
                                    gz_xml_filepath = f"{extraction_dir}/{f3}.gz"
                                    with gzip.open(gz_xml_filepath, "wb") as gz_fp:
                                        gz_fp.write(xml_fp.read())

                                        xml_metadata = FileMetadata(
                                            filename=f"{f3}.gz",
                                            filepath=gz_xml_filepath,
                                            dateCreated=getCurrentDate,
                                            md5=computeMD5Hash(gz_xml_filepath),
                                            script=getScriptName(),
                                        )

                                        xml_files[gz_xml_filepath] = xml_metadata

                                    n_xml_files += 1

                                    xml_file_counter += 1
                                    if xml_file_counter > 1:
                                        print(
                                            f"Found {xml_file_counter} xml files for \
                                                  {f}"
                                        )

    print("Number of package zip file(s): " + str(n_package_files))
    print("Number of extracted zip file(s): " + str(n_zip_files))
    print("Number of extracted xml file(s): " + str(n_xml_files))
    return xml_files


def process(xml_files):
    paths = getPaths()
    extraction_dir = paths["extraction_dir"]
    result_dir = paths["result_dir"]

    hashes = {}
    files = {}
    indications = []
    if len(xml_files) == 0:
        for xml_file in os.listdir(extraction_dir):
            metadata = FileMetadata(
                filename=xml_file, filepath=f"{extraction_dir}/{xml_file}"
            )
            files[xml_file] = metadata
    else:
        files = xml_files

    for file in progressbar(files, "Processing: ", 40):
        metadata = files[file]
        # path = f'{extraction_dir}/{file}'
        path = metadata.filepath

        with gzip.open(path, "rb") as f:
            xml_string = f.read()
            soup = BeautifulSoup(xml_string, "xml")

            set_id = soup.setId["root"]
            xml_id = soup.id["root"]
            version_number = soup.versionNumber["value"]

            sections = soup.find_all("section")
            for section in sections:
                for code in section.find_all("code", attrs={"code": "34067-9"}):
                    # Replace the matching sequences with a single newline
                    # [^.]*\b(treatment|abnormal)\b[^.]*\.
                    text = re.sub(r"(\s){2,}", "\n", section.text.strip())

                    # indication = ' '.join(section.text.split())
                    row = {
                        "set_id": set_id,
                        "xml_id": xml_id,
                        "version_number": version_number,
                        "length": len(text),
                        "indication": text,
                    }
                    myhash = hash(yaml.dump(row))
                    if myhash not in hashes:  # do not include duplicates
                        indications.append(row)
                        hashes[hash] = True
            # if i == 2: break

    # Creating a csv dict writer object
    with open(f"{result_dir}/indications.csv", "w") as csvfile:
        fields = ["set_id", "xml_id", "version_number", "length", "indication"]
        writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=",")
        writer.writeheader()
        writer.writerows(indications)


if __name__ == "__main__":
    startTime = time.time()
    argParser = argparse.ArgumentParser(
        prog="Dailymed Parser",
        description="Downloads and parses Dailymed product labels",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    data_source = "dailymed"
    argParser.add_argument(
        "-w",
        "--working_dir",
        default="/data/" + data_source,
        help="Directory to download files into",
    )
    argParser.add_argument(
        "-d",
        "--download",
        default=True,
        help="Download content, if it hasn't already been downloaded.",
    )
    argParser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Replace files, even if they were previously downloaded",
    )
    argParser.add_argument(
        "-a",
        "--date",
        default=getCurrentDate(),
        help="Use data from specified date in format of YYYY-MM-DD",
    )
    argParser.add_argument(
        "-s",
        "--files",
        default="prescription",
        help="Specify a comma-separated list of the files to download/process. \
            options: all|prescription|otc",
    )
    argParser.add_argument(
        "-e", "--extract", default=True, help="Extract XML files from download files"
    )
    argParser.add_argument(
        "-p", "--process", default=True, help="Extract XML files from download files"
    )
    args = argParser.parse_args()

    # get file list from command line, or the default set
    files = checkFiles(makeFileList())

    if args.download == "True":
        files = download(files)

    xml_files = {}
    if args.extract == "True":
        xml_files = extract(files)

    if args.process == "True":
        process(xml_files)

    executionTime = time.time() - startTime
    print(f"Execution time: {executionTime} seconds")
