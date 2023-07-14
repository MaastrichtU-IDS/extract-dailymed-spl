import re
import sys
import csv
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

def detect(xmlfile, terms, csv_writer, code_dict, term_dict):
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    # Get the namespace
    namespace = root.tag.split('}')[0][1:]

    # Get the metadata about the drug labelx"
    set_id = root.find(f"{{{namespace}}}setId").attrib.get('root')
    xml_id = root.find(f"{{{namespace}}}id").attrib.get('root')

    sentence_regex = re.compile(r'[^.!?]*[.!?]', re.IGNORECASE)

    row = {'xml_id': xml_id, 'set_id': set_id, 'code': '', 'indication': ''}
    
    # Find all the section with specific code
    for item in root.iter(f"{{{namespace}}}section"):
        #TODO: Is there a section that includes indication sentence but does not have code section
        code_tag = item.find(f"{{{namespace}}}code")
        if code_tag == None:
            print(f"Error {xml_id}: has no code")
            continue
        code = code_tag.attrib.get('code')
        row['code'] = code

        code_occr = 0

        for text in item.itertext():
            # Trim the white spaces if any 
            spl_text = text.strip()
            if len(spl_text) == 0:
                continue

            # First get all the sentences in the section
            sentences = re.findall(sentence_regex, text)
            for sentence in sentences:
                for term in terms:
                    # Search terms in the sentence
                    term_regex = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)

                    if re.search(term_regex, sentence):
                        # Increase the occurance for the code and term
                        term_dict[term] += 1 #! Term occurance is misleading since we are not checking all of them
                        code_occr += 1
                        row['indication'] = sentence
                        csv_writer.writerow(row)
                        break
        code_dict[code] += code_occr 

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

    with open(result_fname, 'w') as csvfile:
        code_dict = defaultdict(int)
        term_dict = defaultdict(int)

        writer = csv.DictWriter(csvfile, ['xml_id', 'set_id', 'code', 'indication'])
        writer.writeheader()

        for xmlfile in [os.path.join(xml_dir, f) for f in os.listdir(xml_dir)]:
            detect(xmlfile, terms, writer, code_dict, term_dict)

        print("Codes & Occurances")
        print("===================================")
        for key, value in code_dict.items():
            print(f"{key}\t{value}")

        print("Terms & Occurances")
        print("===================================")
        for key, value in term_dict.items():
            print(f"{key}\t{value}")