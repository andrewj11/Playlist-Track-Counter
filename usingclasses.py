import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import pytz

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000'

#create authentication token
sp = spotipy.Spotify(
    auth_manager = SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = REDIRECT_URI,
        scope = ('user-top-read',
                 'user-read-recently-played',
                 'user-read-private',
                 'user-read-email',
                 'playlist-read-private',
                 'playlist-read-collaborative',
                 'playlist-modify-private',
                 'playlist-modify-public',
                 'user-top-read',
                 'user-read-playback-position'
                 )
    )
)

class Song:
    
    def __init__(self, artist, id, times_played=None):
        self.artist = artist
        self.id = id
        if times_played is None:
            self.times_played = []
        else:
            self.times_played =times_played


#create class object for each song in recently played and track how many times it was played.
def get_recently_played():
    results = sp.current_user_recently_played()
    for idx, song in enumerate(results['items']):
        artist_name = [artist['name'] for artist in song['track']['artists']]
        song_id = song['track']['id']
        played_at = (
            datetime.strptime(song['played_at'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/New_York')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        )
        song['track']['name'] = Song(artist_name, song_id, played_at)
    return idx

print(get_recently_played())
