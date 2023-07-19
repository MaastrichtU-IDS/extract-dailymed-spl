import re
import csv
import sys
import os
from lxml import etree
from collections import defaultdict

class CodeInfo:
    def __init__(self):
        self.display_name = ""
        self.total_occurrences = 0
        self.matching_occurrences = 0

    def increment_total(self):
        self.total_occurrences += 1

    def increment_matching(self):
        self.matching_occurrences += 1

    def set_display_name(self, display_name):
        self.display_name = display_name

    def get_display_name(self):
        return self.display_name
    
    def get_total_occurrences(self):
        return self.total_occurrences

    def get_matching_occurrences(self):
        return self.matching_occurrences

def generate_sentence_regex(terms):
    # Construct the regex pattern. Join the escaped terms using the pipe (|) operator for alternation 
    escaped_terms = [re.escape(term) for term in terms]
    return r'[^.]*\b(' + '|'.join(escaped_terms) + r')\b[^.]*\.'

def explore(xmlfile, terms, code_dict, term_dict):
    tree = etree.parse(xmlfile)
    root = tree.getroot()

    # Get the namespace and create a namespace dictionary for XPath queries
    namespace_uri = root.tag.split('}')[0][1:]
    namespace_prefix = "ns"
    namespace_map = {namespace_prefix: namespace_uri}

    regex_pattern = generate_sentence_regex(terms)

    # Get all "section" tags that contain the child tag "code"
    for section in tree.xpath(f".//{namespace_prefix}:section[{namespace_prefix}:code]", namespaces=namespace_map):
        code_tag = section.find(f"{namespace_prefix}:code", namespaces=namespace_map)
        code = code_tag.attrib.get('code')

        # Initialize the code if not created yet
        code_info = code_dict[code]
        if code_info.get_total_occurrences() == 0:
            code_info.display_name = code_tag.attrib.get('displayName')

        has_matching = False
        for text in section.itertext():
            #? Do we need to strip the text 

            # Find all matches in the text content using regex
            matches = re.findall(regex_pattern, text)
            if matches:
                has_matching = True

            # Increase the occurrences in the term_dict for each match
            for match in matches:
                term_dict[match] += 1

        if has_matching:
            code_dict[code].increment_matching()
        code_dict[code].increment_total()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [xml file directory] [terms file]") 

    result_dir = "result" 
    code_occr_file = "result/code_occr.csv" 
    term_occr_file = "result/term_occr.csv" 

    xml_dir = sys.argv[1]
    terms_fname = sys.argv[2]
    
    terms = []
    with open(terms_fname) as file:
        terms = [line.rstrip() for line in file]

    code_dict = defaultdict(CodeInfo)
    term_dict = defaultdict(int)

    print("Exploring the code section for terms...")
    num_files = 0
    for xmlfile in [os.path.join(xml_dir, f) for f in os.listdir(xml_dir)]:
        explore(xmlfile, terms, code_dict, term_dict)
        num_files += 1
    
    print(f"Completed. Total of {num_files} file scanned.")
    print(f'Writing the statistical data in the folder "{result_dir}"...')

    os.makedirs(result_dir, exist_ok=True)

    # Print results in CSV form
    with open(code_occr_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['code', 'display name', '# of occurrence', '# of match'])
        writer.writeheader()
        writer.writerows({'code': key, 'display name': value.get_display_name(), '# of occurrence': value.get_total_occurrences(), '# of match': value.get_matching_occurrences()} for key, value in code_dict.items())

    with open(term_occr_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['term', '# of occurrence'])
        writer.writeheader()
        writer.writerows({'term': key, '# of occurrence': value} for key, value in term_dict.items())

    print("Completed.")