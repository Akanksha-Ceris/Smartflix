import streamlit as st
import pickle
import pandas as pd
import requests

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="SMARTFLIX",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Load Saved Files ──────────────────────────────────────
movies_list = pickle.load(open('movie_list.pkl', 'rb'))
similarity  = pickle.load(open('similarity.pkl', 'rb'))

# ── Netflix-Style CSS ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Nunito:wght@400;600;700;800&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    background-color: #141414 !important;
    color: #ffffff !important;
    font-family: 'Nunito', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Navbar ── */
.nf-navbar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: linear-gradient(to bottom, rgba(0,0,0,0.95) 70%, transparent);
    padding: 14px 48px;
    display: flex;
    align-items: center;
    gap: 36px;
}
.nf-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px;
    color: #e50914;
    letter-spacing: 3px;
    margin-right: 8px;
}
.nf-nav-link {
    font-size: 13px;
    color: #b3b3b3;
    cursor: pointer;
    font-weight: 600;
}
.nf-nav-link-active {
    font-size: 13px;
    color: #ffffff;
    font-weight: 800;
}

/* ── Hero ── */
.nf-hero {
    position: relative;
    width: 100%;
    height: 380px;
    background: linear-gradient(105deg, #0a0a0a 0%, #1a0505 40%, #0a0010 100%);
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    padding: 0 48px 40px;
    margin-bottom: 8px;
}
.nf-hero-bg-text {
    position: absolute;
    right: -20px;
    top: 50%;
    transform: translateY(-50%);
    font-family: 'Bebas Neue', sans-serif;
    font-size: 200px;
    color: rgba(229,9,20,0.06);
    letter-spacing: 12px;
    pointer-events: none;
    white-space: nowrap;
}
.nf-hero-content { position: relative; z-index: 2; max-width: 500px; }
.nf-hero-badge {
    display: inline-block;
    background: #e50914;
    color: #fff;
    font-size: 10px;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 3px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.nf-hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 58px;
    line-height: 1;
    letter-spacing: 3px;
    margin: 0 0 10px;
    text-shadow: 2px 4px 16px rgba(0,0,0,0.9);
}
.nf-hero-desc {
    font-size: 13px;
    color: #ccc;
    line-height: 1.65;
    margin-bottom: 4px;
}

/* ── Section Title ── */
.nf-section-title {
    font-size: 20px;
    font-weight: 800;
    color: #e5e5e5;
    padding: 16px 48px 10px;
    letter-spacing: 0.3px;
}
.nf-section-title span {
    color: #e50914;
}

/* ── Movie Card Grid ── */
.nf-cards-grid {
    display: flex;
    gap: 12px;
    padding: 4px 48px 28px;
    overflow-x: auto;
    scrollbar-width: none;
}
.nf-cards-grid::-webkit-scrollbar { display: none; }

.nf-card {
    flex: 0 0 auto;
    width: 155px;
    border-radius: 6px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.28s cubic-bezier(.25,.8,.25,1), box-shadow 0.28s;
    position: relative;
    background: #1f1f1f;
}
.nf-card:hover {
    transform: scale(1.10) translateY(-6px);
    box-shadow: 0 20px 48px rgba(0,0,0,0.9), 0 0 0 2px rgba(229,9,20,0.5);
    z-index: 10;
}
.nf-card img {
    width: 155px;
    height: 225px;
    object-fit: cover;
    display: block;
    border-radius: 6px 6px 0 0;
}
.nf-card-info {
    padding: 8px 10px 10px;
    background: #1f1f1f;
    border-radius: 0 0 6px 6px;
}
.nf-card-title {
    font-size: 12px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.35;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.nf-card-match {
    font-size: 11px;
    color: #46d369;
    font-weight: 700;
    margin-top: 3px;
}
.nf-card-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 50%);
    border-radius: 6px;
    opacity: 0;
    transition: opacity 0.25s;
}
.nf-card:hover .nf-card-overlay { opacity: 1; }

/* ── Selector Area ── */
.nf-selector-wrap {
    background: rgba(20,20,20,0.95);
    border-top: 1px solid #2a2a2a;
    padding: 28px 48px 32px;
    margin-top: 8px;
}
.nf-selector-label {
    font-size: 14px;
    font-weight: 700;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

/* ── Selectbox override ── */
div[data-baseweb="select"] > div {
    background-color: #2a2a2a !important;
    border: 1px solid #444 !important;
    border-radius: 6px !important;
    color: #fff !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 15px !important;
}
div[data-baseweb="select"] svg { fill: #aaa !important; }
div[data-baseweb="popover"] { background: #2a2a2a !important; }
li[role="option"] {
    background: #2a2a2a !important;
    color: #fff !important;
    font-family: 'Nunito', sans-serif !important;
}
li[role="option"]:hover { background: #3a3a3a !important; }

/* ── Button override ── */
div.stButton > button {
    background: #e50914 !important;
    color: #fff !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 10px 32px !important;
    letter-spacing: 0.5px !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
    margin-top: 12px !important;
}
div.stButton > button:hover {
    background: #f40612 !important;
    box-shadow: 0 4px 20px rgba(229,9,20,0.5) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #e50914 !important; }

/* ── Empty / Error state ── */
.nf-empty {
    padding: 32px 48px;
    color: #666;
    font-size: 14px;
    font-style: italic;
}

/* ── Divider ── */
.nf-divider {
    border: none;
    border-top: 1px solid #2a2a2a;
    margin: 0 48px;
}

/* ── Footer ── */
.nf-footer {
    padding: 24px 48px;
    font-size: 12px;
    color: #555;
    text-align: center;
    border-top: 1px solid #222;
    margin-top: 16px;
}
.nf-footer span { color: #e50914; }
</style>
""", unsafe_allow_html=True)

# ── Fetch Movie Poster ────────────────────────────────────
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3b0c3004be07389bf1e92d4b247dd0af&language=en-US"
    try:
        data = requests.get(url, timeout=5).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except:
        pass
    return None

# ── Recommend ────────────────────────────────────────────
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
    recommended_scores  = []

    for i in movies_list_sorted:
        if len(recommended_movies) == 5:
            break
        try:
            movie_id = movies_list.iloc[i[0]].movie_id
            title    = movies_list.iloc[i[0]].title
            poster   = fetch_poster(movie_id)
            if poster:
                try:
                    score = min(int(60 + float(i[1]) * 39), 99)
                except:
                    score = 85
                recommended_movies.append(title)
                recommended_posters.append(poster)
                recommended_scores.append(score)
        except:
            continue

    min_len = min(len(recommended_movies), len(recommended_posters), len(recommended_scores))
    return recommended_movies[:min_len], recommended_posters[:min_len], recommended_scores[:min_len]


# ══════════════════════════════════════════════════════════
#  RENDER UI
# ══════════════════════════════════════════════════════════

# ── Navbar ───────────────────────────────────────────────
st.markdown("""
<div class="nf-navbar">
  <div class="nf-logo">SMARTFLIX</div>
  <span class="nf-nav-link-active">Home</span>
  <span class="nf-nav-link">Movies</span>
  <span class="nf-nav-link">TV Shows</span>
  <span class="nf-nav-link">My List</span>
</div>
""", unsafe_allow_html=True)

# ── Hero Banner ──────────────────────────────────────────
st.markdown("""
<div class="nf-hero">
  <div class="nf-hero-bg-text">SMARTFLIX</div>
  <div class="nf-hero-content">
    <div class="nf-hero-badge">✦ AI Powered</div>
    <div class="nf-hero-title">DISCOVER<br>YOUR NEXT<br>OBSESSION</div>
    <div class="nf-hero-desc">
      Pick any movie below and our AI engine finds<br>
      5 perfect matches — just for you.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Movie Selector ───────────────────────────────────────
st.markdown("""
<div class="nf-selector-wrap">
  <div class="nf-selector-label">🎬 Choose a Movie</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    selected_movie_name = st.selectbox(
        label="",
        options=movies_list['title'].values,
        label_visibility="collapsed"
    )
with col2:
    recommend_btn = st.button("▶ Get Recommendations")

# ── Results ──────────────────────────────────────────────
if recommend_btn:
    with st.spinner('Finding perfect movies for you...'):
        names, posters, scores = recommend(selected_movie_name)

    if not names:
        st.markdown('<div class="nf-empty">⚠️ No recommendations found. Please check your API key or try another movie.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<hr class="nf-divider">', unsafe_allow_html=True)
        st.markdown(f'<div class="nf-section-title">Because you watched <span>{selected_movie_name}</span></div>', unsafe_allow_html=True)

        # Build card HTML
        cards_html = '<div class="nf-cards-grid">'
        for i in range(len(names)):
            cards_html += f"""
            <div class="nf-card">
                <img src="{posters[i]}" alt="{names[i]}" />
                <div class="nf-card-overlay"></div>
                <div class="nf-card-info">
                    <div class="nf-card-title">{names[i]}</div>
                    <div class="nf-card-match">{scores[i]}% Match</div>
                </div>
            </div>"""
        cards_html += '</div>'

        st.markdown(cards_html, unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────
st.markdown("""
<div class="nf-footer">
  Made with <span>♥</span> · SMARTFLIX · AI-Powered Movie Recommendations
</div>
""", unsafe_allow_html=True)
