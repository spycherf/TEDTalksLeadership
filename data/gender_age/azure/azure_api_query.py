import csv
import json
import os
import requests
from requests.exceptions import HTTPError
import sys
import time

ENDPOINT = os.environ["AZURE_ENDPOINT"]
KEY = os.environ["AZURE_KEY"]


def get_gender_age(url):
    time.sleep(3.5)  # Free plan includes 20 transactions per minute, sleep 3.5 seconds to be on the safe side

    headers = {"Ocp-Apim-Subscription-Key": KEY}
    params = {
        "returnFaceId": "true",
        "returnFaceLandmarks": "false",
        "returnFaceAttributes": "age,gender"
    }

    response = requests.post(ENDPOINT, params=params, headers=headers, json={"url": url})

    if response.status_code == 403:
        raise HTTPError("403 Forbidden: monthly quota reached")

    try:
        faces = json.loads(response.text)
        print(faces)
        gender = faces[0]["faceAttributes"]["gender"]  # Assuming the first face is the right one
        age = faces[0]["faceAttributes"]["age"]  # Same assumption
    except KeyError:  # Probably occurs when going over transaction limit
        print("KeyError. Trying again...")
        time.sleep(1)
        get_gender_age(url)

    return gender, age


def gender_age_estimation(talk_id, photo_url, video_thumb_url):
    print("Requesting:", talk_id)
    gender1 = gender2 = ""
    age1 = age2 = 0

    try:
        if photo_url:
            try:
                gender1, age1 = get_gender_age(photo_url)
            except IndexError:
                print("No face identified in speaker photo")
        else:
            print("No speaker photo available")

        if video_thumb_url:
            try:
                gender2, age2 = get_gender_age(video_thumb_url)
            except IndexError:
                print("No face identified in video thumbnail")
        else:
            print("No video thumbnail available")

    except UnboundLocalError:
        print("UnboundLocalError. Trying again...")
        gender_age_estimation(talk_id, photo_url, video_thumb_url)

    est_gender = gender1 if gender1 else gender2  # Assuming gender is more likely to be accurate in photo

    if age1 > 0 and age2 > 0:
        est_age = (age1 + age2) / 2
    elif age1 > 0:
        est_age = age1
    else:
        est_age = age2

    assert est_gender and est_age != 0

    return {"id": talk_id, "est_gender": est_gender, "est_age": int(est_age)}


def query_and_update(input_file,
                     output_file,
                     success_log,
                     failure_log):

    # Get list of IDs that have already been queried and can be skipped
    with open(success_log, "r") as f:
        success = [line.strip("\n") for line in f]
    with open(failure_log, "r") as f:
        failure = [line.strip("\n") for line in f]
    to_skip = success + failure

    csv_header = ["id", "est_gender", "est_age"]

    # If output file doesn't exist, write header
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_header)
            writer.writeheader()

    # Get records
    with open(input_file, "r", encoding="utf-8") as urls_file:
        reader = csv.reader(urls_file, delimiter=",")
        next(reader)  # Skip header

        for row in reader:
            sys.stdout.flush()
            talk_id, photo_url, video_thumb_url = row

            if talk_id in to_skip:
                continue

            with open(output_file, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_header)

                try:
                    writer.writerow(gender_age_estimation(talk_id, photo_url, video_thumb_url))
                    csv_file.flush()
                    with open(success_log, "a") as f:
                        f.write(talk_id + "\n")
                except AssertionError:
                    print("Querying ID {0} failed (no face)".format(talk_id))
                    with open(failure_log, "a") as f:
                        f.write(talk_id + "\n")


def main():
    query_and_update("input/ted_talks_images_urls.csv",
                     "output/gender_age_estimates.csv",
                     "logs/successful.txt",
                     "logs/failed.txt")


if __name__ == "__main__":
    main()
