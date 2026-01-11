import streamlit as st
import pickle
import requests
import os
from dotenv import load_dotenv


def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)

# Download models from Google Drive
download_file(
    "https://drive.google.com/uc?export=download&id=1NRaO1cm_SFCeJWfKc9liD5cGo-bEaW2v",
    "movies.pkl"
)

download_file(
    "https://drive.google.com/uc?export=download&id=1wxtpMZ0Ywk3Mnciya8CHQWZnQSfnIeYU",
    "similarity.pkl"
)

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))



st.title('Movie Recommender System')



# Movie list for dropdown
movies_list = movies['title'].values


def fetch_poster(movie_id):


    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        if response.status_code != 200:
            return None

        poster_path = data.get("poster_path")

        if poster_path and poster_path != "null":
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"

    except:
        return "https://via.placeholder.com/300x450?text=Error"




def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]

    movie_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)

    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_list[1:]:
        row = movies.iloc[i[0]]
        poster = fetch_poster(row['id'])

        recommended_movies.append(row['title'])
        recommended_movies_posters.append(poster)

        if len(recommended_movies) == 5:
            break

    return recommended_movies, recommended_movies_posters




# UI
selected_movie_name = st.selectbox(
    'Select a movie:',
    movies_list
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(len(names))

    for i in range(len(names)):
        with cols[i]:
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{posters[i]}" width="100%">
                    <div class="movie-title">{names[i]}</div>
                </div>
            """, unsafe_allow_html=True)




