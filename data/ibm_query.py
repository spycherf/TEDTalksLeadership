import csv
import json
import os
import requests
import sys
from secret import ibm_api_url, ibm_api_key


def get_insights(talk_id, transcript):
    print("Requesting:", talk_id)
    key = ("apikey", ibm_api_key)
    payload = transcript.encode("utf-8")
    headers = {
        "Content-Type": "text/plain",
        "Accept-Charset": "UTF-8",
        "Accept": "application/json"
    }
    response = requests.post(ibm_api_url, auth=key, data=payload, headers=headers)
    profile = json.loads(response.text)

    return {"id": int(talk_id), "personality_profile": profile}


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

    csv_header = ["id", "personality_profile"]

    # If output file doesn't exist, write header
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_header)
            writer.writeheader()

    # Update records
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
    query_and_update("ibm/transcripts.csv",
                     "ibm/personality_profiles.csv",
                     "ibm/successful.txt",
                     "ibm/failed.txt")


if __name__ == "__main__":
    main()
