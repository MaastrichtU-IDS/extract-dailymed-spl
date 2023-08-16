import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

def create_gold_standard_dataset(paragraphs, similarity_threshold=0.9):
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the paragraphs using TF-IDF
    tfidf_matrix = vectorizer.fit_transform(paragraphs)

    # Calculate cosine similarities between paragraphs
    cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Create a dictionary to store groups of similar paragraphs
    similar_paragraphs = defaultdict(list)

    # Iterate through the cosine similarity matrix
    for i in range(len(cosine_similarities)):
        for j in range(i + 1, len(cosine_similarities)):
            if cosine_similarities[i][j] > similarity_threshold:
                # Add similar paragraphs to the same group
                similar_paragraphs[i].append(j)
                similar_paragraphs[j].append(i)

    # Create a list to store the selected representative paragraphs
    representative_paragraphs = []

    # Create a set to keep track of already selected representative indices
    selected_representative_indices = set()

    # Iterate through the groups of similar paragraphs
    for group in similar_paragraphs.values():
        # Select the paragraph with the highest TF-IDF score as representative
        representative_index = max(group, key=lambda index: max(tfidf_matrix[index].toarray()[0]))
        representative_paragraphs.append(paragraphs[representative_index])

        # Check if the index is already selected as representative
        if representative_index not in selected_representative_indices:
            representative_paragraphs.append(paragraphs[representative_index])
            selected_representative_indices.update(group)  # Mark all similar indices as selected

        # Print the group
        print("================")
        for j in group:
            print(f"&>:\n{paragraphs[j]}\n\n")
            
    return representative_paragraphs

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [in: dailymed.csv] [out: dailymed_filtered.csv]") 

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(input_filename)

    # Handle NaN values by filling them with an empty string
    df['text'].fillna('', inplace=True)

    # Extract paragraphs from the DataFrame
    paragraphs = df['text'].tolist()

    # Create a gold standard dataset with representative paragraphs (indication texts)
    gold_standard_dataset = create_gold_standard_dataset(paragraphs, similarity_threshold=0.7)

    # Create a DataFrame containing only dissimilar paragraphs
    dissimilar_df = df[~df['text'].isin(gold_standard_dataset)]

    # Write the dissimilar paragraphs to the output CSV file
    dissimilar_df.to_csv(output_filename, index=False)