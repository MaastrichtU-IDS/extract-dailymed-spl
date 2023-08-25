import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def create_gold_standard_dataset(df, similarity_threshold):
    print("Vectorizing text...")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['text'])

    print("Calculating cosine similarities...")
    cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)

    print("Finding similar paragraphs...")
    selected_indices = set()

    for i in range(len(cosine_similarities)):
        if i not in selected_indices:
            similar_indices = set(
                idx for idx, sim in enumerate(cosine_similarities[i])
                if sim >= similarity_threshold and idx != i
            )
            selected_indices.update(similar_indices)
    
    # Drop selected paragraphs
    df.drop(index=selected_indices, inplace=True)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a gold standard dataset by removing similar paragraphs from a CSV file.")
    parser.add_argument("input_csv", type=str, help="Path to the input CSV file.")
    parser.add_argument("similarity_threshold", type=float, help="Threshold for cosine similarity.")
    parser.add_argument("output_csv", type=str, help="Path to the output CSV file.")
    args = parser.parse_args()

    print("Loading CSV file...")
    df = pd.read_csv(args.input_csv)
    total_paragraphs = len(df)

    print("Applying gold standard dataset creation...")
    create_gold_standard_dataset(df, args.similarity_threshold)

    num_retained_paragraphs = len(df)
    num_removed_paragraphs = total_paragraphs - num_retained_paragraphs
    percent_removed = (num_removed_paragraphs / total_paragraphs) * 100

    print("Writing dissimilar paragraphs to output CSV...")
    df.to_csv(args.output_csv, index=False)

    print("\nSummary:")
    print(f"Total paragraphs: {total_paragraphs}")
    print(f"Retained paragraphs: {num_retained_paragraphs}")
    print(f"Removed paragraphs: {num_removed_paragraphs}")
    print(f"Percentage removed: {percent_removed:.2f}%")
    print("Done!")