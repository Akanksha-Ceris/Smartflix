import streamlit as st
import pickle
import pandas as pd
import requests
import os

# ── Load Saved Files ──────────────────────────────────────

movies_list = pickle.load(open('movie_list.pkl', 'rb'))
similarity  = pickle.load(open('similarity.pkl', 'rb'))
# ── Netflix-style CSS ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');

/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a0a 100%);
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}

/* Title */
.netflix-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 72px;
    background: linear-gradient(90deg, #E50914, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: 4px;
    margin-bottom: 0px;
    text-shadow: none;
}

.netflix-subtitle {
    font-family: 'Roboto', sans-serif;
    color: #aaaaaa;
    text-align: center;
    font-size: 18px;
    margin-top: -10px;
    margin-bottom: 30px;
    font-weight: 300;
    letter-spacing: 2px;
}

/* Selectbox label */
.stSelectbox label {
    color: #ffffff !important;
    font-family: 'Roboto', sans-serif;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: #1f1f1f !important;
    border: 1px solid #E50914 !important;
    color: white !important;
    border-radius: 8px !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(90deg, #E50914, #b20710) !important;
    color: white !important;
    font-family: 'Roboto', sans-serif !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    padding: 12px 40px !important;
    border-radius: 8px !important;
    border: none !important;
    width: 100% !important;
    letter-spacing: 2px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #ff1a1a, #E50914) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 0 20px rgba(229, 9, 20, 0.5) !important;
}

/* Movie cards */
.movie-card {
    background: #1a1a1a;
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid #2a2a2a;
}

.movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 30px rgba(229, 9, 20, 0.3);
}

.movie-title {
    color: #ffffff;
    font-family: 'Roboto', sans-serif;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    padding: 10px 5px;
    background: #1a1a1a;
}

/* Section heading */
.section-heading {
    font-family: 'Bebas Neue', cursive;
    color: #E50914;
    font-size: 36px;
    letter-spacing: 3px;
    margin-top: 30px;
    margin-bottom: 20px;
    border-left: 4px solid #E50914;
    padding-left: 15px;
}

/* Divider */
.red-divider {
    height: 2px;
    background: linear-gradient(90deg, #E50914, transparent);
    margin: 20px 0;
    border: none;
}

/* Image styling */
.stImage img {
    border-radius: 10px 10px 0 0 !important;
}

/* Caption styling */
.stImage + div {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── Fetch Movie Poster ────────────────────────────────────

def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances   = similarity[movie_index]

    # Get top 50 candidates for maximum backup
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

            if poster is not None:
                recommended_movies.append(title)
                recommended_posters.append(poster)
        except:
            continue  # skip any broken entry

    return recommended_movies, recommended_posters
# ── UI Layout ─────────────────────────────────────────────

# Hero Section
st.markdown('<div class="netflix-title">SMARTFLIX</div>', unsafe_allow_html=True)
st.markdown('<div class="netflix-subtitle">✦ AI-POWERED MOVIE RECOMMENDATIONS ✦</div>', unsafe_allow_html=True)
st.markdown('<hr class="red-divider">', unsafe_allow_html=True)

# Search Section
col_left, col_mid, col_right = st.columns([1, 3, 1])
with col_mid:
    selected_movie_name = st.selectbox(
        '🎬  CHOOSE A MOVIE',
        movies_list['title'].values
    )
    recommend_btn = st.button('▶  GET RECOMMENDATIONS')

# Results Section
if recommend_btn:
    with st.spinner('🎬 Finding perfect movies for you...'):
        names, posters = recommend(selected_movie_name)

    st.markdown('<div class="section-heading">🍿 RECOMMENDED FOR YOU</div>', unsafe_allow_html=True)

    # Only show movies we actually have
    if not names:
    st.error("⚠️ No recommendations found. Check your API key.")
    else:
        cols = st.columns(len(names))
        for idx, col in enumerate(cols):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                st.image(posters[idx], use_column_width=True)
                st.markdown(f'<div class="movie-title">{names[idx]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<hr class="red-divider">', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#555; font-family:Roboto; font-size:13px; padding:10px;">
    Built with ❤️ using Python • Streamlit • TMDB API • Machine Learning
</div>
""", unsafe_allow_html=True)
