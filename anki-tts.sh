#!/bin/bash

# $1 is the text we want to tts
# $2 is the current directory

# curl has --silent and --show-error
# mplayer has -really-quiet

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo $DIR

# make the tts directory if it doesn't exist
mkdir -p $DIR/tts

# first create the name of the file
FILE_NAME=$( md5sum <<< "$1" | cut --delimiter ' ' --fields 1-1 )

if [ ! -f $DIR/tts/$FILE_NAME.mp3 ]
then
  curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' > $DIR/tts/$FILE_NAME.mp3
fi



mplayer -really-quiet $DIR/tts/$FILE_NAME.mp3 2> /dev/null


# curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' | mplayer -really-quiet - -cache 1024 2> /dev/null
# curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' > temp.audio
# flite -t $1
