import csv
import json
import os
import requests
import sys
import time

ENDPOINT = os.environ["AZURE_ENDPOINT"]
KEY = os.environ["AZURE_KEY"]


def get_gender_age(url):
    headers = {"Ocp-Apim-Subscription-Key": KEY}
    params = {
        "returnFaceId": "true",
        "returnFaceLandmarks": "false",
        "returnFaceAttributes": "age,gender"
    }

    time.sleep(1)

    response = requests.post(ENDPOINT, params=params, headers=headers, json={"url": url})
    faces = json.loads(response.text)

    try:
        gender = faces[0]["faceAttributes"]["gender"]  # Assuming the first face is the right one
        age = faces[0]["faceAttributes"]["age"]  # Same assumption
    except KeyError:  # Sometimes getting this error for some reason, just need to try again
        get_gender_age(url)

    return gender, age


def gender_age_estimation(talk_id, photo_url, video_thumb_url):
    print("Requesting:", talk_id)
    gender1 = gender2 = ""
    age1 = age2 = 0

    if photo_url:
        try:
            gender1, age1 = get_gender_age(photo_url)
        except IndexError:
            print("No face identified in speaker photo")

    if video_thumb_url:
        try:
            gender2, age2 = get_gender_age(video_thumb_url)
        except IndexError:
            print("No face identified in video thumbnail")

    est_gender = gender1 if gender1 else gender2  # Assuming gender is more likely to be accurate in photo

    if age1 > 0 and age2 > 0:
        est_age = (age1 + age2) / 2
    elif age1 > 0:
        est_age = age1
    else:
        est_age = age2

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

                # try:
                writer.writerow(gender_age_estimation(talk_id, photo_url, video_thumb_url))
                csv_file.flush()
                with open(success_log, "a") as f:
                    f.write(talk_id + "\n")
                # except Exception as e:
                #     print("Querying ID {0} failed because of {1}".format(talk_id, e))
                #     with open(failure_log, "a") as f:
                #         f.write(talk_id + "\n")


def main():
    query_and_update("input/ted_talks_images_FULL.csv",
                     "output/gender_age_estimates_notranscript.csv",
                     "logs/successful.txt",
                     "logs/failed.txt")


if __name__ == "__main__":
    main()
