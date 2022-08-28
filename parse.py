import json
import time
import spotipy
import datetime
from os import listdir
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

class Artist:
    songs = []
    name = ""

    def __init__(self, name) -> None:
        self.name = name

    def addSong(self, song):
        self.songs.append(song)

class Song:
    def __init__(self, name, artist):
        self.name = name
        self.artist = artist
        self.streams = []

    def __str__(self):
        return "(" + str(len(self.streams)) + ") " + self.name + " - " + self.artist.name

    def addPlay(self, stream_data, ms_played):
        stream_date = stream_data.split(' ')[0].split('-')
        stream_time = stream_data.split(' ')[1].split(':')
        stream_timestamp = time.mktime((datetime.datetime(int(stream_date[0]), int(stream_date[1]), int(stream_date[2]), int(stream_time[0]), int(stream_time[1]))).timetuple()) - ms_played
        
        if len([stream for stream in self.streams if (stream[0] == stream_timestamp) and (stream[1] == ms_played)]) == 0:
            self.streams.append((stream_timestamp, ms_played))

    def printStream(self, stream):
        print(datetime.datetime.fromtimestamp(stream[0]))

    def getTimePlayed(self):
        total_time = 0
        for stream in self.streams:
            total_time += stream[1]

        return total_time

def clearLine():
    print(" " * 100, end="\r", flush=True)

def run():
    data_folder_path = ""
    client_id = ""
    secret = ""

    artists = []
    songs = []

    with open(".arguments") as info_file:
        info_dict = {}

        for line in info_file:
            line = line.replace('\n', '')
            line = line.split('=')
            info_dict[line[0].strip()] = line[1].strip()

        data_folder_paths = info_dict["paths"].split(", ")
        client_id = info_dict["cid"]
        secret = info_dict["secret"]
        redirect_uri = info_dict["redirect_uri"]

    for data_folder_path in data_folder_paths:
        filenames = [file for file in listdir(data_folder_path) if "StreamingHistory" in file]
        raw_data = []

        for filename in filenames:
            full_path = data_folder_path + filename
            print(" " * 100, end="\r", flush=True)
            print("reading \"" + full_path + "\"")

            with open(full_path) as data_file:
                data = json.load(data_file)

                file_length = len(data)
                current_line = 0

                for line in data:
                    current_line += 1
                    progress = current_line / file_length

                    length = len("reading " + full_path) + 1
                    clearLine()
                    print("[" + "#" * int(length * progress) + "=" * int(length - (length * progress)) + "]", end="\r", flush=True)

                    if len([artist for artist in artists if artist.name == line["artistName"]]) == 0:
                        artists.append(Artist(line["artistName"]))
                    
                    for artist in [artist for artist in artists if artist.name == line["artistName"]]:
                        if(len([song for song in artist.songs if song.name == line["trackName"]])) == 0:
                            new_song = Song(line["trackName"], artist)
                            artist.addSong(new_song)
                            songs.append(new_song)
                        
                        for song in [song for song in artist.songs if song.name == line["trackName"]]:
                            song.addPlay(line["endTime"], line["msPlayed"])

    clearLine()
    print("sorting...")
    songs.sort(key=lambda song : len(song.streams))

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read", client_id=client_id, client_secret=secret, redirect_uri=redirect_uri))

    liked_songs_long = []
    liked_songs = []
    offset = 0

    clearLine()
    print("getting liked songs...")
    while len(sp.current_user_saved_tracks(limit=50, offset=offset)["items"]) > 0:
        for item in sp.current_user_saved_tracks(limit=50, offset=offset)["items"]:
            liked_songs_long.append(item) 
            
        offset += 50
    
    for idx, item in enumerate(liked_songs_long):
        track = item["track"]
        name = track["name"]
        artist = track["artists"][0]["name"]
        
        for song in songs:
            if song.name == name and song.artist.name == artist:
                liked_songs.append(song)

    for song in liked_songs:
        if song.getTimePlayed() < 600000:
            print(str(song))

run()