import csv
import os
import pickle
import sys

import numpy as np
import python_speech_features as mfcc
from scipy.io.wavfile import read
from sklearn import preprocessing
import youtube_dl
from youtube_dl.utils import DownloadError


def get_MFCC(sr,audio):
    features = mfcc.mfcc(audio, sr, 0.025, 0.01, 13, appendEnergy=False)
    feat = np.asarray(())

    for i in range(features.shape[0]):
        temp = features[i, :]
        if np.isnan(np.min(temp)):
            continue
        else:
            if feat.size == 0:
                feat = temp
            else:
                feat = np.vstack((feat, temp))

    features = preprocessing.scale(feat)

    return features


def yt_download_audio(yt_id):
    ydl_opts = {
        "format": "worstaudio",
        "outtmpl": "yt_file"
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["http://www.youtube.com/watch?v=" + yt_id])


def to_wav(input_file, output_file, sampling_rate, bit_rate, seek, trim):
    os.system(" ".join([
        "ffmpeg", "-loglevel panic", "-i", input_file,
        "-ar", sampling_rate, "-ac", "1", "-ab", bit_rate,
        "-ss", seek, "-t", trim,
        output_file, "-y"
    ]))


def predict_gender(talk_id, yt_id):
    print("Requesting", talk_id)

    yt_download_audio(yt_id)
    audio_input = "yt_file"
    audio_output = "audio.wav"
    to_wav(input_file=audio_input, output_file=audio_output, sampling_rate="16000", bit_rate="16", seek="0", trim="180")

    print("Predicting gender...")

    # Path to models
    base_path = os.path.dirname(__file__)
    model_path = os.path.join(base_path, "models/")

    gmm_files = [os.path.join(model_path, file_name) for file_name in os.listdir(model_path) if file_name.endswith(".gmm")]
    models = [pickle.load(open(file_name, "rb")) for file_name in gmm_files]
    genders = [file_name.split("models/")[-1].split(".gmm")[0] for file_name in gmm_files]

    sr, audio = read(audio_output)
    features = get_MFCC(sr, audio)
    log_likelihood = np.zeros(len(models))

    for i in range(len(models)):
        gmm = models[i]
        scores = np.array(gmm.score(features))
        log_likelihood[i] = scores.sum()

    winner = np.argmax(log_likelihood)
    print("\tPredicted gender:", genders[winner])
    print("\tScores: female", log_likelihood[0], "male", log_likelihood[1])

    os.remove(audio_input)
    os.remove(audio_output)

    return {"id": talk_id, "yt_id": yt_id, "est_gender": genders[winner]}


def get_genders(input_file,
                output_file,
                success_log,
                failure_log):

    # Get list of IDs that have already been queried and can be skipped
    with open(success_log, "r") as f:
        success = [line.strip("\n") for line in f]
    with open(failure_log, "r") as f:
        failure = [line.strip("\n") for line in f]
    to_skip = success + failure

    csv_header = ["id", "yt_id", "est_gender"]

    # If output file doesn't exist, write header
    if not os.path.isfile(output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_header)
            writer.writeheader()

    with open(input_file, "r", encoding="utf-8") as ids_file:
        reader = csv.reader(ids_file, delimiter=",")
        next(reader)  # Skip header

        for row in reader:
            sys.stdout.flush()
            talk_id, yt_id = row

            if talk_id in to_skip:
                continue

            with open(output_file, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_header)

                try:
                    writer.writerow(predict_gender(talk_id, yt_id))
                    csv_file.flush()
                    with open(success_log, "a") as f:
                        f.write(talk_id + "\n")
                except DownloadError as e:
                    print("Querying ID {0} failed because of {1}".format(talk_id, e))
                    with open(failure_log, "a") as f:
                        f.write(talk_id + "\n")


def main():
    get_genders("input/youtube_ids.csv",
                "output/gender_estimates.csv",
                "logs/successful.txt",
                "logs/failed.txt")


if __name__ == "__main__":
    main()
