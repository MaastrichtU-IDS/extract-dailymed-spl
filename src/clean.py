import sys
import re
import random
import pandas as pd

def clean_text(text):
    cleaned_text = re.sub(r'\n+', '\n', text)  # Remove extra line breaks
    cleaned_text = re.sub(r'\n\s+', '\n', cleaned_text)  # Remove leading spaces after line breaks
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'^\d* ','', cleaned_text)
    cleaned_text = re.sub(r'\d* INDICATIONS AND USAGE','', cleaned_text)
    cleaned_text = re.sub(r'INDICATIONS AND USAGE','', cleaned_text)
    cleaned_text = cleaned_text.encode("ascii", "ignore").decode()
    return cleaned_text

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [input_csv_file] [output_csv_file]") 
        
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(in_file)

    # Apply the clean_text function and filter rows by text length in one step
    df['text'] = df['text'].apply(clean_text)
    # df = df[df['text'].str.len().between(min_len, max_len)]

    df.drop_duplicates(subset=['text'])

    # Shuffle the order of filtered rows randomly (set seed for reproducibility)
    random.seed(42) 
    df_shuffled = df.sample(frac=1).reset_index(drop=True)

    # Save the shuffled and cleaned DataFrame to a CSV file
    df_shuffled.to_csv(out_file, index=False)