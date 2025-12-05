import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import re
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Letterboxd Quick Wrapped",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Dark Theme Adjustment */
    [data-testid="stAppViewContainer"] {
        background-color: #14181c;
        color: #9ab;
    }
    [data-testid="stSidebar"] {
        background-color: #1f252d; 
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: #2c3440;
        border: 1px solid #456;
        padding: 15px;
        border-radius: 8px;
        color: #fff;
    }
    label[data-testid="stMetricLabel"] {
        color: #00e054 !important; /* Letterboxd Green */
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* Personality Card */
    .personality-card {
        background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
        border: 2px solid #00e054;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 224, 84, 0.2);
    }
    .personality-entry {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .personality-entry:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .personality-title {
        font-size: 2.2em;
        font-weight: bold;
        color: #00e054;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    .personality-desc {
        font-size: 1.1em;
        color: #fff;
        font-style: italic;
    }

    /* Poster Grid */
    .poster-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        padding: 20px 0;
    }
    .poster-img {
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        transition: transform 0.2s;
        width: 100px; 
    }
    @media only screen and (max-width: 600px) {
      .poster-img {
        width: 70px;
      }
    }
    .poster-img:hover {
        transform: scale(1.05);
        z-index: 10;
    }
    
    /* Fun Stat Box */
    .fun-stat-box {
        background-color: #2c3440;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #456;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Roast Bubble */
    .roast-box {
        background: linear-gradient(45deg, #1f252d, #2c0000);
        border-left: 5px solid #ff4040;
        padding: 20px;
        margin: 20px 0;
        border-radius: 8px;
        font-size: 1.3em;
        font-style: italic;
        color: #ffcccc;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* Cine-MBTI */
    .mbti-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    .mbti-letter {
        font-size: 3em;
        font-weight: bold;
        color: #00e054;
        text-shadow: 0 0 10px rgba(0, 224, 84, 0.3);
    }
    .mbti-desc {
        color: #9ab;
        font-size: 0.9em;
    }
    
    /* Soundtrack List */
    .song-row {
        display: flex; 
        align-items: center; 
        padding: 10px; 
        background: #1f252d; 
        margin-bottom: 8px; 
        border-radius: 8px;
        border-left: 4px solid #40bcf4;
    }
    .song-icon { font-size: 1.5em; margin-right: 15px; }
    .song-info { display: flex; flex-direction: column; }
    .song-title { font-weight: bold; color: #fff; }
    .song-artist { font-size: 0.9em; color: #9ab; }
    
    /* Buttons */
    .stButton>button {
        background-color: #00e054;
        color: #14181c;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #40bcf4; /* Letterboxd Blue */
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def fetch_rss_data(username):
    url = f"https://letterboxd.com/{username}/rss/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, f"Could not find user '{username}' (Status: {response.status_code})"
            
        soup = BeautifulSoup(response.content, "html.parser")
        items = soup.find_all('item')
        
        data = []
        for item in items:
            watched_date_tag = item.find('letterboxd:watcheddate')
            if not watched_date_tag:
                continue 
            watched_date = pd.to_datetime(watched_date_tag.text)
            
            title_tag = item.find('letterboxd:filmtitle')
            title = title_tag.text if title_tag else "Unknown"
            
            year_tag = item.find('letterboxd:filmyear')
            year = int(year_tag.text) if year_tag and year_tag.text.isdigit() else 0
            
            rating_tag = item.find('letterboxd:memberrating')
            rating = float(rating_tag.text) if rating_tag else 0.0
            
            rewatch_tag = item.find('letterboxd:rewatch')
            rewatch = 'Yes' if (rewatch_tag and rewatch_tag.text == 'Yes') else 'No'
            
            description = item.find('description')
            poster_url = None
            review_length = 0
            
            if description:
                desc_soup = BeautifulSoup(description.text, "html.parser")
                img = desc_soup.find('img')
                if img and 'src' in img.attrs:
                    poster_url = img['src']
                
                for p in desc_soup.find_all('p'):
                    if p.find('img'):
                        p.decompose()
                
                text_content = desc_soup.get_text(strip=True)
                review_length = len(text_content.split())
            
            data.append({
                'Date': watched_date,
                'Name': title,
                'Year': year,
                'Rating': rating,
                'Rewatch': rewatch,
                'Poster': poster_url,
                'Review_Words': review_length,
                'Has_Review': True if review_length > 5 else False
            })
            
        if not data:
            return None, "No diary entries found in RSS feed."
            
        df = pd.DataFrame(data)
        df['Month'] = df['Date'].dt.month_name()
        df['Day'] = df['Date'].dt.day_name()
        df['Decade'] = (df['Year'] // 10) * 10
        
        return df, None

    except Exception as e:
        return None, f"Error fetching RSS: {str(e)}"

def calculate_stats(df):
    if df.empty:
        return 0, 0, "N/A"
    dates = sorted(df['Date'].dt.date.unique())
    if not dates:
        streak = 0
    else:
        longest_streak = 1
        current_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1
        streak = max(longest_streak, current_streak)
        
    daily_counts = df.groupby(df['Date'].dt.date).size()
    max_binge = daily_counts.max()
    binge_date = daily_counts.idxmax().strftime('%b %d')
    return streak, max_binge, binge_date

def get_multi_personalities(total, avg_rating, rewatch_pct, diversity_score, review_pct):
    personas = []
    
    # 1. Base Engagement
    if total < 5:
        personas.append(("The Casual Viewer", "Just dipping your toes in the cinematic waters."))
        return personas # Return mainly this if data is too low
        
    # 2. Rating Habits
    if avg_rating > 4.0:
        personas.append(("The Generous Spirit", "5 stars for everyone! You love movies and they love you."))
    elif avg_rating < 2.8:
        personas.append(("The Harsh Critic", "Hard to please? Or maybe you just have impeccable taste."))
        
    # 3. Rewatch Habits
    if rewatch_pct > 30:
        personas.append(("The Comfort Seeker", "Why risk a bad movie when you can watch a masterpiece again?"))
    elif rewatch_pct < 5:
        personas.append(("The Explorer", "Always seeking something new. No looking back."))
        
    # 4. Era / Diversity
    if diversity_score > 6:
        personas.append(("The Time Traveler", "From the classics to the modern era, you see it all."))
        
    # 5. Review Habits
    if review_pct > 50:
        personas.append(("The Scribe", "You don't just watch; you document. Pen mighty!"))
        
    # Fallback
    if not personas:
        personas.append(("The Balanced Cinephile", "A perfectly balanced diet of cinema."))
        
    return personas

def generate_roast(df):
    comments = []
    avg = df['Rating'].mean()
    rewatch_count = df[df['Rewatch'] == 'Yes'].shape[0]
    old_movies = df[df['Year'] < 1980].shape[0]
    
    # Rating specific
    if avg > 4.5:
        comments.append("You know 2.5 stars exists, right? Not everything is a masterpiece.")
        comments.append("You're the person who claps when the plane lands, aren't you?")
    elif avg < 2.5:
        comments.append("Who hurt you? Seriously, do you even like movies?")
        comments.append("I bet you're fun at parties. 'Actually, the book was better.'")
        comments.append("You woke up and chose violence with these ratings.")
    elif avg > 3.8:
        comments.append("A little generous with the stars, are we?")
        
    # Rewatch specific
    if rewatch_count > 15:
        comments.append("Comfort movies are a cry for help. We hear you.")
        comments.append("Trying to relive the past won't fix the present.")
        comments.append("We get it, you really like that one movie.")
    elif rewatch_count == 0:
        comments.append("Commitment issues? You never call a movie back.")
        
    # Era specific
    if old_movies > 15:
        comments.append("We get it, you own a turntable and hate CGI.")
        comments.append("Born in the wrong generation? Or just pretentious?")
    elif df[df['Year'] > 2020].shape[0] > 20:
        comments.append("Recency bias is a hell of a drug.")
        
    # Day specific
    if df[df['Day'] == 'Monday'].shape[0] > 5:
        comments.append("Watching movies on Monday? Avoiding responsibilities like a pro.")
        
    # Generic
    if not comments:
        comments.append("Your taste is so painfully average, I can't even roast it.")
        comments.append("You exist. You watch movies. That's about it.")
        comments.append("Honestly? A pretty respectable list. Boring, but respectable.")
        
    return random.choice(comments)

def calculate_cine_mbti(df):
    # E (Explorer) vs I (Comfort)
    rewatch_rate = (df[df['Rewatch'] == 'Yes'].shape[0] / len(df)) * 100
    p1 = "I" if rewatch_rate > 20 else "E"
    
    # S (Modern) vs N (Vintage)
    avg_year = df['Year'].mean()
    p2 = "S" if avg_year > 2010 else "N"
    
    # T (Critical) vs F (Fan)
    avg_rating = df['Rating'].mean()
    p3 = "T" if avg_rating < 3.2 else "F"
    
    # J (Routine) vs P (Binge)
    daily_variance = df.groupby(df['Date'].dt.date).size().var()
    p4 = "P" if daily_variance > 1.5 else "J"
    
    code = f"{p1}{p2}{p3}{p4}"
    meaning = {
        "E": "Explorer (New Films)", "I": "Comfort (Rewatches)",
        "S": "Modernist (Recent)", "N": "Historian (Classics)",
        "T": "Critic (Analytic)", "F": "Fan (Emotional)",
        "J": "Routine (Steady)", "P": "Binger (Spontaneous)"
    }
    return code, meaning

def get_soundtrack_suggestions(mbti_code, df):
    pools = {
        "N": [("Heroes", "David Bowie"), ("Dreams", "Fleetwood Mac"), ("Space Oddity", "David Bowie"), ("There Is a Light", "The Smiths")],
        "S": [("Blinding Lights", "The Weeknd"), ("Midnight City", "M83"), ("As It Was", "Harry Styles"), ("Espresso", "Sabrina Carpenter")],
        "T": [("Paranoid Android", "Radiohead"), ("Psycho Killer", "Talking Heads"), ("Where Is My Mind?", "Pixies"), ("Tame Impala", "New Person")],
        "F": [("Dancing Queen", "ABBA"), ("Mr. Brightside", "The Killers"), ("Dog Days Are Over", "Florence + The Machine"), ("Cruel Summer", "Taylor Swift")],
        "I": [("Fast Car", "Tracy Chapman"), ("Landslide", "Fleetwood Mac"), ("Vienna", "Billy Joel"), ("Mystery of Love", "Sufjan Stevens")],
        "E": [("Time to Pretend", "MGMT"), ("Paper Planes", "M.I.A."), ("Maps", "Yeah Yeah Yeahs"), ("Electric Feel", "MGMT")]
    }
    suggestions = []
    # Dominant Traits logic
    if "E" in mbti_code: suggestions.extend(random.sample(pools["E"], 1))
    else: suggestions.extend(random.sample(pools["I"], 1))
    if "N" in mbti_code: suggestions.extend(random.sample(pools["N"], 1))
    else: suggestions.extend(random.sample(pools["S"], 1))
    if "T" in mbti_code: suggestions.extend(random.sample(pools["T"], 1))
    else: suggestions.extend(random.sample(pools["F"], 1))
    
    # Specific Movie Vibe
    if not df.empty:
        top_movie = df.sort_values(by=['Rating', 'Date'], ascending=[False, True]).iloc[0]
        year = top_movie['Year']
        if year < 1980: suggestions.append(("California Dreamin'", "The Mamas & The Papas"))
        elif year < 1990: suggestions.append(("Everybody Wants to Rule the World", "Tears for Fears"))
        elif year < 2000: suggestions.append(("Smells Like Teen Spirit", "Nirvana"))
        elif year < 2010: suggestions.append(("Mr. Brightside", "The Killers"))
        else: suggestions.append(("bad guy", "Billie Eilish"))
            
    avg_rating = df['Rating'].mean()
    if avg_rating < 2.5: suggestions.append(("Creep", "Radiohead"))
    elif avg_rating > 4.5: suggestions.append(("Walking on Sunshine", "Katrina and the Waves"))
        
    return list(set(suggestions))[:5]

# --- MAIN APP ---

def main():
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'username' not in st.session_state:
        st.session_state.username = ""

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚡ Quick Wrapped")
        st.caption("Last 50 Films")
        username_input = st.text_input("Username (Public account only)", value=st.session_state.username)
        if st.button("Generate", type="primary"):
            if username_input:
                st.session_state.username = username_input
                with st.spinner(f"Fetching..."):
                    df, error = fetch_rss_data(username_input)
                    if error:
                        st.error(error)
                        st.session_state.data = None
                    else:
                        st.session_state.data = df
            else:
                st.warning("Enter username")
        
        st.markdown("---")
        st.caption("Note: Limited to last 50 entries due to RSS limits.")

    # --- LANDING PAGE ---
    if st.session_state.data is None:
        st.markdown("""
        <div style="text-align: center; padding: 60px; background-color: #2c3440; border-radius: 10px; border: 1px solid #456;">
            <h1 style="color: #00e054;">Letterboxd Quick Wrapped</h1>
            <p style="font-size: 1.2em; color: #abc;">
                Enter your username in the sidebar to instantly visualize your recent movie history.
            </p>
            <div style="font-size: 3em; margin: 30px;">🍿 🎬 📊</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # --- PREPARE DATA ---
    df = st.session_state.data
    total_movies = len(df)
    avg_rating = df['Rating'].mean()
    rewatches = df[df['Rewatch'] == 'Yes'].shape[0]
    rewatch_pct = (rewatches / total_movies) * 100 if total_movies > 0 else 0
    reviews_count = df['Has_Review'].sum()
    review_pct = (reviews_count / total_movies) * 100 if total_movies > 0 else 0
    decade_counts = df['Decade'].value_counts()
    streak, max_binge, binge_date = calculate_stats(df)
    
    # 1. Header & Personality (UPDATED TO SHOW ALL)
    st.title(f"🎬 {st.session_state.username}'s Recent Wrapped")
    
    personas = get_multi_personalities(total_movies, avg_rating, rewatch_pct, len(decade_counts), review_pct)
    
    # Construct HTML for ALL personalities found - NO INDENTATION TO FIX RENDERING BUG
    persona_html = """<div class="personality-card">
<div style="font-size: 1.5em; color: #9ab; margin-bottom: 20px;">Your Cinematic Archetypes</div>"""
    
    for p_title, p_desc in personas:
        persona_html += f"""
<div class="personality-entry">
<div class="personality-title">{p_title}</div>
<div class="personality-desc">"{p_desc}"</div>
</div>"""
    
    persona_html += "</div>"
    st.markdown(persona_html, unsafe_allow_html=True)

    # 2. Key Metrics
    st.markdown("### 📊 The Numbers")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Recent Logs", total_movies)
    col2.metric("Avg Rating", f"{avg_rating:.2f} ★")
    col3.metric("Review Rate", f"{review_pct:.0f}%")
    avg_year = int(df['Year'].mean()) if not df['Year'].eq(0).all() else "N/A"
    col4.metric("Avg Release Year", avg_year)

    st.markdown("---")
    
    # 3. Cinematic Roast
    st.subheader("🔥 Cinematic Roast")
    snark = generate_roast(df)
    st.markdown(f"""<div class="roast-box">"{snark}"</div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 4. Cine-MBTI
    st.subheader("🧬 Your Movie DNA (Cine-MBTI)")
    st.caption("A personality type based on your **viewing habits** (Eras, Ratings, Consistency).")
    
    mbti_code, mbti_meaning = calculate_cine_mbti(df)
    
    mbti_html = "<div class='mbti-container'>"
    for char in mbti_code:
        mbti_html += f"<div style='text-align:center;'><div class='mbti-letter'>{char}</div><div class='mbti-desc'>{mbti_meaning[char]}</div></div>"
    mbti_html += "</div>"
    st.markdown(mbti_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 5. Fun Insights (Grid)
    st.subheader("⚡ Flash Stats")
    
    fs1, fs2, fs3, fs4 = st.columns(4)
    
    with fs1:
        st.markdown(f"""<div class="fun-stat-box"><div style="font-size: 2em;">🔥</div><div>Best Streak</div><div style="font-size: 1.5em; font-weight: bold; color: #fff;">{streak} Days</div></div>""", unsafe_allow_html=True)
    with fs2:
        st.markdown(f"""<div class="fun-stat-box"><div style="font-size: 2em;">🍿</div><div>Biggest Binge</div><div style="font-size: 1.5em; font-weight: bold; color: #fff;">{max_binge} Films</div></div>""", unsafe_allow_html=True)
        
    vibe = "Balanced"
    if avg_rating > 3.5: vibe = "Positive Vibes Only"
    elif avg_rating < 2.8: vibe = "Tough Critic"
    elif rewatch_pct > 50: vibe = "Nostalgic"
    
    with fs3:
        st.markdown(f"""<div class="fun-stat-box"><div style="font-size: 2em;">✨</div><div>The Vibe</div><div style="font-size: 1.2em; font-weight: bold; color: #fff;">{vibe}</div></div>""", unsafe_allow_html=True)
    
    day_counts = df['Day'].value_counts()
    fav_day = day_counts.idxmax() if not day_counts.empty else "N/A"
    with fs4:
        st.markdown(f"""<div class="fun-stat-box"><div style="font-size: 2em;">📅</div><div>Movie Night</div><div style="font-size: 1.5em; font-weight: bold; color: #fff;">{fav_day}s</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    
    # 6. Rating Rollercoaster
    st.subheader("🎢 The Rating Rollercoaster")
    st.caption("How your ratings have trended over these 50 films.")
    
    df_trend = df.sort_values(by='Date').reset_index(drop=True)
    df_trend['Rolling_Avg'] = df_trend['Rating'].rolling(window=5, min_periods=1).mean()
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=df_trend['Date'], y=df_trend['Rating'], mode='markers', name='Rating', marker=dict(color='#40bcf4', size=8, opacity=0.6)))
    fig_trend.add_trace(go.Scatter(x=df_trend['Date'], y=df_trend['Rolling_Avg'], mode='lines', name='Trend (5-film avg)', line=dict(color='#00e054', width=3)))
    fig_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#fff", yaxis=dict(range=[0, 5.5], title="Stars"), margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_trend, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
    
    st.markdown("---")

    # 7. The Poster Wall
    st.subheader("🖼️ The Wall of Fame")
    posters_html = '<div class="poster-container">'
    for _, row in df.iterrows():
        if row['Poster']:
            posters_html += f'<img src="{row["Poster"]}" class="poster-img" title="{row["Name"]} ({row["Year"]})">'
    posters_html += '</div>'
    st.markdown(posters_html, unsafe_allow_html=True)

    # 8. Title Superlatives & Time Warp
    st.markdown("### 🏆 Fun Superlatives")
    valid_years = df[df['Year'] > 0]
    
    col_sup1, col_sup2, col_sup3 = st.columns(3)
    with col_sup1:
        longest_title = df.loc[df['Name'].str.len().idxmax()]
        st.info(f"**📝 Longest Title:**\n\n{longest_title['Name']}")
    with col_sup2:
         if not valid_years.empty:
            oldest_film = valid_years.loc[valid_years['Year'].idxmin()]
            st.success(f"**🕰️ Oldest Film:**\n\n{oldest_film['Name']} ({oldest_film['Year']})")
    with col_sup3:
        if not valid_years.empty:
            newest_film = valid_years.loc[valid_years['Year'].idxmax()]
            st.warning(f"**🆕 Newest Film:**\n\n{newest_film['Name']} ({newest_film['Year']})")

    st.markdown("---")

    # 9. Charts: Ratings & Rhythm
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("⭐ Ratings Distribution")
        rating_counts = df['Rating'].value_counts().sort_index()
        colors = ['#ff8000' if r >= 4 else '#40bcf4' if r >= 2.5 else '#667788' for r in rating_counts.index]
        fig_rating = go.Figure(data=[go.Bar(x=rating_counts.index, y=rating_counts.values, marker_color=colors, text=rating_counts.values, textposition='auto')])
        fig_rating.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#fff", margin=dict(t=20, b=20), xaxis=dict(tickmode='linear', tick0=0.5, dtick=0.5, title="Stars"), yaxis=dict(showgrid=False, visible=False))
        st.plotly_chart(fig_rating, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

    with col_right:
        st.subheader("🥁 Your Movie Rhythm")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts_radar = df['Day'].value_counts().reindex(day_order, fill_value=0)
        fig_radar = go.Figure(data=go.Scatterpolar(r=day_counts_radar.values, theta=day_order, fill='toself', line_color='#00e054'))
        fig_radar.update_layout(polar=dict(bgcolor="#1f252d", radialaxis=dict(visible=True, gridcolor="#456"), angularaxis=dict(color="#fff")), paper_bgcolor="rgba(0,0,0,0)", font_color="#fff", margin=dict(t=20, b=20, l=40, r=40))
        st.plotly_chart(fig_radar, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

    # 10. Top Rated List
    st.markdown("### 👑 Recent Favorites")
    top_movies = df.sort_values(by=['Rating', 'Date'], ascending=[False, True]).head(5)
    for i, row in top_movies.iterrows():
        cols = st.columns([1, 4])
        with cols[0]:
            if row['Poster']:
                st.image(row['Poster'], width=70)
        with cols[1]:
            st.markdown(f"**{row['Name']}** ({row['Year']})")
            st.markdown(f"<span style='color:#00e054; font-weight:bold;'>{row['Rating']} ★</span> • Watched {row['Date'].strftime('%b %d')}", unsafe_allow_html=True)

    st.markdown("---")

    # 11. Soundtrack of the Year
    st.subheader("🎵 The Soundtrack of Your Year")
    st.caption("A dynamic playlist based on your Movie MBTI and Top Hits.")
    playlist = get_soundtrack_suggestions(mbti_code, df)
    for song, artist in playlist:
        st.markdown(f"""<div class="song-row"><div class="song-icon">🎵</div><div class="song-info"><span class="song-title">{song}</span><span class="song-artist">{artist}</span></div></div>""", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #567; font-size: 0.8em;">
        Data provided by Letterboxd public RSS feed. Not affiliated with Letterboxd.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()