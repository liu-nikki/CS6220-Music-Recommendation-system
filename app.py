import streamlit as st
from cs6220_spotify_music_recommendation_system import (
    recommend_songs_kmeans_with_api,
    songs_df,
    sp,
    scaler,
    pca,
    kmeans
)

# Streamlit UI
st.title("Spotify Music Recommendation System")

st.sidebar.header("Enter Song Details")
song_name = st.sidebar.text_input("Song Name", "")
year = st.sidebar.number_input("Year", min_value=1900, max_value=2024, step=1)

if st.sidebar.button("Recommend"):
    if song_name and year:
        input_song = [{"name": song_name, "year": year}]
        recommendations = recommend_songs_kmeans_with_api(
            input_songs=input_song,
            songs_df=songs_df,
            pca_model=pca,
            scaler=scaler,
            kmeans_model=kmeans,
            n_recommendations=10
        )
        if not recommendations.empty:
            st.success(f"Top {len(recommendations)} Recommendations for '{song_name}':")
            st.dataframe(recommendations)
        else:
            st.error("No recommendations found. Please try different inputs.")
    else:
        st.warning("Please enter both Song Name and Year.")

st.write("### Dataset Overview")
st.dataframe(songs_df.head())
