import pandas as pd
import re
import os
import gzip

folder = "./data"
os.makedirs(folder, exist_ok=True)

csvfile = f"{folder}/indications_full_text.csv"
cleancsv = f"{folder}/indications_clean.csv"
cleanjsonl = f"{folder}/indications_clean.jsonl"
smallercsv = f"{folder}/indications_clean_150_to_600.csv"
smallerjsonl = f"{folder}/indications_clean_150_to_600.jsonl"
hist_plot = f"{folder}/indication_distribution.png"


def clean(text):
    return re.sub(r"(\s){2,}", "\n", text.strip().encode("ascii", "ignore").decode())


df = (
    pd.read_csv(csvfile)
    .drop_duplicates("indication")
    .sample(frac=1)
    .reset_index(drop=True)
)

df["indication_cleaned"] = df.apply(lambda row: clean(row["indication"]), axis=1)
df["length"] = df.apply(lambda row: len(row["indication_cleaned"]), axis=1)

cleandf = df.drop("indication", axis=1)
cleandf.to_csv(cleancsv)
cleandf.to_json(cleanjsonl, orient="records", lines=True)
with open(cleanjsonl, "rb") as f_in, gzip.open(cleanjsonl + ".gz", "wb") as f_out:
    f_out.writelines(f_in)


smallerdf = cleandf[cleandf["length"].between(150, 600)]
smallerdf.to_csv(smallercsv)
smallerdf.to_json(smallerjsonl, orient="records", lines=True)
with open(smallerjsonl, "rb") as f_in, gzip.open(smallerjsonl + ".gz", "wb") as f_out:
    f_out.writelines(f_in)


### plotting
d = df.drop(
    ["set_id", "xml_id", "indication", "version_number", "indication_cleaned"], axis=1
)
plot = d.plot(kind="hist", bins=500)
plot.set_xlim(0, 5000)
plot.figure.savefig(hist_plot)
