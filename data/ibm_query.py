import csv
import json
import requests
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

    return requests.post(ibm_api_url, auth=key, data=payload, headers=headers)


def query_and_update(input_file,
                     output_file,
                     success_log):

    # Get list of IDs that have already been queried and can be skipped
    with open(success_log, "r") as f:
        to_skip = [line.strip("\n") for line in f]

    # Update records
    with open(input_file, "r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader)  # Skip header
        for row in reader:
            talk_id, transcript = row
            if talk_id in to_skip:
                continue
            insights = json.loads(get_insights(talk_id, transcript).text)
            with open(output_file, "r+", encoding="utf-8") as json_file:  # Have to rewrite the whole file each time...
                file_contents = json.load(json_file)
                record = {"id": int(talk_id), "personality_insights": insights}
                file_contents.append(record)
                json_file.seek(0)
                json.dump(file_contents, json_file, indent=2)
                with open(success_log, "a") as f:
                    f.write(talk_id + "\n")


def main():
    query_and_update("ibm/transcripts.csv",
                     "ibm/personality_insights.json",
                     "ibm/successful.txt")


if __name__ == "__main__":
    main()
