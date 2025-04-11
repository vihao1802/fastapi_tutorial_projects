import tensorflow_hub as hub
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Tải mô hình Universal Sentence Encoder từ TensorFlow Hub
model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# Đọc dữ liệu phim
df = pd.read_csv("movies.csv")

# Chuyển mô tả phim thành vector
movie_embeddings = model(df["description"].tolist())


def recommend_movies(movie_description, top_k=3):
    """
    Gợi ý phim dựa trên mô tả nội dung.
    - movie_description: Nội dung phim người dùng muốn tìm.
    - top_k: Số lượng phim gợi ý (mặc định = 3).
    """
    user_embedding = model([movie_description])  # Mã hóa câu nhập vào
    similarities = cosine_similarity(
        user_embedding, movie_embeddings
    )  # Tính độ tương đồng

    # Sắp xếp theo độ tương đồng
    sorted_indices = np.argsort(similarities[0])[::-1]

    # Lấy top K phim gợi ý
    recommendations = df.iloc[sorted_indices[:top_k]][
        ["id", "title", "description"]
    ].to_dict(orient="records")
    return recommendations
