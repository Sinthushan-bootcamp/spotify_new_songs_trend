import requests
import datetime
from datetime import date

from dotenv import load_dotenv
load_dotenv()
import os

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTH_URL = 'https://accounts.spotify.com/api/token'

yesterday_date = date.today() - datetime.timedelta(1)

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
        release_date = datetime.datetime.strptime(new_album['release_date'], '%Y-%m-%d').date()
        if  release_date < yesterday_date and new_album['album_type'] == 'single':
            print(new_album['name'])
    offset += 50