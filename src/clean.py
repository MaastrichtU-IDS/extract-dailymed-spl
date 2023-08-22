import argparse
import re
import random
import pandas as pd

def clean_text(text):
    cleaned_text = re.sub(r'\n+', '\n', text)
    cleaned_text = re.sub(r'\n\s+', '\n', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = re.sub(r'^\d* ','', cleaned_text)
    cleaned_text = re.sub(r'\d* INDICATIONS AND USAGE','', cleaned_text)
    cleaned_text = cleaned_text.encode("ascii", "ignore").decode()
    return cleaned_text.strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and shuffle text data from a CSV file.")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to the output CSV file")
    args = parser.parse_args()

    in_file = args.input_file
    out_file = args.output_file
    
    df = pd.read_csv(in_file)

    df['text'] = df['text'].apply(clean_text)
    df = df.drop_duplicates(subset=['text'])

    random.seed(42)
    df_shuffled = df.sample(frac=1).reset_index(drop=True)

    df_shuffled.to_csv(out_file, index=False)