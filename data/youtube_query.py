import csv
import os
import re
import sys
from ted_scraper import request_html
from datetime import datetime
from googleapiclient.discovery import build
from secret import youtube_api_key
from urllib.error import HTTPError

youtube = build("youtube", "v3", developerKey=youtube_api_key)


def get_transcript(video_id):
    transcript = ""

    try:
        html_src = request_html("http://video.google.com/timedtext?lang=en&v=" + video_id)
        for text in html_src.find_all("text"):
            if text.contents:
                transcript += (re.sub("\s+", " ", text.contents[0].strip() + " "))
    except HTTPError:
        pass

    return transcript


def get_video_metadata(video_id, parts):
    print("Requesting:", video_id)
    request = youtube.videos().list(id=video_id, part=parts)
    response = request.execute()
    video = response.get("items", [])[0]

    channel = video["snippet"]["channelTitle"]
    title = video["snippet"]["title"]
    description = re.sub("\s+", " ", video["snippet"]["description"])

    tags = ""
    if "tags" in video["snippet"]:
        for tag in video["snippet"]["tags"]:
            tags += (re.sub("\s+", " ", tag) + ";")

    date_published = datetime.strptime(video["snippet"]["publishedAt"][:10], "%Y-%m-%d").date()
    views = video["statistics"]["viewCount"]

    likes = 0
    dislikes = 0
    if "likeCount" in ["statistics"]:
        likes = video["statistics"]["likeCount"]
    if "dislikeCount" in ["statistics"]:
        dislikes = video["statistics"]["dislikeCount"]

    nb_comments = ""
    if "commentCount" in video["statistics"]:
        nb_comments = video["statistics"]["commentCount"]

    # Get transcript
    transcript = ""
    captions_available = video["contentDetails"]["caption"]
    if captions_available == "true":
        transcript = get_transcript(video_id)

    return {
        "id": video_id, "channel": channel, "title": title,
        "description": description, "tags": tags, "date_published": date_published,
        "views": views, "likes": likes, "dislikes": dislikes, "nb_comments": nb_comments,
        "transcript": transcript
    }


def query_and_update(ids_file,
                     output_file,
                     success_log,
                     failure_log):
    csv_header = [
        "id", "channel", "title",
        "description", "tags", "date_published",
        "views", "likes", "dislikes", "nb_comments",
        "transcript"
    ]

    # Get list of IDs
    with open(ids_file, "r") as f:
        ids = [line.strip("\n") for line in f]

    # Get list of IDs that have already been queried and can be skipped
    with open(success_log, "r") as f:
        success = [line.strip("\n") for line in f]
    with open(failure_log, "r") as f:
        failure = [line.strip("\n") for line in f]
    to_skip = success + failure

    # If output file doesn't exist, write header
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()

    # Update records
    with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_header)
        for video_id in ids:
            sys.stdout.flush()
            if video_id in to_skip:
                continue
            try:
                writer.writerow(get_video_metadata(video_id, "id, snippet, contentDetails, statistics"))
                csvfile.flush()
                with open(success_log, "a") as f:
                    f.write(video_id + "\n")
            except IndexError as e:
                print("Querying ID {0} failed because of {1}".format(video_id, e))
                with open(failure_log, "a") as f:
                    f.write(video_id + "S\n")


def main():
    query_and_update("youtube/youtube_ids.txt",
                     "youtube/ted_talks_YT_metadata_transcript.csv",
                     "youtube/successful.txt",
                     "youtube/failed.txt")


if __name__ == "__main__":
    main()
