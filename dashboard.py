import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

with open('PlaysPerSong.json', 'r') as file:
    PlaysPerSong = json.load(file)

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

def song_tally():
    total_plays = PlaysPerSong
    tallys = []
    for song_id in total_plays.keys():
        play_tally = len(total_plays[song_id])
        tallys.append((song_id, play_tally))
    song_tally = pd.DataFrame(tallys, columns = ['ID', 'Play_Count'])
    return song_tally

tally_list = (song_tally().sort_values('Play_Count', ascending=False))

def get_song_name():
    song_names = []
    for i in tally_list['ID']:
        name =  sp.track(i)['name']
        song_names.append(name)
    return song_names

def get_artist_names():
    temp_artist_names = []
    batch_size = 50 #define a batch size for API calls
    processed_songs = set()
    try:
        for i in range(0, len(tally_list['ID']), batch_size):
            batch_ids = tally_list['ID'][i:i+batch_size]
            tracks_info = sp.tracks(batch_ids)['tracks']
            for track_info in tracks_info:
                song_id = track_info['id']
                if song_id not in processed_songs:
                    # Append the first artist separately
                    first_artist = track_info['artists'][0]['name']
                    rest_artists = [artist['name'] for artist in track_info['artists'][1:]]
                    artist_names = first_artist + ', '.join(rest_artists)
                    temp_artist_names.append(artist_names)
                    processed_songs.add(song_id)
    except Exception as e:
        print("Error fetching artist names:", e)
    return temp_artist_names
song_name = get_song_name()
artist_names = get_artist_names()
times_played = tally_list["Play_Count"]

print(times_played)

table = go.Figure(data = [go.Table(
    header = dict(values=['Song', 'Artist', 'Plays'],
                  line_color = 'darkslategray',
                  fill_color = 'lightskyblue',
                  align = 'left'),
    cells = dict(values = [song_name, artist_names, times_played],
                 line_color = 'darkslategray',
                 fill_color = 'lightcyan',
                 align = 'left'))
])

table.update_layout(width = 1000, height = 30000)
table.show()

'''
it's duplicating songs with multiple artists
'''
