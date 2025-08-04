import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from catboost import CatBoostClassifier
from sentence_transformers import SentenceTransformer
from sklearn.metrics import confusion_matrix, classification_report

# Loads model and outputs classification report and confusion matrix
model = CatBoostClassifier()
model.load_model("model/catboost_model.cbm")

df = pd.read_csv("data/labelled.csv")
texts = df["cleaned_text"].tolist()
y_true = df["risk"].tolist()  

embedder = SentenceTransformer('all-MiniLM-L6-v2')
X_embed = embedder.encode(texts, batch_size=32, show_progress_bar=True)

probs = model.predict_proba(X_embed)[:, 1]

threshold = 0.19
y_pred = (probs >= threshold).astype(int)

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title(f'Confusion Matrix (threshold = {threshold})')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.tight_layout()
plt.show()

print("\nClassification Report:")
print(classification_report(y_true, y_pred, digits=3))