import requests
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import os
import psycopg2
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/spotify")

conn = psycopg2.connect("dbname=spotify user=postgres password=postgres")
cur = conn.cursor()

sql_query = """
    CREATE TABLE IF NOT EXISTS spotify_new_releases(
        id VARCHAR(200),
        release_date VARCHAR(200),
        name VARCHAR(200),
        Artist VARCHAR(200),
        Features INT,
        popularity INT,
        danceability NUMERIC,
        energy NUMERIC,
        key INT,
        loudness NUMERIC,
        mode INT,
        speechiness NUMERIC,
        acousticness NUMERIC,
        instrumentalness NUMERIC,
        liveness NUMERIC,
        valence NUMERIC,
        tempo NUMERIC,
        CONSTRAINT primary_key_constraint PRIMARY KEY (id)
    )
    """
cur.execute(sql_query)
conn.commit()
df = pd.DataFrame()

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTH_URL = 'https://accounts.spotify.com/api/token'



token_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

token_data = token_response.json()
spotify_token = token_data['access_token']

NEW_ALBUMS_URL = 'https://api.spotify.com/v1/browse/new-releases'

offset = 0
releases = True
while releases:
    new_albums_response = requests.get(NEW_ALBUMS_URL, 
        headers={
            'Authorization': f'Bearer {spotify_token}'
        },
        params={
            'limit': 50,
            'offset': offset,
        })
    new_albums = new_albums_response.json()
    releases = new_albums['albums']['next']
    for new_album in new_albums['albums']['items']:
        if new_album['album_type'] == 'single':
            album_id = new_album['id']
            album_url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
            track_list_response = requests.get(album_url, 
            headers={
                'Authorization': f'Bearer {spotify_token}'
            })
            track_list = track_list_response.json()
            track_id = track_list['items'][0]['id']
            track_url = f'https://api.spotify.com/v1/tracks/{track_id}'
            audio_features_url = f'https://api.spotify.com/v1/audio-features/{track_id}'
            track_info_response = requests.get(track_url, 
            headers={
                'Authorization': f'Bearer {spotify_token}'
            })
            audio_features_response = requests.get(audio_features_url, 
            headers={
                'Authorization': f'Bearer {spotify_token}'
            })
            track_info = track_info_response.json()
            audio_features = audio_features_response.json()
            df = df.append({
                'id': track_id,
                'release_date':track_info['album']['release_date'], 
                'name': track_info['name'],
                'artist': track_info['artists'][0]['name'],
                'features': len(track_info['artists']) -1,
                'popularity': track_info['popularity'],
                'danceability': audio_features['danceability'],
                'energy': audio_features['energy'],
                'key': audio_features['key'],
                'loudness': audio_features['loudness'],
                'mode': audio_features['mode'],
                'speechiness': audio_features['speechiness'],
                'acousticness': audio_features['acousticness'],
                'instrumentalness': audio_features['instrumentalness'],
                'liveness': audio_features['liveness'],
                'valence': audio_features['valence'],
                'tempo': audio_features['tempo'],
                },
                ignore_index=True)
    offset += 50


df.to_sql("spotify_new_releases", engine, index=False, if_exists='append')

conn.close()