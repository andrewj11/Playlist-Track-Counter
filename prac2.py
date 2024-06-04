import plotly.express as px
import json
import pandas as pd

data = pd.DataFrame.from_dict(json.load(open('listening_history.json')), orient = 'index')

def song_tally():
    total_plays = data
    tallys = []
    for song_id in total_plays.keys():
        play_tally = len(total_plays[song_id])
        tallys.append((song_id, play_tally))
    song_tally = pd.DataFrame(tallys, columns = ['ID', 'Play_Count'])
    return song_tally

tally_list = song_tally()

print(tally_list)

fig = px.bar(tally_list, x='ID', y='Play_Count')
fig.show()
