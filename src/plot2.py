import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
import plotly.express as px
import csv
import sys

def plot_tsne(sentences1, sentences2, out_file):
    print("Generating sentence embeddings...")
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    embeddings1 = model.encode(sentences1)
    embeddings2 = model.encode(sentences2)
    
    print("Performing t-SNE dimensionality reduction...")
    tsne_embeddings1 = TSNE(n_components=2, random_state=42).fit_transform(embeddings1)
    tsne_embeddings2 = TSNE(n_components=2, random_state=42).fit_transform(embeddings2)
    
    print("Creating t-SNE plot...")
    df1 = pd.DataFrame(tsne_embeddings1, columns=['x', 'y'])
    df2 = pd.DataFrame(tsne_embeddings2, columns=['x', 'y'])
    df1['sentence'] = sentences1
    df2['sentence'] = sentences2
    df = pd.concat([df1, df2], ignore_index=True)
    df['dataset'] = ['Dataset 1'] * len(df1) + ['Dataset 2'] * len(df2)
    
    fig = px.scatter(df, x='x', y='y', color='dataset', hover_data=['sentence'])
    
    print("Saving t-SNE plot as an image...")
    fig.write_image(out_file)
    print(f"Plot saved as {out_file}")

def load_indications(filename):
    print(f"Loading indication data from '{filename}'...")
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row['text'])
    print(f"Loaded {len(data)} indications")
    return data

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(f"Usage: {sys.argv[0]} [input_csv_file1] [input_csv_file2] [output_image_file]") 

    input_csv1 = sys.argv[1]
    input_csv2 = sys.argv[2]
    output_image = sys.argv[3]

    print("Starting t-SNE Visualization Script")
    
    # Load indication data from CSV files
    indications1 = load_indications(input_csv1)
    indications2 = load_indications(input_csv2)
    
    # Generate and save t-SNE plot
    plot_tsne(indications1, indications2, output_image)

    print("Completed.")
