import streamlit as st
import pickle
import pandas as pd
import requests

# ── Load Saved Files ──────────────────────────────────────
movies_list = pickle.load(open('movie_list.pkl', 'rb'))
similarity  = pickle.load(open('similarity.pkl', 'rb'))

# ── Fetch Movie Poster ────────────────────────────────────
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3b0c3004be07389bf1e92d4b247dd0af&language=en-US"
        data = requests.get(url, timeout=5).json()
        poster_path = data.get('poster_path')  # ← use .get() instead of direct key
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"
    except:
        return "https://via.placeholder.com/500x750?text=No+Poster"

# ── Recommend Function ────────────────────────────────────
def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances   = similarity[movie_index]

    movies_list_sorted = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:20]

    recommended_movies  = []
    recommended_posters = []

    for i in movies_list_sorted:
        # Stop once we have 5 good recommendations
        if len(recommended_movies) == 5:
            break

        movie_id = movies_list.iloc[i[0]].movie_id
        poster   = fetch_poster(movie_id)

        # ← Only add if poster is a real TMDB image, skip placeholders
        if "placeholder" not in poster:
            recommended_movies.append(movies_list.iloc[i[0]].title)
            recommended_posters.append(poster)

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
    names, posters = recommend(selected_movie_name)

    st.markdown("### 🍿 Recommended Movies")
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx])
            st.caption(names[idx])