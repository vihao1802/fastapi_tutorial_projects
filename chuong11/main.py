from fastapi import FastAPI
from recommendation import recommend_movies

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Movie Recommendation API is running!"}


@app.get("/recommend/")
def get_recommendations(movie_description: str, top_k: int = 3):
    """
    API gợi ý phim
    - movie_description: Mô tả phim mà người dùng thích.
    - top_k: Số lượng phim gợi ý.
    """
    recommendations = recommend_movies(movie_description, top_k)
    return {"recommendations": recommendations}
