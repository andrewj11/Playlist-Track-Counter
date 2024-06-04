import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
import os
import json

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000'

sp = spotipy.Spotify(
    auth_manager = SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = REDIRECT_URI,
        scope = ('user-top-read','user-read-recently-played','user-read-private','user-read-email','playlist-read-private','playlist-read-collaborative','playlist-modify-private','playlist-modify-public','user-top-read','user-read-playback-position')
    )
)

#st.set_page_config(page_title = 'Spotify Dashboard', page_icon = 'random')
#st.title('Analysis on Recently Played Songs')
#st.write('This is a breakdown of recently played songs')

#function to get playlist items
def get_user_playlists():
    playlists = sp.current_user_playlists()
    return playlists['items']

#get tracks from playlist items
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

#load or create playlist tracks dictionary
def load_or_create_playlist_tracks():
    try:
        with open('playlist_tracks_log.json', 'r') as file:
            playlist_tracks = json.load(file)
    except FileNotFoundError:
        playlist_tracks = {}
    return playlist_tracks

#get playlists
user_playlists = get_user_playlists()

#Dictionary to store playlists, their tracks, and play logs
playlist_tracks = load_or_create_playlist_tracks()

#Check if playlist_tracks is empty or not
if not playlist_tracks:
    #iterate through each playlist
    for playlist in user_playlists:
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        print(f"Processing playlist: {playlist_name}")
        #Get tracks in the playlist
        tracks = get_playlist_tracks(playlist_id)
        #extract track names
        track_names = [track['track']['name'] for track in tracks]
        #store track names in the dictionary wiht playlist name as key
        playlist_tracks[playlist_name] = {track_name: [] for track_name in track_names}
    
    #save playlist_track dictionary to a file
    with open('playlist_tracks_log.json', 'w') as file:
        json.dump(playlist_tracks, file)
