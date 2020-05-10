from __future__ import unicode_literals
import csv
import youtube_dl
#import deepspeech
#https://www.slanglabs.in/blog/how-to-build-python-transcriber-using-mozilla-deepspeech
# https://github.com/danielmlow/deepspeech_transcription/blob/master/transcribe.py
import ffmpeg
import pitch
import os
import sys


def yt_download_audio(yt_id):
    ydl_opts = {
        "format": "worst",
        "outtmpl": "yt_file"
        # "postprocessors": [{
        #     "key": "FFmpegExtractAudio",
        #     "preferredcodec": "webm",
        #     "preferredquality": "5",
        # }]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["http://www.youtube.com/watch?v=" + yt_id])


def to_wav(input_file, output_file, sampling_rate, bit_rate):
    os.system(" ".join([
        "ffmpeg", "-i", input_file,
        "-ar", sampling_rate, "-ac", "1", "-ab", bit_rate,
        output_file, "-y"
    ]))
    os.remove(input_file)


def determine_gender(talk_id, yt_id):
    yt_download_audio(yt_id)
    file_name = "audio.wav"
    to_wav(input_file="yt_file", output_file=file_name, sampling_rate="16000", bit_rate="16")

    p = pitch.find_pitch(file_name)

    return p

def transcribe(input_file,
               output_file,
               success_log,
               failure_log):

    # Get list of IDs that have already been queried and can be skipped
    with open(success_log, "r") as f:
        success = [line.strip("\n") for line in f]
    with open(failure_log, "r") as f:
        failure = [line.strip("\n") for line in f]
    to_skip = success + failure

    csv_header = [
        "id", "yt_id", "stt_transcript"
    ]

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
            print(talk_id, yt_id)
            if talk_id in to_skip:
                continue

            with open(output_file, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_header)

                # try:
                writer.writerow(deepspeech_test(talk_id, yt_id))
                csv_file.flush()
                with open(success_log, "a") as f:
                    f.write(talk_id + "\n")
                # except Exception as e:
                #     print("Querying ID {0} failed because of {1}".format(talk_id, e))
                #     with open(failure_log, "a") as f:
                #         f.write(talk_id + "\n")


def main():
    transcribe("input/notranscript_yt_ids.csv",
               "output/YT_STT_transcripts.csv",
               "logs/successful.txt",
               "logs/failed.txt")


if __name__ == "__main__":
    # main()
    print(determine_gender(1, "rDiGYuQicpA"))  # WWuOiKMbU8A




# DeepSpeech parameters
# DEEPSPEECH_MODEL_DIR = 'deepspeech-0.6.0-models'
# MODEL_FILE_PATH = os.path.join(DEEPSPEECH_MODEL_DIR, 'output_graph.pbmm')
# BEAM_WIDTH = 500
# LM_FILE_PATH = os.path.join(DEEPSPEECH_MODEL_DIR, 'lm.binary')
# TRIE_FILE_PATH = os.path.join(DEEPSPEECH_MODEL_DIR, 'trie')
# LM_ALPHA = 0.75
# LM_BETA = 1.85

# if __name__ == "__main__":
#     # Paths
#     input_dir = config.input_dir #./data/wavs_01234/
#     wav_dir = config.wav_dir
#     model_dir = config.deepspeech_models
#     output_dir = config.output_dir
#     # Create output dir
#     mkdir(output_dir)
#     files = os.listdir(input_dir)
#     try: files.remove('.DS_Store')
#     except: pass
#     files.sort()
#     for file in files:
#         # convert to 16kHz and 16bit wav
#         converted_filename = file[:-4]+'_16khz.wav'
#         to_wav(input_dir = input_dir, filename=file, output_dir = wav_dir,output_filename=converted_filename,sampling_rate='16000', bit_rate = '16')
#
#         if config.deepspeech:
#             command = 'deepspeech --model {0}output_graph.pb --alphabet {0}alphabet.txt --lm {0}lm.binary --trie {0}trie --audio {1} >> {2}'.format(model_dir, wav_dir+converted_filename, output_dir+file[:-4]+'_deepspeech.txt')
#             os.system(command)
#         if config.google:
#             os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_credentials
#             transcript = transcribe_google(wav_dir+converted_filename)
#             with open(output_dir + file[:-4] + '_google.txt', 'a+') as f:
#                 f.write(transcript)
#     if config.remove_wav_dir:
#         os.system('rm -r '+config.wav_dir)

# from os import walk
# import os
# import sys
# try:
#         link = sys.argv[1]
# except IndexError:
#         scriptName = sys.argv[0]
#         print "Usage: python " + scriptName + " linkOfVideo"
#         exit()
# #Change this path with yours.
# #Also make sure that youtube-dl and ffmpeg installed.
# #Previous versions of youtube-dl can be slow for downloading audio. Make sure you have downloaded the latest version from webpage.
# #https://github.com/rg3/youtube-dl
# mypath = "/home/pi/fmtransmitter/FM_Transmitter_RPi3"
# os.chdir(mypath)
# os.system("youtube-dl --extract-audio " + link)
#
# vidID= link.split("=")[1]
# print "VidID = " + vidID
# f = []
# for (dirpath, dirnames, filenames) in walk(mypath):
#     f.extend(filenames)
#     break
# for i in range(0, len(f)):
#         if ".opus" in f[i] and vidID in f[i]:
#                 vidName = f[i]
#                 print vidName
#                 cmdstr = "ffmpeg -i \"" + vidName + "\" -f wav -flags bitexact \"" + vidName[:-5] + ".wav"  + "\""
#                 print cmdstr
#                 os.system(cmdstr)
#                 os.remove(vidName) #Will remove original opus file. Comment it if you want to keep that file.
