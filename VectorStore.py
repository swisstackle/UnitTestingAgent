from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

class VectorStore:
    def __init__(self, vectorizer, tfidf_matrix, documents: list[str], thePassedDict=None):
        try:
            self.vectorizer = vectorizer
            self.tfidf_matrix = tfidf_matrix 
            self.documents = documents
            self.thedict = thePassedDict
        except Exception as e:
            print(f"Error initializing VectorStore: {str(e)}")
            raise

    @classmethod
    def from_documents(cls, documents):
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(documents)
            return cls(vectorizer, tfidf_matrix, documents)
        except Exception as e:
            print(f"Error creating VectorStore from documents: {str(e)}")
            raise

    @classmethod
    def from_dict_inmemory(cls, data_dict):
        try:
            documents = list(data_dict.keys())
            vectorizer = TfidfVectorizer()
            if documents:
                tfidf_matrix = vectorizer.fit_transform(documents)
            else:
                tfidf_matrix = np.array([])
            return cls(vectorizer, tfidf_matrix, documents, data_dict)
        except Exception as e:
            print(f"Error creating VectorStore from dictionary: {str(e)}")
            raise

    @classmethod
    def from_dict_json(cls, jsonstring: str):
        try:
            data_dict = json.loads(jsonstring)
            return cls.from_dict_inmemory(data_dict)
        except Exception as e:
            print(f"Error creating VectorStore from JSON string: {str(e)}")
            raise

    @classmethod
    def from_dict_json_file(cls, filepath: str):
        try:
            with open(filepath, "r") as f:
                data_dict = json.load(f)
            return cls.from_dict_inmemory(data_dict)
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return cls.from_dict_inmemory({})

    def search_strings(self, query: str, k: int = 2) -> list[dict]:
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            return [
                {"document": self.documents[i], "relevan": float(similarities[i])}
                for i in top_k_indices
            ]
        except Exception as e:
            print(f"Error searching strings: {str(e)}")
            return []

    def search_dict(self, query: str, k: int = 2) -> list[dict]:
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            return [
                {"document": self.documents[i], "Value": self.thedict[self.documents[i]], "relevan": float(similarities[i])}
                for i in top_k_indices
            ]
        except Exception as e:
            print(f"Error searching dictionary: {str(e)}")
            return []

    def add_memory_string_inmemory(self, string: str):
        try:
            self.documents.append(string)
        except Exception as e:
            print(f"Error adding string to memory: {str(e)}")

    def add_memory_dict_inmemory(self, key: str, value):
        try:
            self.thedict[key] = value
        except Exception as e:
            print(f"Error adding to dictionary: {str(e)}")

    def save_dict_to_json(self, filepath):
        try:
            with open(filepath, "w") as f:
                json.dump(self.thedict, f)
        except Exception as e:
            print(f"Error saving dictionary to JSON: {str(e)}")

    def save_strings_to_json(self, filepath):
        try:
            with open(filepath, "w") as f:
                json.dump(self.documents, f)
        except Exception as e:
            print(f"Error saving strings to JSON: {str(e)}")

    def delete_by_dict_key(self, key):
        try:
            del self.thedict[key]
        except Exception as e:
            print(f"Error deleting key from dictionary: {str(e)}")

    def delete_by_value(self, value):
        try:
            if not self.thedict:
                raise ValueError("No dictionary available to delete from")
            keys_to_delete = [k for k, v in self.thedict.items() if v == value]
            for key in keys_to_delete:
                del self.thedict[key]
            if value in self.documents:
                self.documents.remove(value)
        except Exception as e:
            print(f"Error deleting by value: {str(e)}")

if __name__ == "__main__":
    vector_store = VectorStore.from_dict_json_file("memories.json")
    print(vector_store.search_strings("Build and Tests Executed Successfully"))
