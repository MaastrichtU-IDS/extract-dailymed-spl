import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
import plotly.express as px
import csv
import sys
import multiprocessing

def process_data(sentences, tsne_embeddings):
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    embeddings = model.encode(sentences)
    
    tsne_result = TSNE(n_components=2, random_state=42).fit_transform(embeddings)
    
    tsne_embeddings.extend(tsne_result)

def load_and_process_data(file_path, tsne_embeddings):
    print(f"Loading and processing data from '{file_path}'...")
    sentences = []
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            sentences.append(row['text'])

    process_data(sentences, tsne_embeddings)
    print(f"Data processing completed for '{file_path}'.")

def plot_tsne_multiprocess(input_csv1, input_csv2, out_file):
    tsne_embeddings1, tsne_embeddings2 = multiprocessing.Manager().list(), multiprocessing.Manager().list()

    process1 = multiprocessing.Process(target=load_and_process_data, args=(input_csv1, tsne_embeddings1))
    process2 = multiprocessing.Process(target=load_and_process_data, args=(input_csv2, tsne_embeddings2))

    process1.start()
    process2.start()

    process1.join()
    process2.join()

    print("All data processed. Creating t-SNE plot...")

    tsne_array1 = np.array(tsne_embeddings1)
    tsne_array2 = np.array(tsne_embeddings2)

    df1 = pd.DataFrame(tsne_array1, columns=['x', 'y'])
    df2 = pd.DataFrame(tsne_array2, columns=['x', 'y'])
    df1['sentence'] = input_csv1
    df2['sentence'] = input_csv2
    df = pd.concat([df1, df2], ignore_index=True)
    df['dataset'] = ['Dataset 1'] * len(df1) + ['Dataset 2'] * len(df2)
    
    fig = px.scatter(df, x='x', y='y', color='dataset', hover_data=['sentence'])
    
    print("Plot created. Saving t-SNE plot as an image...")

    fig.write_image(out_file)
    print(f"Plot saved as '{out_file}'")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(f"Usage: {sys.argv[0]} [input_csv_file1] [input_csv_file2] [output_image_file]") 

    input_csv1 = sys.argv[1]
    input_csv2 = sys.argv[2]
    output_image = sys.argv[3]

    print("Starting t-SNE Visualization")

    plot_tsne_multiprocess(input_csv1, input_csv2, output_image)

    print("Completed.")
