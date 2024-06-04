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

#load the playlist tracks dict from file
def load_playlist_tracks_from_file(file_path):
    with open(file_path, 'r') as file:
        file = json.load(file)
    return file

playlist_tracks = load_playlist_tracks_from_file('playlist_tracks_log.json') #get dict into 

#create function to get recently played tracks in a dataframe
def get_recently_played():
    results = sp.current_user_recently_played()
    tracks = []
    spotify_ids = []
    artists = []
    played_ats = []
    for idx, item in enumerate(results['items']):
        track = item['track']['name']
        spotify_id = item['track']['id']
        artist_names = [artist['name'] for artist in item['track']['artists']]
        played_at = (
            datetime.strptime(item['played_at'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/New_York')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        )
        tracks.append(track)
        spotify_ids.append(spotify_id)
        artists.append(artist_names)
        played_ats.append(played_at)
    listening_history = pd.DataFrame({'Track': tracks, 'ID': spotify_ids, 'Artist': artists, 'Played_At': played_ats})
    return listening_history

#load previous tally from file if exists
if os.path.exists('PlaysPerSong.json'):
    with open('PlaysPerSong.json', 'r') as file:
        PlaysPerSong = json.load(file)
else:
    PlaysPerSong = {}

#create function to tally how many times each song is played
def song_plays():
    last_fifty = get_recently_played()
    for song_id, time_played in zip(last_fifty['ID'], last_fifty['Played_At']):
        if song_id not in PlaysPerSong:
            PlaysPerSong[song_id] = [time_played]
        elif time_played not in PlaysPerSong[song_id]:
            PlaysPerSong[song_id].append(time_played) 
    return PlaysPerSong

PlaysPerSong = song_plays()

#save combined tally to file
with open('PlaysPerSong.json' ,'w') as file:
    json.dump(PlaysPerSong, file)

#create function to tally how many times song have been listened to
def song_tally():
    tallys = []
    for song_id in PlaysPerSong.keys():
        play_tally = len(PlaysPerSong[song_id])
        tallys.append((song_id, play_tally))
    song_tally = pd.DataFrame(tallys, columns = ['ID', 'Play_Count'])
    return song_tally

tally_list = song_tally()

print(get_recently_played())
print(pd.DataFrame.from_dict(song_plays(), orient='index'))
print(tally_list.sort_values(by=['Play_Count'], ascending=False))
