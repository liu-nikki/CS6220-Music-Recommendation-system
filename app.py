import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API Credentials
client_id = "7d79fe83da984659b5581054295c34c9"
client_secret = "432302ce5805441dac55670e8a6144bd"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load Data
@st.cache_data
def load_data():
    data = pd.read_csv("./spotify-dataset/data/data.csv")
    return data

data = load_data()

# K-means Clustering Pipeline
song_cluster_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=20, verbose=False))
])

# Fit the Pipeline
X = data.select_dtypes(np.number)
song_cluster_pipeline.fit(X)
data['cluster_label'] = song_cluster_pipeline.predict(X)

# Streamlit UI
st.title("Spotify Music Recommendation System")

st.sidebar.header("Search for a Song")
artist_name = st.sidebar.text_input("Artist Name", "")
song_title = st.sidebar.text_input("Song Title", "")

if st.sidebar.button("Recommend"):
    if artist_name and song_title:
        result = sp.search(q=f"{song_title} {artist_name}", limit=1)
        if result['tracks']['items']:
            st.success(f"Found Song: {result['tracks']['items'][0]['name']} by {artist_name}")
            st.write("Top Recommendations:")
            st.dataframe(data.sample(5))  # Placeholder for real recommendations
        else:
            st.error("Song not found. Please try different inputs.")
    else:
        st.warning("Please enter both Artist Name and Song Title.")

st.write("### Dataset Overview")
st.dataframe(data.head())
