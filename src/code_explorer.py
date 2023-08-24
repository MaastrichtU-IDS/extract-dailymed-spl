import re
import csv
import os
import argparse
from lxml import etree
from collections import defaultdict

class CodeInfo:
    def __init__(self):
        self.display_name = ""
        self.term_dist = defaultdict(int)
        self.total_occurrences = 0
        self.matching_occurrences = 0

    def increment_total(self):
        self.total_occurrences += 1

    def increment_matching(self):
        self.matching_occurrences += 1
    
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
        if code_info.total_occurrences == 0:
            code_info.display_name = code_tag.attrib.get('displayName')

        has_matching = False
        for text in section.itertext():
            # Find all matches in the text content using regex
            matches = re.findall(regex_pattern, text)
            if matches:
                has_matching = True

            # Increase the occurrences in the term_dict for each match
            for match in matches:
                term_dict[match] += 1
                code_dict[code].term_dist[match] += 1

        if has_matching:
            code_dict[code].increment_matching()
        code_dict[code].increment_total()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explore XML files and generate statistical data.")
    parser.add_argument("xml_directory", type=str, help="Path to the directory containing XML files.")
    parser.add_argument("terms_file", type=str, help="Path to the file containing terms.")
    args = parser.parse_args()

    result_dir = "result"
    code_occr_file = os.path.join(result_dir, "code_occr.csv")
    code_occr_dist_file = os.path.join(result_dir, "code_occr_dist.csv")
    term_occr_file = os.path.join(result_dir, "term_occr.csv")

    xml_dir = args.xml_directory
    terms_fname = args.terms_file

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

    print(f"Completed. Total of {num_files} file(s) scanned.")
    print(f'Writing the statistical data in the folder "{result_dir}"...')

    os.makedirs(result_dir, exist_ok=True)

    # Sort the list according to matching occurrences
    sorted_code_list = sorted(code_dict.items(), key=lambda item: item[1].matching_occurrences, reverse=True)
    sorted_term_list = sorted(term_dict.items(), key=lambda item: item[1], reverse=True)
    
    # Print the results in CSV form
    with open(code_occr_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['code', 'display name', '# of occurrence', '# of match'])
        writer.writeheader()
        writer.writerows({
            'code': code_val, 
            'display name': code_info.display_name, 
            '# of occurrence': code_info.total_occurrences, 
            '# of match': code_info.matching_occurrences
        } for (code_val, code_info) in sorted_code_list)

    with open(code_occr_dist_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['code', 'display name', '# of occurrence', '# of match', 'distribution of terms'])
        writer.writeheader()
        writer.writerows({
            'code': code_val, 
            'display name': code_info.display_name, 
            '# of occurrence': code_info.total_occurrences, 
            '# of match': code_info.matching_occurrences, 
            'distribution of terms': '\n'.join([f'{occr}:\t {term}' for (term, occr) in sorted(code_info.term_dist.items(), key=lambda item: item[1], reverse=True)])
        } for (code_val, code_info) in sorted_code_list)

    with open(term_occr_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['term', '# of occurrence'])
        writer.writeheader()
        writer.writerows({'term': term, '# of occurrence': occr} for (term, occr) in sorted_term_list)

    print("Completed.")