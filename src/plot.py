import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
import plotly.express as px
import csv
import sys

def plot_tsne(sentences, out_file):
    # Get sentence embeddings
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    embeddings = model.encode(sentences)
    # Compute t-SNE embeddings
    tsne_embeddings = TSNE(n_components=2, random_state=42).fit_transform(embeddings)
    # Create an interactive plot
    df = pd.DataFrame(tsne_embeddings, columns=['x', 'y'])
    df['sentence'] = sentences
    fig = px.scatter(df, x='x', y='y', hover_data=['sentence'])
    fig.write_image(out_file)

def load_indications(filename):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row['text'])
    return data

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [in: dailymed.csv] [plot.png]") 

    print("Loading indication data from CSV file...")
    ind = load_indications(sys.argv[1])
    
    print("Generating t-SNE plot...")
    plot_tsne(ind, sys.argv[2])

    print("t-SNE plot generated and saved.")