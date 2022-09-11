import math
import time
import json
import pandas as pd
from os import listdir
from utils import clear_line


def main():
    streams = []

    start = time.perf_counter()
    with open(".credentials") as info_file:
        info_dict = {}

        for line in info_file:
            line = line.replace("\n", "")
            line = line.split("=")
            info_dict[line[0].strip()] = line[1].strip()

        data_folder_paths = info_dict["paths"].split(", ")

    for data_folder_path in data_folder_paths:
        files = [
            data_folder_path + file
            for file in listdir(data_folder_path)
            if "StreamingHistory" in file
        ]

        for file in files:
            clear_line()
            print('reading "' + file + '"')

            with open(file) as data_file:
                data = json.load(data_file)
                start_parse_file = time.perf_counter()

                for idx, line in enumerate(data):
                    progress = idx / len(data)
                    length = len("reading " + file) + 1
                    clear_line()
                    print(
                        "["
                        + "#" * int(length * progress)
                        + "=" * int(length - (length * progress))
                        + "]["
                        + str(int(progress * 100))
                        + "%]["
                        + str("{:.2f}".format(time.perf_counter() - start_parse_file))
                        + " secs]",
                        end="\r",
                        flush=True,
                    )

                    streams.append(line)

    streams.sort(
        key=lambda line: (
            line["artistName"],
            line["trackName"],
            line["endTime"],
            line["msPlayed"],
        )
    )

    unique_streams = [streams[0]]

    clear_line()
    print()
    print("removing duplicates...")
    start_remove_duplicates = time.perf_counter()
    for idx, line in enumerate(streams):
        if not line == unique_streams[-1]:
            progress = idx / len(streams)
            length = 70
            clear_line()
            print(
                "["
                + "#" * int(length * progress)
                + "=" * int(length - (length * progress))
                + "]["
                + str(int(progress * 100))
                + "%]["
                + str("{:.2f}".format(time.perf_counter() - start_remove_duplicates))
                + " secs]",
                end="\r",
                flush=True,
            )
            unique_streams.append(line)

    clear_line()
    print("sorting data...")
    print()

    streaming_data = pd.DataFrame.from_records(unique_streams)
    streaming_data.to_hdf("data/streaming_data.h5", "fixed")

    print(str(len(unique_streams)) + " unique streams")
    print(str(time.perf_counter() - start) + " seconds")


if __name__ == "__main__":
    main()
