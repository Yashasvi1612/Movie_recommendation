import streamlit as st
import pickle
import requests
import os


API_KEY = os.getenv("TMDB_API_KEY")
def download_file(file_id, filename):
    if os.path.exists(filename):
        return

    print(f"Downloading {filename}...")

    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = None

    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    with open(filename, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

# Download models from Google Drive
download_file("1NRaO1cm_SFCeJWfKc9liD5cGo-bEaW2v", "movies.pkl")
download_file("1wxtpMZ0Ywk3Mnciya8CHQWZnQSfnIeYU", "similarity.pkl")




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




