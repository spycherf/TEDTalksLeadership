from __future__ import unicode_literals
import youtube_dl


ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "wav",
        "preferredquality": "192"
    }]
}

yt_id = "FOZ6KnVPvIU"
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(["http://www.youtube.com/watch?v=" + yt_id])



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
