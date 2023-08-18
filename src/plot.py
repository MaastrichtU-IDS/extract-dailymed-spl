import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
import plotly.express as px
import csv
import sys

def plot_tsne(sentences, out_file):
    print("Generating sentence embeddings...")
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    embeddings = model.encode(sentences)
    
    print("Performing t-SNE dimensionality reduction...")
    tsne_embeddings = TSNE(n_components=2, random_state=42).fit_transform(embeddings)
    
    print("Creating t-SNE plot...")
    df = pd.DataFrame(tsne_embeddings, columns=['x', 'y'])
    df['sentence'] = sentences
    fig = px.scatter(df, x='x', y='y', hover_data=['sentence'])
    
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
    if len(sys.argv) != 3:
        sys.exit(f"Usage: {sys.argv[0]} [input_csv_file] [output_image_file]") 

    input_csv = sys.argv[1]
    output_image = sys.argv[2]

    indications = load_indications(input_csv)
    
    plot_tsne(indications, output_image)

    print("Completed")
