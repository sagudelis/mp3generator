# pulls a bunch of YouTube links and converts to MP3
import os.path

from pytube import YouTube
import ffmpeg
import ffprobe
import eyed3
import pydub
# import os
import subprocess
import time
from pydub.audio_segment import AudioSegment
import tkinter as tk
from tkinter import filedialog
import sys
import music_tag

sys.path.append('/path/to/ffmpeg')
pydub.AudioSegment.ffmpeg = "/absolute/path/to/ffmpeg"


# user set vars
dataFile = "youtubeLinks.csv"

# arrays to be used
linkList = []
artistName = []
albumName = []
songTitle = []
trackNum = []
startTime = []
endTime = []

# initialize and close the window
root = tk.Tk()
root.withdraw()

# prompt the user to choose a directory
path = filedialog.askdirectory()
# folderName = path[path.rfind('/') + 1:len(path)] + '-mp3-Files'
destination = path
os.makedirs(destination, exist_ok=True)

# destroy the window
root.destroy()

# get data from data file
alldata = open(dataFile, 'r')
thisdata = alldata.readlines()
alldata.close()
thisdata.pop(0)     # remove the first line

# parse data
#   link, artist name, album name, title, start time, end time
for line in thisdata:
    rowarray = line.split(",")

    # append to the arrays
    linkList.append(rowarray[0])
    artistName.append(rowarray[1])
    albumName.append(rowarray[2])
    songTitle.append(rowarray[3])
    trackNum.append(rowarray[4])
    startTime.append(rowarray[5])
    endTime.append(rowarray[6])

# for each video, get the whole video and save to mp3
for idx, videoLink in enumerate(linkList):
    if videoLink != 'skip':
        print(videoLink)
        yt = YouTube(videoLink, use_oauth=True)
        video = yt.streams.filter(only_audio=True).first()

        # download the file
        new_file = songTitle[idx] + '.mp3'
        out_file = video.download(output_path=destination, filename=new_file)

        # trim the file to the desired start and end times
        # get start and end time and parse
        print(f'start time = {startTime[idx]}, end time = {endTime[idx]}')
        startMin, startSec = startTime[idx].split(":")
        endMin, endSec = endTime[idx].split(":")
        # convert to MS
        startTimeMS = int(startMin)*60*1000+int(startSec)*1000
        endTimeMS = int(endMin)*60*1000+int(endSec)*1000
        # open file and extract segment
        print(new_file)
        song = AudioSegment.from_file(new_file)
        extract = song[startTimeMS:endTimeMS]
        # save
        extract.export(new_file, format="mp3")

        # change the metadata for artist, album, title, etc.
        audiofile = eyed3.load(new_file)
        audiofile.initTag()
        audiofile.tag.artist = artistName[idx]
        audiofile.tag.album = albumName[idx]
        audiofile.tag.album_artist = artistName[idx]
        audiofile.tag.title = songTitle[idx]
        audiofile.tag.track_num = trackNum[idx]
        audiofile.tag.save(new_file)
