import sys
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def create_gold_standard_dataset_inplace(df, similarity_threshold=0.9):
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the paragraphs using TF-IDF
    tfidf_matrix = vectorizer.fit_transform(df['text'])

    # Calculate cosine similarities between paragraphs
    cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Initialize a set to keep track of selected paragraph indices
    selected_indices = set()

    # Iterate through each paragraph and find similar paragraphs
    for i in range(len(cosine_similarities)):
        if i not in selected_indices:
            similar_indices = set(
                idx for idx, sim in enumerate(cosine_similarities[i])
                if sim >= similarity_threshold and idx != i
            )
            selected_indices.update(similar_indices)
    
    # Mark the selected paragraphs as True in the 'selected' column
    df['selected'] = df.index.isin(selected_indices)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [in: dailymed.csv] [out: dailymed_filtered.csv]") 

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(input_filename)

    # Handle NaN values by filling them with an empty string
    df['text'].fillna('', inplace=True)

    # Apply the create_gold_standard_dataset_inplace function
    create_gold_standard_dataset_inplace(df, similarity_threshold=0.6)

    # Create a DataFrame containing only dissimilar paragraphs
    dissimilar_df = df[~df['selected']]

    # Write the dissimilar paragraphs to the output CSV file
    dissimilar_df.to_csv(output_filename, index=False)