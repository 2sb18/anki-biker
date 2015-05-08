#!/bin/bash

# $1 is the text we want to tts
# $2 is the current directory

# curl has --silent and --show-error
# mplayer has -really-quiet

DIR="$( cd "$( dirname "$0" )" && pwd )"
FILE_NAME=$( echo $1 | md5sum | cut --delimiter ' ' --fields 1-1 )

if [ ! -s $DIR/tts/$FILE_NAME.mp3 ]; then
  flite -t "can't find audio file"
  echo "can't find audio file"
  else
    mplayer -really-quiet $DIR/tts/$FILE_NAME.mp3 2> /dev/null
fi
