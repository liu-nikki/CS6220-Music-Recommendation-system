
# Spotify Music Recommendation System

## Contributors
- **Xiaoshu Liu, Xinyue Han, Hao Li, Siying Lu**

## Overview
This project implements a **Spotify Music Recommendation System** that leverages audio features and clustering algorithms to suggest music similar to user preferences. It collects data using Spotify's Web API, performs feature analysis and clustering, and delivers recommendations based on user input.

### Key Features:
- Collects and analyzes Spotify track data
- Performs clustering using k-Means and recommendation generation
- Provides an interactive user interface through Streamlit

---

## Instructions

### 1. Prerequisites
- Python 3.9 or higher
- Spotify Developer Account (for API credentials)

---

### 2. Installation and Setup

#### Step 1: Set Up a Python Virtual Environment
1. Create a virtual environment:
   ```bash
   python3 -m venv env
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```
   - On Windows:
     ```bash
     env\Scripts\activate
     ```

#### Step 2: Install Dependencies
1. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

#### Step 3: Configure Spotify API Credentials
1. Go to the [Spotify Developer Portal](https://developer.spotify.com/) and create an app.
2. Obtain your `Client ID` and `Client Secret`.
3. Export them as environment variables:
   - On macOS/Linux:
     ```bash
     export SPOTIPY_CLIENT_ID='your_client_id'
     export SPOTIPY_CLIENT_SECRET='your_client_secret'
     ```
   - On Windows (Command Prompt):
     ```cmd
     set SPOTIPY_CLIENT_ID=your_client_id
     set SPOTIPY_CLIENT_SECRET=your_client_secret
     ```

#### Step 4: Run the Application
1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`.

---

### Files in the Repository

1. **`app.py`**
   - The main entry point for the Streamlit web application. It integrates the recommendation system logic and serves the user interface for generating Spotify music recommendations.

2. **`cs6220_spotify_music_recommendation_system.py`**
   - Implements advanced recommendation logic, including clustering, audio feature analysis, and performance evaluation. This script contains functions for handling Spotify API data and generating music clusters.

3. **`music_recommendation_system.py`**
   - A complementary script that focuses on the foundational recommendation algorithm and basic data processing. Includes methods to preprocess Spotify track data and build recommendations.

4. **`requirements.txt`**
   - Lists all the dependencies required for the project. Libraries include `pandas`, `numpy`, `scikit-learn`, and `streamlit` for application and data processing purposes.


---

### Google Colab
For an alternative execution method, you can run this project directly in Google Colab:  
[Spotify Music Recommendation System - Colab Notebook](https://colab.research.google.com/drive/1UAoif2RnzGp1AYmRKK-tVYu8nWbQEnfp)

---

### Additional Resources

- [Spotify Developer Portal](https://developer.spotify.com/)

