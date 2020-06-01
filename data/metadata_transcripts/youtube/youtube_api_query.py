import csv
from datetime import datetime
import os
import re
import sys
from urllib.error import HTTPError

from googleapiclient.discovery import build

from TEDTalksLeadership.lib.custom.request import request_html

KEY = os.environ["YOUTUBE_API_KEY"]
youtube = build("youtube", "v3", developerKey=KEY)


def get_transcript(video_id):
    """
    This function is not needed anymore because transcripts are now retrieved
    using the youtube_transcript_api library (see youtube_transcripts.py script).
    However, we keep it here in case the aforementioned library stops working
    (based on the YouTube web-client, an undocumented part of the YouTube API).
    """
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
    # transcript = ""
    # captions_available = video["contentDetails"]["caption"]
    # if captions_available == "true":
    #     transcript = get_transcript(video_id)

    return {
        "id": video_id, "channel": channel, "title": title,
        "description": description, "tags": tags, "date_published": date_published,
        "views": views, "likes": likes, "dislikes": dislikes, "nb_comments": nb_comments,
        # "transcript": transcript
    }


def query_and_update(input_file,
                     output_file,
                     success_log,
                     failure_log):

    # Get list of YouTube IDs
    with open(input_file, "r") as f:
        ids = [line.strip("\n") for line in f]

    # Get list of IDs that have already been queried and can be skipped
    with open(success_log, "r") as f:
        success = [line.strip("\n") for line in f]
    with open(failure_log, "r") as f:
        failure = [line.strip("\n") for line in f]
    to_skip = success + failure

    csv_header = [
        "id", "channel", "title",
        "description", "tags", "date_published",
        "views", "likes", "dislikes", "nb_comments",
        # "transcript"
    ]

    # If output file doesn't exist, write header
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_header)
            writer.writeheader()

    # Get records
    with open(output_file, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_header)

        for video_id in ids:
            sys.stdout.flush()

            if video_id in to_skip:
                continue

            try:
                # This request has a API quota cost of 7 units
                writer.writerow(get_video_metadata(video_id, "id, snippet, contentDetails, statistics"))
                csv_file.flush()
                with open(success_log, "a") as f:
                    f.write(video_id + "\n")
            except IndexError as e:
                print("Querying ID {0} failed because of {1}".format(video_id, e))
                with open(failure_log, "a") as f:
                    f.write(video_id + "\n")


def main():
    query_and_update("input/youtube_ids.txt",
                     "output/ted_talks_YT_metadata_transcript.csv",
                     "logs/metadata_successful.txt",
                     "logs/metadata_failed.txt")


if __name__ == "__main__":
    main()
