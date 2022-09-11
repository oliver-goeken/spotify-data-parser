import time
import spotipy
import datetime
import pandas as pd
from utils import clear_line
from spotipy.oauth2 import SpotifyOAuth


class Artist:
    songs = []
    name = ""

    def __init__(self, name) -> None:
        self.name = name

    def add_song(self, song):
        self.songs.append(song)


class Song:
    def __init__(self, name, artist):
        self.name = name
        self.artist = artist
        self.streams = []

    def __str__(self):
        return (
            "(" + str(len(self.streams)) + ") " + self.name + " - " + self.artist.name
        )

    def add_play(self, stream_data, ms_played):
        stream_date = stream_data.split(" ")[0].split("-")
        stream_time = stream_data.split(" ")[1].split(":")
        stream_timestamp = (
            time.mktime(
                (
                    datetime.datetime(
                        int(stream_date[0]),
                        int(stream_date[1]),
                        int(stream_date[2]),
                        int(stream_time[0]),
                        int(stream_time[1]),
                    )
                ).timetuple()
            )
            - ms_played
        )

        if (
            len(
                [
                    stream
                    for stream in self.streams
                    if (stream[0] == stream_timestamp) and (stream[1] == ms_played)
                ]
            )
            == 0
        ):
            self.streams.append((stream_timestamp, ms_played))

    def print_stream(self, stream):
        print(datetime.datetime.fromtimestamp(stream[0]))

    def print_time_played(self):
        return_str = ""
        time_played = self.get_time_played()

        if time_played > 3600000:
            return_str += str(self.get_hours_played()) + " hours, "

        if time_played > 60000:
            return_str += str(self.get_mins_played()) + " mins, "

        return_str += str(self.get_secs_played()) + " secs"

        return return_str

    def get_time_played(self):
        total_time = 0

        for stream in self.streams:
            total_time += stream[1]

        return total_time

    def get_secs_played(self):
        return int((self.get_time_played() - (self.get_mins_played() * 60000)) / 1000)

    def get_mins_played(self):
        return int(
            (self.get_time_played() - (self.get_hours_played() * 3600000)) / 60000
        )

    def get_hours_played(self):
        return int(self.get_time_played() / 3600000)


def main():
    data = pd.read_hdf("data/streaming_data.h5", "fixed").to_dict("records")

    args = {}

    artists = []
    songs = []

    with open(".credentials") as info_file:
        for line in info_file:
            line = line.replace("\n", "")
            line = line.split("=")
            args[line[0].strip()] = line[1].strip()

    print("loading data...")

    start = time.perf_counter()

    song_idx = 0

    data_by_artist = []
    sorted_streams = []

    for stream in data:
        if (
            data_by_artist
            and data_by_artist[-1]
            and stream["artistName"] == data_by_artist[-1][0]["artistName"]
        ):
            data_by_artist[-1].append(stream)
        else:
            data_by_artist.append([stream])

    for artist_streams in data_by_artist:
        data_by_song = []

        for stream in artist_streams:
            if (
                data_by_song
                and data_by_song[-1]
                and stream["trackName"] == data_by_song[-1][0]["trackName"]
            ):
                data_by_song[-1].append(stream)
            else:
                data_by_song.append([stream])

        sorted_streams.append(data_by_song)

    for artist_streams in sorted_streams:
        current_artist = Artist(artist_streams[0][0]["artistName"])
        artists.append(current_artist)

        for song_streams in artist_streams:
            current_song = Song(song_streams[0]["trackName"], current_artist)
            current_artist.add_song(current_song)
            songs.append(current_song)

            for song in song_streams:
                current_song.add_play(song["endTime"], song["msPlayed"])

                song_idx += 1
                length = 50
                progress = song_idx / len(data)

                clear_line()
                print(
                    "["
                    + "#" * int(length * progress)
                    + "=" * int(length - (length * progress))
                    + "]["
                    + str(int(progress * 100))
                    + "%]["
                    + str("{:.2f}".format(time.perf_counter() - start))
                    + " secs]",
                    end="\r",
                    flush=True,
                )

    songs.sort(key=lambda song: len(song.streams))

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="user-library-read",
            client_id=args["spotify_client_id"],
            client_secret=args["spotify_secret"],
            redirect_uri=args["spotify_redirect_uri"],
        )
    )

    liked_songs = []
    liked_songs_long = []
    offset = 0

    clear_line()
    print("getting liked songs...")

    while len(sp.current_user_saved_tracks(limit=50, offset=offset)["items"]) > 0:
        for item in sp.current_user_saved_tracks(limit=50, offset=offset)["items"]:
            track = item["track"]
            name = track["name"]
            artist = track["artists"][0]["name"]

            for song in songs:
                if song.name == name and song.artist.name == artist:
                    liked_songs.append(song)
                    break
            else:
                new_song = None
                new_artist = None

                for existing_artist in artists:
                    if existing_artist.name == artist:
                        new_artist = existing_artist
                        break
                else:
                    new_artist = Artist(artist)

                new_song = Song(name, new_artist)

                songs.append(new_song)
                new_artist.add_song(new_song)
                liked_songs.append(new_song)

        offset += 50

    liked_songs.sort(key=lambda song: song.get_time_played(), reverse=True)


if __name__ == "__main__":
    main()
