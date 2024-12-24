from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load dữ liệu
df_movies = pd.read_csv("movies.csv", usecols=["movieId", "title", "genres"], dtype={"movieId": "int32", "title": "str"})
df_ratings = pd.read_csv("ratings.csv", usecols=["userId", "movieId", "rating"], dtype={"userId": "int32", "movieId": "int32", "rating": "float32"})

# Chuẩn bị ma trận ratings (hàng: userId, cột: movieId)
users_movies = df_ratings.pivot(index="userId", columns="movieId", values="rating").fillna(0)
users_movies_matrix = users_movies.to_numpy()

# Hàm tính khoảng cách Euclidean
def calc_distance(item, point):
    return np.sqrt(np.sum((np.array(item) - np.array(point)) ** 2))

# Hàm KNN: Tìm k người dùng gần nhất
def k_nearest_neighbors(train_set, point, k):
    distances = []
    for index, item in enumerate(train_set):
        distances.append({"index": index, "value": calc_distance(item, point)})
    distances.sort(key=lambda x: x["value"])
    return distances[:k]

#Tính rating xuất hiện nhiều nhất
def calculate_mode(ratings):
    unique, counts = np.unique(ratings, return_counts=True)
    return unique[np.argmax(counts)]  # Lấy giá trị có tần suất xuất hiện cao nhất

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    user_id = data.get("user_id")  # Lấy user_id từ request

    # Kiểm tra nếu user_id không tồn tại
    if user_id is None or not user_id.isdigit():
        return jsonify({"recommendations": []})

    user_id = int(user_id)

    # Kiểm tra xem user_id có tồn tại trong dữ liệu không
    if user_id not in users_movies.columns:
        return jsonify({"recommendations": []})

    # Lấy vector đánh giá của người dùng
    user_ratings = users_movies.loc[user_id].to_numpy()

    print(users_movies)

    # Tìm k người dùng gần nhất
    nearest_neighbors = k_nearest_neighbors(users_movies_matrix, user_ratings, k=3)

    print(nearest_neighbors)

    #Lấy danh sách các phim chưa xem và đánh giá 
    recommendations = {}
    for neighbor in nearest_neighbors:
        neighbor_id = neighbor["index"]
        neighbor_ratings = users_movies.iloc[neighbor_id, :]  # Lấy toàn bộ đánh giá cho tất cả các bộ phim của người dùng gần nhất
        for movie_id, rating in neighbor_ratings.items():
            if movie_id in users_movies.columns:
                if rating > 0 and users_movies.loc[user_id, movie_id] == 0:
                    recommendations.setdefault(movie_id, []).append(rating)
            else:
                print(movie_id)
                print(f"Movie ID {movie_id} không tồn tại trong DataFrame.")


    final_recommendations = [
        {
            "id": movie_id,
            "title": df_movies[df_movies["movieId"] == movie_id]["title"].values[0],
            "genres": df_movies[df_movies["movieId"] == movie_id]["genres"].values[0],
            "predicted_rating": calculate_mode(ratings),
        }
        for movie_id, ratings in recommendations.items()
    ]
    final_recommendations_sorted = sorted(final_recommendations, key=lambda x: x["predicted_rating"], reverse=True)[:10]
    return jsonify({"recommendations": final_recommendations_sorted})


if __name__ == "__main__":
    app.run(debug=True)

#Hướng dẫn chạy
# python -m venv venv
# venv\Scripts\activate
# pip install flask pandas numpy
# python app.py