import random
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics import classification_report, accuracy_score
from catboost import CatBoostClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from typing import List, Tuple


def set_seed(seed=42):
    """
    To set the seed for reproducibility across iterations.
    """
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def encode_texts(embedder: object, texts: List[str], batch_size=32) -> np.ndarray:
    """
    Encode text into specified embedder.
    
    Args:
        embedder (object): Sentence embedding model 
        texts (List[str]): List of cleaned content to encode 
        batch_size (int): Number of texts to process per batch
    
    Returns:
        np.ndarray: Array of embeddings corresponding to text
    """
    return embedder.encode(texts, batch_size=batch_size, show_progress_bar=True)

def pseudo_labeling(model: object, embedder: object, unlabelled_texts: List[str], conf_threshold=0.9, max_samples=None) -> Tuple[List[str], List[int]]:
    """
    Applies pseudo label on unlabelled text based on confidence 
    
    Args: 
        model (object): Trained classifier model
        embedder (object): Sentence embeddding model
        unlabelled_texts (List[str]): List of unlabelled content 
        conf_threshold (float): Minimum probability to be considered "confident" (Default: 0.9)
        max_samples (int): Maximum number of samples to return. If none, all returned (Default: None)
        
    Returns:
        Tuple[List[str], List[int]]: List of text confidentally labelled, list of labels corresponding to each
    """
    unlabelled_embeds = encode_texts(embedder, unlabelled_texts)
    probs = model.predict_proba(unlabelled_embeds)

    candidates = []
    for i, prob in enumerate(probs):
        max_prob = max(prob)
        pred_label = np.argmax(prob)
        if max_prob >= conf_threshold:
            candidates.append((unlabelled_texts[i], pred_label, max_prob))

    candidates = sorted(candidates, key=lambda x: x[2], reverse=True)

    if max_samples is not None:
        candidates = candidates[:max_samples]

    pseudo_texts = [c[0] for c in candidates]
    pseudo_labels = [c[1] for c in candidates]

    return pseudo_texts, pseudo_labels

def plot_thresholds(all_val_probs, all_val_true):
    """
    Plots precision-recall curve and the best threshold based on F1 score
    
    Args:
        all_val_probs (List[float]): List of probabilities of validation set
        all_val_true (List[int]): List of labels of validation set
    """

    all_val_probs = np.array(all_val_probs)
    all_val_true = np.array(all_val_true)

    precision, recall, thresholds = precision_recall_curve(all_val_true, all_val_probs)

    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-8)

    best_f1_idx = np.argmax(f1_scores)
    best_f1_threshold = thresholds[best_f1_idx]
    best_f1 = f1_scores[best_f1_idx]

    print(f"Best threshold by F1: {best_f1_threshold:.3f} with F1: {best_f1:.3f}")

    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, label="Precision-Recall Curve")
    plt.scatter(recall[best_f1_idx], precision[best_f1_idx], color='red', label=f"Best F1 Threshold ({best_f1_threshold:.2f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    plt.grid()
    plt.show()

def main():
    """
    Training semi-supervised classification model to determine "risk-event" vs. not
    """
    set_seed(42)

    labelled_df = pd.read_csv("data/labelled.csv")
    unlabelled_df = pd.read_csv("data/unlabelled.csv")
    X = labelled_df["cleaned_text"].tolist()
    y = labelled_df["risk"].tolist()
    unlabelled_texts_original = unlabelled_df["cleaned_text"].tolist()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=30)

    fold_accuracies = []
    
    all_val_probs = []
    all_val_true = []


    for fold, (train_index, val_index) in enumerate(skf.split(X, y)):
        print(f"\n=== Fold {fold+1} ===")

        X_train_texts = [X[i] for i in train_index]
        y_train_labels = [y[i] for i in train_index]
        X_val_texts = [X[i] for i in val_index]
        y_val_labels = [y[i] for i in val_index]

        X_val_embed = encode_texts(embedder, X_val_texts)

        unlabelled_texts = unlabelled_texts_original.copy()

        max_iter = 3
        threshold = 0.95
        acc = None

        for iteration in range(max_iter):
            print(f"\n--- Iteration {iteration+1} ---")

            X_train_embed = encode_texts(embedder, X_train_texts)

            classes = np.unique(y_train_labels)
            weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train_labels)
            class_weights = weights.tolist()

            model = CatBoostClassifier(
                iterations=300,
                learning_rate=0.03,
                depth=4,
                random_seed=42,
                verbose=0,
                class_weights=class_weights
            )
            model.fit(X_train_embed, y_train_labels)

            pseudo_texts, pseudo_labels = pseudo_labeling(model, embedder, unlabelled_texts, conf_threshold=threshold, max_samples=25)

            unlabelled_texts = [text for text in unlabelled_texts if text not in pseudo_texts]

            print(f"Selected {len(pseudo_labels)} pseudo-labeled samples")

            if len(pseudo_labels) == 0:
                print("No more high-confidence samples, stopping early.")
                break  

            X_train_texts.extend(pseudo_texts)
            y_train_labels.extend(pseudo_labels)

            y_pred = model.predict(X_val_embed)
            acc = accuracy_score(y_val_labels, y_pred)

            print(f"Validation Accuracy: {acc:.4f}")
            print(classification_report(y_val_labels, y_pred))
        
        y_val_probs = model.predict_proba(X_val_embed)[:, 1]

        all_val_probs.extend(y_val_probs)
        all_val_true.extend(y_val_labels)

        fold_accuracies.append(acc)

    avg_acc = np.mean(fold_accuracies)
    print(f"\nAverage CV Accuracy: {avg_acc:.4f}")
    plot_thresholds(all_val_probs, all_val_true)
    
    # To save model, uncomment code: 
    # model.save_model("model/catboost_model_updated.cbm")
    # print("Model saved!")
    
    # After all pseudo-labeling iterations, to update unlabelled dataset:
    unlabelled_df = unlabelled_df[~unlabelled_df["cleaned_text"].isin(X_train_texts)].reset_index(drop=True)
    unlabelled_df.to_csv("data/unlabelled_updated.csv", index=False)
    print("Final updated unlabeled dataset saved!")

if __name__ == "__main__":
    main()
