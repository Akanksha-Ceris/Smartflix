import streamlit as st
import pickle
import pandas as pd
import requests
import os

# ── Load Saved Files ──────────────────────────────────────
movies_list = pickle.load(open('movie_list.pkl', 'rb'))
similarity  = pickle.load(open('similarity.pkl', 'rb'))

# ── Fetch Movie Poster ────────────────────────────────────
def fetch_poster(movie_id):
    api_key = "YOUR_TMDB_API_KEY"   # 🔴 Put your API key here
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3b0c3004be07389bf1e92d4b247dd0af&language=en-US"

    try:
        data = requests.get(url)
        data = data.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return None
    except:
        return None


def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances   = similarity[movie_index]

    movies_list_sorted = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:50]

    recommended_movies  = []
    recommended_posters = []

    for i in movies_list_sorted:
        if len(recommended_movies) == 5:
            break

        try:
            movie_id = movies_list.iloc[i[0]].movie_id
            title    = movies_list.iloc[i[0]].title
            poster   = fetch_poster(movie_id)

            if poster:
                recommended_movies.append(title)
                recommended_posters.append(poster)
        except:
            continue

    return recommended_movies, recommended_posters


# ── UI Layout ─────────────────────────────────────────────

st.title("SMARTFLIX 🎬")
st.write("AI-powered movie recommendations")

selected_movie_name = st.selectbox(
    'Choose a movie',
    movies_list['title'].values
)

recommend_btn = st.button('Get Recommendations')

# ✅ FIXED BLOCK
if recommend_btn:
    with st.spinner('Finding perfect movies for you...'):
        names, posters = recommend(selected_movie_name)

    st.subheader("Recommended for you")

    if not names:
        st.error("No recommendations found. Check your API key.")
    else:
        cols = st.columns(len(names))

        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx])
                st.caption(names[idx])