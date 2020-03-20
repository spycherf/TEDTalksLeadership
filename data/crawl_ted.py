import csv
import json
import os
import random
import re
import sys
import time
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import urlopen


def wait():
    sleep_duration = random.randint(1, 60)
    print("Too many requests. Sleeping for {0} seconds...".format(sleep_duration))
    time.sleep(sleep_duration)
    print("Trying again...")


def request_html(url):
    print("Requesting:", url)
    i = 0

    while i < 100:
        sys.stdout.flush()
        time.sleep(2)
        try:
            response = urlopen(url)
            break
        except HTTPError as e:
            # Handling "too many requests" errors
            if e.code == 429:
                i += 1
                wait()
                continue
            else:
                raise
        # Handling "WinError 10054" errors
        except URLError:
            i += 1
            wait()
            continue

    src = response.read().decode("utf8", "ignore").replace("\r", " ").replace("\n", " ").replace("&amp;", "&")
    html = BeautifulSoup(src, "lxml")

    if not html:
        raise IOError("HTTP failure")

    return html


def get_transcript(url):
    transcript = ""

    try:
        html_src = request_html(url + "/transcript?language=en")
        divs = html_src.find_all("div", {"class": "Grid__cell flx-s:1 p-r:4"})
        for text in divs:
            transcript += (re.sub("\s+", " ", text.contents[1].contents[0]).strip() + " ")
    except HTTPError:
        pass

    return transcript


def get_data(url):
    html_src = request_html(url)
    scripts = html_src.find_all("script")

    # Extract full JSON
    full_JSON = None
    for script in scripts:
        if not script.getText().startswith('q("talkPage.init"'):
            continue
        match = re.search('(?<=q\(\"talkPage\.init\"\,)(\{.*\})', script.contents[0])
        full_JSON = json.loads(match.group(0))['__INITIAL_DATA__']

    # Get current talk ID
    talk_id = full_JSON["current_talk"]

    # Extract JSON for the current talk
    current_talk_JSON = None
    for talk in full_JSON["talks"]:
        if not talk["id"] == talk_id:
            continue
        else:
            current_talk_JSON = talk
            break
    assert current_talk_JSON, IOError("JSON details not found")

    # Get metadata
    talk_url = full_JSON["url"]
    main_speaker = current_talk_JSON["speaker_name"]
    title = current_talk_JSON["title"]
    full_name = full_JSON["name"]
    event = current_talk_JSON["event"]
    event_type = current_talk_JSON["video_type"]["name"]
    description = re.sub("\s+", " ", current_talk_JSON["description"])
    duration = current_talk_JSON["duration"]
    nb_languages = len(current_talk_JSON["downloads"]["languages"])
    views = current_talk_JSON["viewed_count"]

    tags = ""
    for tag in current_talk_JSON["tags"]:
        tags += (tag + ";")

    date_recorded = -1
    date_published = -1
    native_language = ""
    ext_src = ""
    ext_id = ""
    ext_duration = ""
    for player_talk in current_talk_JSON["player_talks"]:
        if player_talk["id"] == talk_id:
            date_recorded = datetime.strptime(current_talk_JSON["recorded_at"][:10], "%Y-%m-%d").date()
            date_published = datetime.fromtimestamp(player_talk["published"]).date()
            if "external" in player_talk:
                ext_src = player_talk["external"]["service"]
                ext_id = player_talk["external"]["code"]
                ext_duration = player_talk["external"]["duration"]
            if "nativeLanguage" in player_talk:
                native_language = player_talk["nativeLanguage"]
            break

    nb_comments = -1
    if full_JSON["comments"]:
        nb_comments = full_JSON["comments"]["count"]

    nb_speakers = 0
    speakers = ""
    speakers_desc = ""
    for speaker in current_talk_JSON["speakers"]:
        nb_speakers += 1
        speakers += (speaker["firstname"] + " " + speaker["lastname"] + ";")
        if speaker["description"]:
            speakers_desc += (speaker["description"] + ";")

    # Get transcript
    transcript = get_transcript(url)

    return {
        "id": int(talk_id), "url": talk_url, "main_speaker": main_speaker, "title": title, "full_name": full_name,
        "event": event, "event_type": event_type, "description": description, "tags": tags,
        "date_recorded": date_recorded, "date_published": date_published, "duration": duration,
        "native_language": native_language, "nb_languages": nb_languages, "views": views, "nb_comments": nb_comments,
        "nb_speakers": nb_speakers, "speakers": speakers, "speakers_desc": speakers_desc,
        "ext_src": ext_src, "ext_id": ext_id, "ext_duration": ext_duration,
        "transcript": transcript
    }


def crawl_and_update(output_file,
                     success_log,
                     failure_log):
    csv_header = [
        "id", "url", "main_speaker", "title", "full_name",
        "event", "event_type", "description", "tags",
        "date_recorded", "date_published", "duration",
        "native_language", "nb_languages", "views", "nb_comments",
        "nb_speakers", "speakers", "speakers_desc",
        "ext_src", "ext_id", "ext_duration",
        "transcript"
    ]

    # Get list of IDs that have already been crawled and can be skipped
    with open(success_log, "r") as f:
        success = [int(talk_id) for talk_id in f]
    with open(failure_log, "r") as f:
        failure = [int(talk_id) for talk_id in f]
    to_skip = success + failure

    # If crawling for the first time, write header
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()

    # Update records
    with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_header)
        for i in range(1, 61000):  # approximation of total IDs (March 2020)
            sys.stdout.flush()
            if i in to_skip:
                continue
            url = "https://www.ted.com/talks/" + str(i)
            try:
                writer.writerow(get_data(url))
                csvfile.flush()
                with open(success_log, "a") as f:
                    f.write(str(i) + "\n")
            except Exception as e:
                print("Crawling ID {0} failed because of {1}".format(i, e))
                with open(failure_log, "a") as f:
                    f.write(str(i) + "\n")


def main():
    crawl_and_update("ted/ted_talks_TED_metadata_transcripts.csv",
                     "ted/successful.txt",
                     "ted/failed.txt")


if __name__ == "__main__":
    main()
