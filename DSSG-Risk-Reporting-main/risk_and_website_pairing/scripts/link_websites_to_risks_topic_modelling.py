from pathlib import Path
import pandas as pd
import json
import numpy as np
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA

# === Paths ===
risk_file = Path("data/risk_list.csv")
website_dir = Path("data/websites/with_summary")
output_dir = Path("data/risk_website_pairs/topic_modelling")
output_dir.mkdir(parents=True, exist_ok=True)

# === Model Config ===
embedding_model = SentenceTransformer("all-MiniLM-L12-v2")

umap_model = UMAP(
    n_neighbors=10,
    n_components=2,
    min_dist=0.1,
    metric="cosine",
    random_state=11
)

hdbscan_model = HDBSCAN(
    min_cluster_size=10,
    min_samples=2,
    prediction_data=True,
    cluster_selection_method='leaf'
)

vectorizer_model = CountVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_df=1.0,
    min_df=2,
    max_features=5000
)

# === Functions ===
def load_risk_descriptions(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["Risk Description"])
    df["Risk Description"] = df["Risk Description"].astype(str).str.strip()

    # Simple preprocessing without bigram modeling
    df["Processed"] = df["Risk Description"].str.lower().str.strip()

    return df[["Risk Name", "Risk Description", "Processed"]]

def load_website_articles(directory: Path):
    articles = []
    for file_path in directory.glob("*.json"):
        with open(file_path, "r") as f:
            data = json.load(f)
            for item in data:
                articles.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "") or item.get("text", ""),
                    "summary": item.get("summary", ""),
                    "source_file": file_path.name
                })
    df = pd.DataFrame(articles)
    df = df[df["content"].str.strip().astype(bool)]
    return df.reset_index(drop=True)

# === Main Pipeline ===
def run_risk_website_matching_tm():
    print("Loading data...")
    risk_df = load_risk_descriptions(risk_file)
    web_df = load_website_articles(website_dir)

    if risk_df.empty or web_df.empty:
        print("No data found.")
        return

    print("Embedding risk descriptions...")
    risk_embeddings = embedding_model.encode(risk_df["Processed"].tolist(), show_progress_bar=True)

    print("Running BERTopic...")
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        calculate_probabilities=True,
        verbose=True
    )

    topics, _ = topic_model.fit_transform(risk_df["Processed"].tolist(), risk_embeddings)

    # Count number of outliers and topics
    num_outliers = topics.count(-1)
    num_topics = len(set(topics)) - (1 if -1 in topics else 0)

    print(f"Identified {num_topics} topics")
    print(f"Number of outlier documents: {num_outliers}")

    risk_df["Assigned Topic"] = topics

    # Add top 10 keywords with weights for each topic
    risk_df["Topic Keywords"] = risk_df["Assigned Topic"].apply(
        lambda t: ", ".join([f"{word} ({weight:.2f})" for word, weight in topic_model.get_topic(t)[:10]]) if t != -1 else ""
    )

    # Group risks by topic for structured JSON output
    grouped_topics = {}
    for topic_id in sorted(risk_df["Assigned Topic"].unique()):
        if topic_id == -1:
            continue  # skip outliers
        topic_risks = risk_df[risk_df["Assigned Topic"] == topic_id]
        grouped_topics[str(topic_id)] = {
            "topic_keywords": ", ".join([
                f"{word} ({weight:.2f})" for word, weight in topic_model.get_topic(topic_id)[:10]
            ]),
            "risks": [
                {
                    "risk_name": row["Risk Name"],
                    "description": row["Risk Description"],
                    "processed": row["Processed"]
                }
                for _, row in topic_risks.iterrows()
            ]
        }

    with open(output_dir / "risk_topics.json", "w") as f:
        json.dump(grouped_topics, f, indent=2)

    print("Embedding website articles...")
    web_embeddings = embedding_model.encode(web_df["content"].tolist(), show_progress_bar=True)

    # Dimensionality reduction
    common_dim = 128
    pca_risk = PCA(n_components=min(common_dim, len(risk_embeddings)))
    pca_web = PCA(n_components=min(common_dim, len(web_embeddings)))

    risk_proj = pca_risk.fit_transform(risk_embeddings)
    web_proj = pca_web.fit_transform(web_embeddings)

    final_dim = min(risk_proj.shape[1], web_proj.shape[1])
    risk_proj = risk_proj[:, :final_dim]
    web_proj = web_proj[:, :final_dim]

    # Build topic vectors
    topic_vectors = {}
    topic_to_risks = {}
    for topic_id in risk_df["Assigned Topic"].unique():
        if topic_id == -1:
            continue
        idxs = risk_df[risk_df["Assigned Topic"] == topic_id].index
        vecs = [risk_proj[i] for i in idxs]
        topic_vectors[topic_id] = np.mean(vecs, axis=0)
        topic_to_risks[topic_id] = risk_df.loc[idxs, "Risk Name"].tolist()

    # Match website articles to topic vectors
    threshold = 0.5
    matches = []

    print(f"Matching website articles to topics (threshold = {threshold})...")
    for i, web_vec in enumerate(web_proj):
        for topic_id, topic_vec in topic_vectors.items():
            sim = cosine_similarity([web_vec], [topic_vec])[0][0]
            if sim >= threshold:
                matches.append({
                    "title": web_df.loc[i, "title"],
                    "url": web_df.loc[i, "url"],
                    "summary": web_df.loc[i, "summary"] if web_df.loc[i, "summary"] else web_df.loc[i, "content"][:200] + "...",
                    "matched_topic": topic_id,
                    "similarity": sim,
                    "topic_keywords": ", ".join([f"{word} ({weight:.2f})" for word, weight in topic_model.get_topic(topic_id)[:10]]),
                    "related_risks": topic_to_risks[topic_id]
                })

    # Group website matches by risk name
    risk_links = {}
    for match in matches:
        topic_id = match["matched_topic"]
        risks = topic_to_risks.get(topic_id, [])
        for risk_name in risks:
            if risk_name not in risk_links:
                risk_links[risk_name] = {
                    "matched_topic": int(topic_id),  # Convert numpy.int64 to int for JSON serialization
                    "topic_keywords": match["topic_keywords"],
                    "matching_articles": []
                }
            risk_links[risk_name]["matching_articles"].append({
                "title": match["title"],
                "url": match["url"],
                "summary": match["summary"],
                "similarity": float(match["similarity"])  # Convert numpy.float to float
            })

    if not risk_links:
        print("No matches found. Consider lowering threshold.")
    else:
        with open(output_dir / "website_topic_links.json", "w") as f:
            json.dump(risk_links, f, indent=2)
        print(f"Saved matches to: {output_dir / 'website_topic_links.json'}")

