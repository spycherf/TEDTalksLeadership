import csv
import json
import os
import requests
import sys

ENDPOINT = os.environ["IBM_ENDPOINT"]
KEY = os.environ["IBM_KEY"]


def get_insights(talk_id, transcript):
    print("Requesting:", talk_id)
    key = ("apikey", KEY)
    payload = transcript.encode("utf-8")
    headers = {
        "Content-Type": "text/plain",
        "Accept-Charset": "UTF-8",
        "Accept": "application/json"
    }
    response = requests.post(ENDPOINT, auth=key, data=payload, headers=headers)
    profile = json.dumps(json.loads(response.text))  # Change to "response.text" when project is over

    return {"id": int(talk_id), "profile": profile}


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

    csv_header = ["id", "profile"]

    # If output file doesn't exist, write header
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_header)
            writer.writeheader()

    # Get records
    with open(input_file, "r", encoding="utf-8") as transcripts_file:
        reader = csv.reader(transcripts_file, delimiter=",")
        next(reader)  # Skip header

        for row in reader:
            sys.stdout.flush()
            talk_id, transcript = row

            if talk_id in to_skip:
                continue

            with open(output_file, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_header)

                try:
                    writer.writerow(get_insights(talk_id, transcript))
                    csv_file.flush()
                    with open(success_log, "a") as f:
                        f.write(talk_id + "\n")
                except KeyError as e:
                    print("Querying ID {0} failed because of {1}".format(talk_id, e))
                    with open(failure_log, "a") as f:
                        f.write(talk_id + "\n")


def main():
    query_and_update("input/transcripts.csv",
                     "output/personality_profiles_json.csv",
                     "logs/successful.txt",
                     "logs/failed.txt")


if __name__ == "__main__":
    main()
