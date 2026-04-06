import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

texts = [
    "This study proposes a method to improve accuracy and presents results with conclusion",
    "This paper discusses something unclear and lacks proper structure",
    "We present methodology, results and conclusion clearly"
]

labels = [1, 0, 1]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
