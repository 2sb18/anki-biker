#!/bin/bash

# $1 is the text we want to tts
# $2 is the current directory

# curl has --silent and --show-error
# mplayer has -really-quiet

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# make the tts directory if it doesn't exist
mkdir -p $DIR/tts

create_file_name() {
  FILE_NAME=$( md5sum <<< "$1" | cut --delimiter ' ' --fields 1-1 )
}

# first argument is the text, second argument is the file_name
curl_thing () {
    curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' > $DIR/tts/$2.mp3
}

# uses the FILE_NAME variable created in this script
# the argument is the text to be downloaded
download_if_missing() {
  if [ ! -s $DIR/tts/$FILE_NAME.mp3 ]
  then
    play_audio downloading
    echo "downloading tts file"
    curl_thing "$1" $FILE_NAME
  fi
}

# the argument is the file_name
play_audio() {
  # if the size of the file is 0, that's a problem
  if [ ! -s $DIR/tts/$1.mp3 ]
  then
    play_audio problem
    echo "there was a problem getting the tts file"
  else
    mplayer -really-quiet $DIR/tts/$1.mp3 2> /dev/null
  fi
}

# gotta make sure the "downloading" and "problem" audio exists
if [ ! -s $DIR/tts/downloading.mp3 -o ! -s $DIR/tts/problem.mp3 ]
then
  curl_thing downloading downloading
  curl_thing problem problem
fi

create_file_name "$1"
download_if_missing "$1"
play_audio $FILE_NAME








# curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' | mplayer -really-quiet - -cache 1024 2> /dev/null
# curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' > temp.audio
# flite -t $1
