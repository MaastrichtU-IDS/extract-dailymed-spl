import re
import sys
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

def detect(xmlfile, terms, result_file, code_dict, term_dict):
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    # Get the namespace
    namespace = root.tag.split('}')[0][1:]

    # Get the metadata about the drug labelx"
    set_id = root.find(f"{{{namespace}}}setId").attrib.get('root')

    # Find all the section with specific code
    for item in root.iter(f"{{{namespace}}}section"):
        for text in item.itertext():
            # Trim the white spaces if any 
            spl_text = text.strip()
            if len(spl_text) == 0:
                continue

            for term in terms:
                regex = f'[A-Za-z," ]+{term}[A-Za-z," ]+'
                matches = re.findall(regex, spl_text)
                if not matches:
                    continue
                code_tag = item.find(f"{{{namespace}}}code")
                if code_tag == None:
                    print(f"Error {set_id}: has no code")
                    continue
                code = code_tag.attrib.get('code')

                # Increase the count for the code section
                code_dict[code] += 1
                term_dict[term] += 1

                # Print all the matches
                for match in matches: 
                    result_file.write(f"{set_id}\t{code}\t{match}\n")


# Sample usage python detect_section.py ./consolidation terms.txt result.txt
if __name__ == "__main__":  
    if len(sys.argv) != 4:
        sys.exit(f"Right usage: {sys.argv[0]} <xml directory> <terms file> <result file>") 

    xml_dir = sys.argv[1]
    terms_fname = sys.argv[2]
    result_fname = sys.argv[3]
    
    terms = []
    with open(terms_fname) as file:
        terms = [line.rstrip() for line in file]

    with open(result_fname, 'w') as result_file:
        code_dict = defaultdict(int)
        term_dict = defaultdict(int)
        for xmlfile in [os.path.join(xml_dir, f) for f in os.listdir(xml_dir)]:
            detect(xmlfile, terms, result_file, code_dict, term_dict)

        print("Codes & Occurances")
        print("===================================")
        for key, value in code_dict.items():
            print(f"{key}\t{value}")

        print("Terms & Occurances")
        print("===================================")
        for key, value in term_dict.items():
            print(f"{key}\t{value}")