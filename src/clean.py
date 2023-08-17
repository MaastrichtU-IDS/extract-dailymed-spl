import sys
import re
import random
import pandas as pd

def clean_text(text):
    regex_pattern = r'(\s){2,}\n'
    text = re.sub(regex_pattern, '\n', text).strip()
    
    # Remove non-ASCII characters
    text = ''.join([char if ord(char) < 128 else '' for char in text])

    return text

if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(f"Right usage: {sys.argv[0]} [in: dailymed.csv] [in: min-len] [in: max-len] [out: dailymed_clean.csv]") 
        
    in_file = sys.argv[1]
    min_len = int(sys.argv[2])
    max_len = int(sys.argv[3])
    out_file = sys.argv[4]
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(in_file)

    # Apply the clean_text function and filter rows by text length in one step
    df['text'] = df['text'].apply(clean_text)
    df = df[df['text'].str.len().between(min_len, max_len)]

    # Shuffle the order of filtered rows randomly (set seed for reproducibility)
    random.seed(42) 
    df_shuffled = df.sample(frac=1).reset_index(drop=True)

    # Save the shuffled and cleaned DataFrame to a CSV file
    df_shuffled.to_csv(out_file, index=False)