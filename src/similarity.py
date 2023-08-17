import sys
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
    if len(sys.argv) != 4:  
        sys.exit(f"Right usage: {sys.argv[0]} [in: in.csv] [in: similarity_threshold] [out: out.csv]") 

    input_filename = sys.argv[1]
    similarity_threshold = float(sys.argv[2])
    output_filename = sys.argv[3]

    print("Loading CSV file...")
    df = pd.read_csv(input_filename)
    total_paragraphs = len(df)

    print("Applying gold standard dataset creation...")
    create_gold_standard_dataset(df, similarity_threshold)

    num_retained_paragraphs = len(df)
    num_removed_paragraphs = total_paragraphs - num_retained_paragraphs
    percent_removed = (num_removed_paragraphs / total_paragraphs) * 100

    print("Writing dissimilar paragraphs to output CSV...")
    df.to_csv(output_filename, index=False)

    print("\nSummary:")
    print(f"Total paragraphs: {total_paragraphs}")
    print(f"Retained paragraphs: {num_retained_paragraphs}")
    print(f"Removed paragraphs: {num_removed_paragraphs}")
    print(f"Percentage removed: {percent_removed:.2f}%")
    print("Done!")