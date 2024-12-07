# -*- coding: utf-8 -*-
"""CS6220_Spotify_Music_Recommendation_System.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/lihaohl0307/Spotify-Music-Recommendation/blob/main/CS6220_Spotify_Music_Recommendation_System.ipynb

# **Final Project: Spotify Music Recommendation System**

### Team Members:
### placeholder

### Package Installation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import spotipy
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
from spotipy.oauth2 import SpotifyClientCredentials

"""### Data Import"""

data = pd.read_csv("./spotify-dataset/data/data.csv")
songs_data = pd.read_csv('./spotify-dataset/data/data.csv')
genre_data = pd.read_csv('./spotify-dataset/data/data_by_genres.csv')
print(data.shape)
print(data.head(5))

song_cluster_pipeline = Pipeline([('scaler', StandardScaler()),
                                  ('kmeans', KMeans(n_clusters=20,
                                   verbose=False))
                                 ], verbose=False)

X = data.select_dtypes(np.number)
number_cols = list(X.columns)
song_cluster_pipeline.fit(X)
song_cluster_labels = song_cluster_pipeline.predict(X)
data['cluster_label'] = song_cluster_labels

"""### Connect to Spotify API"""

client_id = "7d79fe83da984659b5581054295c34c9"
client_secret = "432302ce5805441dac55670e8a6144bd"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# API testing
name = ["Michael Jackson","pitbull","Christina","Elvis Presley"]
result = sp.search(name)
result['tracks']['items'][1]['artists']

"""## K-means clustering on songs"""

# Reload data in seperate data frame
songs_df = pd.read_csv('./spotify-dataset/data/data.csv')

selected_features = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                     'liveness', 'loudness', 'speechiness', 'valence', 'tempo',
                     'duration_ms', 'key', 'mode']

"""### PCA for Dimensionality Reduction (retain 95% variance)"""

# Standardize the Features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(songs_df[selected_features])

pca = PCA(n_components=0.95, random_state=42) # 95%
pca_features = pca.fit_transform(scaled_features)

explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

print(f"Number of components selected: {pca.n_components_}")
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")

# Calculate Cumulative Variance for Full Components
pca_full = PCA(random_state=42)
pca_full.fit(scaled_features)
explained_variance_full = pca_full.explained_variance_ratio_
cumulative_variance_full = np.cumsum(explained_variance_full)

# Plot total explained variance
plt.figure(figsize=(8, 6))
plt.plot(range(1, len(cumulative_variance_full) + 1), cumulative_variance_full, color='black', label="Cumulative Explained Variance")
plt.axhline(y=0.95, color='red', linestyle='--', label="95% Variance Threshold")
plt.axvline(x=pca.n_components_, color='blue', linestyle='--', label=f"{pca.n_components_} Components")

plt.xlabel('Number of Components')
plt.ylabel('Total Explained Variance')
plt.title('Explained Variance vs Number of Components')
plt.legend(loc='lower right')
plt.grid(True)
plt.show()

# plt.figure(figsize=(10, 7))
# plt.plot(cumulative_variance, color='k', lw=2)
# plt.xlabel('Number of components')
# plt.ylabel('Total explained variance')
# plt.xlim(0, len(selected_features))
# plt.yticks(np.arange(0, 1.1, 0.1))
# plt.axvline(pca.n_components_, c='b', label=f'{pca.n_components_} components')
# plt.axhline(0.95, c='r', label='95% variance')
# plt.legend()
# plt.show()

# Principal Component Loadings - detailed weighted features for each PC
loadings = pd.DataFrame(
    pca.components_.T,
    columns=[f'Principal Component {i+1}' for i in range(pca.n_components_)],
    index=selected_features
)

print("Feature Contributions to Principal Components:")
print(loadings)

# PC and explained variance display
components_df = pd.DataFrame({
    'Principal Component': [f'PC{i+1}' for i in range(len(explained_variance))],
    'Explained Variance': explained_variance,
    'Cumulative Variance': cumulative_variance
})

print("\nExplained Variance for Principal Components:")
print(components_df)

"""### Elbow Method to determine optimal k for clustering"""

inertias = []
k_values = range(5, 30)

for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(pca_features)
    inertias.append(kmeans.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(k_values, inertias, 'bo-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal k')
plt.show()

"""### Apply K-means Clustering"""

optimal_k = 8
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
kmeans.fit(pca_features)

# Assign clusters to the original DataFrame
songs_df['cluster'] = kmeans.labels_

# Function to retrieve song data from Spotify API
def find_song_from_spotify(name, year):
    song_data = defaultdict()
    results = sp.search(q=f'track:{name} year:{year}', limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    # Basic metadata
    song_data['name'] = results['name']
    song_data['artists'] = ', '.join([artist['name'] for artist in results['artists']])
    song_data['year'] = year
    song_data['duration_ms'] = results['duration_ms']
    song_data['explicit'] = int(results['explicit'])

    # Audio features
    for key, value in audio_features.items():
        if key in selected_features:
            song_data[key] = value

    return song_data

def recommend_songs_kmeans_with_api(input_songs, songs_df, pca_model, scaler, kmeans_model, n_recommendations=10):
    # Ensure 'cluster' column exists
    if 'cluster' not in songs_df.columns:
        raise KeyError("'cluster' column not found in songs_df. Ensure k-means clustering is performed.")

    clusters = []
    input_song_names = []
    new_songs = []  # Store newly added songs for dynamic clustering

    for song in input_songs:
        song_name = song['name']
        year = song['year']
        print(song_name, year)
        matched_songs = songs_df[songs_df['name'].str.lower() == song_name.lower()]
        if matched_songs.empty:
            print(f"Song '{song_name}' not found in the dataset. Fetching from Spotify...")
            # Attempt to fetch song from Spotify API
            spotify_song_data = find_song_from_spotify(song_name, year)
            if spotify_song_data:
                new_songs.append(spotify_song_data)
                print(f"Added '{spotify_song_data['name']}' from Spotify.")
            else:
                print(f"Could not find '{song_name}' on Spotify.")
            continue

        input_song_names.append(song_name.lower())
        song_clusters = matched_songs['cluster'].unique()
        clusters.extend(song_clusters)

    # Dynamically cluster new songs (if any)
    if new_songs:
        new_songs_df = pd.DataFrame(new_songs)
        scaled_new_features = scaler.transform(new_songs_df[selected_features])
        pca_new_features = pca_model.transform(scaled_new_features)
        new_clusters = kmeans_model.predict(pca_new_features)
        new_songs_df['cluster'] = new_clusters
        songs_df = pd.concat([songs_df, new_songs_df], ignore_index=True)
        clusters.extend(new_clusters)

    if not clusters:
        print("No matching songs found in the dataset or Spotify.")
        return []

    # Unique clusters
    clusters = list(set(clusters))

    # Songs in the same cluster(s)
    recommended_songs = songs_df[songs_df['cluster'].isin(clusters)]

    # Exclude input songs
    recommended_songs = recommended_songs[~recommended_songs['name'].str.lower().isin(input_song_names)]

    # Randomly select recommendations
    recommended_songs = recommended_songs.sample(n=n_recommendations, random_state=42)
    return recommended_songs[['name', 'year', 'artists', 'cluster']]

# Test input
input_songs = [{'name': 'Come As You Are', 'year':1991},
                {'name': 'Smells Like Teen Spirit', 'year': 1991},
                {'name': 'Lithium', 'year': 1992},
                {'name': 'All Apologies', 'year': 1993},
                {'name': 'Stay Away', 'year': 1993},
               {'name': 'Work', 'year':2016},
                {'name': 'We Found Love', 'year': 2011},
                {'name': 'Diamonds', 'year': 2012},
                {'name': 'Umbrella', 'year': 2007},
                {'name': 'Stay', 'year': 2012}]

recommendations = recommend_songs_kmeans_with_api(
    input_songs,
    songs_df,
    pca_model=pca,
    scaler=scaler,
    kmeans_model=kmeans,
    n_recommendations=10
)

# Display recommendations
print(recommendations)

def get_average_popularity_with_spotipy(recommendations_df):
    total_popularity = 0
    song_count = 0

    for _, row in recommendations_df.iterrows():
        song_name = row['name']
        year = row['year']

        # Construct a search query with name and year
        query = f"track:{song_name} year:{year}"

        try:
            results = sp.search(q=query, type='track', limit=10)  # Fetch multiple results to filter by year
            if results and results['tracks']['items']:
                # Filter results by release year
                filtered_tracks = [
                    track for track in results['tracks']['items']
                    if track['album']['release_date'].startswith(str(year))
                ]
                if filtered_tracks:
                    # Use the first matching track
                    track = filtered_tracks[0]
                    # print(song_name, track['popularity'])
                    total_popularity += track['popularity']
                    song_count += 1
                else:
                    print(f"No exact year match found for '{song_name}' in {year}")
            else:
                print(f"No match found for '{song_name}' in {year}")
        except Exception as e:
            print(f"Error fetching data for '{song_name}' in {year}: {e}")

    if song_count == 0:
        return 0  # Avoid division by zero

    # Calculate the average popularity
    return total_popularity / song_count

# Get average popularity
average_popularity = get_average_popularity_with_spotipy(recommendations)
print(f"Average Popularity: {average_popularity}")

"""## Enhanced K-Means Model with Weighted Genre"""

# Define feature columns
number_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
               'liveness', 'loudness', 'speechiness', 'valence', 'tempo',
               'duration_ms', 'key', 'mode']

def classify_songs_by_genre(songs_df, genre_df, feature_columns):
    """
    Assign each song in the songs_df to the closest genre based on shared features in genre_df.
    """
    # Ensure all features are numeric and explicitly cast to float64
    songs_df[feature_columns] = songs_df[feature_columns].apply(pd.to_numeric, errors='coerce').fillna(songs_df[feature_columns].mean())
    genre_df[feature_columns] = genre_df[feature_columns].apply(pd.to_numeric, errors='coerce').fillna(genre_df[feature_columns].mean())

    # Extract genre features and explicitly cast to float64
    genre_features = genre_df[feature_columns].values.astype(np.float64)
    classified_genres = []

    for _, song in songs_df.iterrows():
        # Extract features for the current song and explicitly cast to float64
        song_features = song[feature_columns].values.reshape(1, -1).astype(np.float64)

        # Compute distances between the song and all genres
        distances = cdist(song_features, genre_features, metric='euclidean')

        # Assign the closest genre
        closest_genre_index = distances.argmin()
        closest_genre = genre_df.iloc[closest_genre_index]['genres']
        classified_genres.append(closest_genre)

    # Add the classified genres to the songs DataFrame
    songs_df['classified_genre'] = classified_genres
    return songs_df

# Classify songs into different genres
songs_with_genre_df = classify_songs_by_genre(songs_data, genre_data, number_cols)

songs_with_genre_df.head()

# Encode the 'classified_genre' column into numeric values
label_encoder = LabelEncoder()
songs_with_genre_df['classified_genre_encoded'] = label_encoder.fit_transform(songs_with_genre_df['classified_genre'])

# Update the feature list
selected_features_with_genre = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                                'liveness', 'loudness', 'speechiness', 'valence', 'tempo',
                                'duration_ms', 'key', 'mode', 'classified_genre_encoded'] # use encoded classfied_genre(convert string to float)

# Standardize the Features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(songs_with_genre_df[selected_features_with_genre])

# Apply PCA
pca_genre = PCA(n_components=0.95, random_state=42)  # 95% variance threshold
pca_features_with_genre = pca_genre.fit_transform(scaled_features)

# Calculate Explained Variance
explained_variance_genre_enhanced = pca_genre.explained_variance_ratio_
cumulative_variance_genre_enhanced = np.cumsum(explained_variance_genre_enhanced)

print(f"Number of components selected: {pca_genre.n_components_}")
print(f"Explained variance ratio: {pca_genre.explained_variance_ratio_}")

# apply k-means clustering
optimal_k = 8
enhanced_kmeans = KMeans(n_clusters=optimal_k, random_state=42)
enhanced_kmeans.fit(pca_features_with_genre)

# Assign clusters to the original DataFrame
songs_with_genre_df['cluster'] = enhanced_kmeans.labels_

# Test input
input_songs = [{'name': 'Come As You Are', 'year':1991},
                {'name': 'Smells Like Teen Spirit', 'year': 1991},
                {'name': 'Lithium', 'year': 1992},
                {'name': 'All Apologies', 'year': 1993},
                {'name': 'Stay Away', 'year': 1993},
               {'name': 'Work', 'year':2016},
                {'name': 'We Found Love', 'year': 2011},
                {'name': 'Diamonds', 'year': 2012},
                {'name': 'Umbrella', 'year': 2007},
                {'name': 'Stay', 'year': 2012}]

enhanced_recommendations = recommend_songs_kmeans_with_api(
    input_songs,
    songs_with_genre_df,
    pca_model=pca_genre,
    scaler=scaler,
    kmeans_model=kmeans,
    n_recommendations=10
)

# Display recommendations
print(enhanced_recommendations)

# Get average popularity
enhanced_average_popularity = get_average_popularity_with_spotipy(enhanced_recommendations)
print(f"Average Popularity: {enhanced_average_popularity}")

