import streamlit as st
import pickle
import pandas as pd
import requests
import os

# ── Load Saved Files ──────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_list = pickle.load(open(os.path.join(BASE_DIR, 'movie_list.pkl'), 'rb'))
similarity  = pickle.load(open(os.path.join(BASE_DIR, 'similarity.pkl'), 'rb'))

# ── Fetch Movie Poster ────────────────────────────────────
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3b0c3004be07389bf1e92d4b247dd0af&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return None  # ← return None if no poster
    except:
        return None  # ← return None on any error

# ── Recommend Function ────────────────────────────────────
def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances   = similarity[movie_index]

    # Get top 30 candidates so we have plenty of backups
    movies_list_sorted = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:30]

    recommended_movies  = []
    recommended_posters = []

    for i in movies_list_sorted:
        if len(recommended_movies) == 5:
            break

        movie_id = movies_list.iloc[i[0]].movie_id
        poster   = fetch_poster(movie_id)
        title    = movies_list.iloc[i[0]].title

        if poster is not None:  # ← only add if poster exists
            recommended_movies.append(title)
            recommended_posters.append(poster)

    # ── Final safety net ──────────────────────────────────
    # If still less than 5, fill with placeholder
    while len(recommended_movies) < 5:
        recommended_movies.append("N/A")
        recommended_posters.append("https://via.placeholder.com/500x750?text=No+Poster")

    return recommended_movies, recommended_posters

# ── Streamlit UI ──────────────────────────────────────────
st.set_page_config(page_title="Smartflix", page_icon="🎬")

st.title('🎬 Smartflix')
st.markdown("##### Find movies similar to your favourites!")

selected_movie_name = st.selectbox(
    'Type or select a movie:',
    movies_list['title'].values
)

if st.button('🎯 Recommend'):
    with st.spinner('Finding movies for you...'):
        names, posters = recommend(selected_movie_name)

    st.markdown("### 🍿 Recommended Movies")
    cols = st.columns(5)

    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx])
            st.caption(names[idx])