import csv
import json
import os
import random
import re
import sys
import time
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


def http_request(url):
    print("Requesting: ", url)
    sys.stdout.flush()

    i = 0
    while i < 100:
        time.sleep(2)
        try:
            response = urlopen(url)
            break
        except HTTPError as e:
            if e.code == 429:
                i += 1
                print("Call no. {0}, HTTP Error {1}: {2}".format(i, e.code, e.msg))
                s = random.randint(1, 60)
                print("Sleeping for {0} seconds".format(s))
                time.sleep(s)
                print("Trying again...")
                sys.stdout.flush()
                continue
            else:
                raise

    src = response.read().decode("utf8", "ignore").replace("\r", " ").replace("\n", " ")
    html = BeautifulSoup(src, 'lxml')

    if not html:
        raise IOError("HTTP failure")

    return html


def get_transcript(url):
    transcript = ""
    html_src = http_request(url + "/transcript?language=en")
    divs = html_src.find_all("div", {"class": "Grid__cell flx-s:1 p-r:4"})  # class value might change with time

    for text in divs:
        transcript += (re.sub("\s+", " ", text.contents[1].contents[0]).strip() + " ")

    if not transcript:
        raise IOError("Empty transcript")

    return transcript


def get_metadata(url):
    html_src = http_request(url)
    scripts = html_src.find_all("script")

    # Extract full JSON
    full_JSON = None
    for script in scripts:
        if not script.getText().startswith('q("talkPage.init"'):
            continue
        match = re.search('(?<=q\(\"talkPage\.init\"\,)(\{.*\})', script.contents[0])
        full_JSON = json.loads(match.group(0))['__INITIAL_DATA__']

    talk_id = full_JSON['current_talk']

    # Extract JSON for the current talk
    current_talk_JSON = None
    for talk in full_JSON['talks']:
        if not talk["id"] == talk_id:
            continue
        else:
            current_talk_JSON = talk
            break
    assert current_talk_JSON, IOError("JSON details not found")

    # Dates
    date_published = 0
    date_filmed = 0
    for player_talk in current_talk_JSON["player_talks"]:
        if player_talk["id"] == talk_id:
            date_published = player_talk["published"]
            date_filmed = player_talk["published"]
            break

    # Comments
    nb_comments = 0
    if full_JSON["comments"]:
        nb_comments = full_JSON["comments"]["count"]

    # Speakers
    nb_speakers = 0
    speakers = ""
    speakers_desc = ""
    for speaker in current_talk_JSON["speakers"]:
        nb_speakers += 1
        speakers += (speaker["firstname"] + " " + speaker["lastname"] + ";")
        if speaker["description"]:
            speakers_desc += (speaker["description"] + ";")

    # Other metadata
    talk_url = full_JSON["url"]
    main_speaker = current_talk_JSON["speaker_name"]
    title = current_talk_JSON["title"]
    event = current_talk_JSON["event"]
    event_type = current_talk_JSON["video_type"]["name"]
    description = current_talk_JSON["description"]
    tags = current_talk_JSON["tags"]
    duration = current_talk_JSON["duration"]
    nb_languages = len(current_talk_JSON["downloads"]["languages"])
    views = current_talk_JSON["viewed_count"]
    transcript = get_transcript(url)

    return {
        "id": talk_id, "url": talk_url, "main_speaker": main_speaker, "title": title,
        "event": event, "event_type": event_type, "description": description, "tags": tags,
        "date_filmed": date_filmed, "date_published": date_published, "duration": duration,
        "nb_languages": nb_languages, "views": views, "nb_comments": nb_comments,
        "nb_speakers": nb_speakers, "speakers": speakers, "speakers_desc": speakers_desc,
        "transcript": transcript
    }


def crawl_and_update(output_file):
    csv_header = [
        "id", "url", "main_speaker", "title",
        "event", "event_type", "description", "tags",
        "date_filmed", "date_published", "duration",
        "nb_languages", "views", "nb_comments",
        "nb_speakers", "speakers", "speakers_desc",
        "transcript"
    ]

    # Get list of IDs that have already been crawled
    with open("to_skip.txt", "r") as f:
        to_skip = [int(id) for id in f]

    # Write header for the first crawl
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()

    with open(output_file, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_header)
        for i in range(1, 61000):
            if i in to_skip:
                continue
            url = "https://www.ted.com/talks/" + str(i)
            try:
                writer.writerow(get_metadata(url))
            except Exception as e:
                print("Crawling {0} failed because of {1}".format(i, e))
                continue

            with open("to_skip.txt", "a") as f:
                f.write(str(i) + "\n")


crawl_and_update("ted_talks_metadata_transcripts.csv")
