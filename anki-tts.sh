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

# the argument is the file_name
play_audio() {
  # if the size of the file is 0, that's a problem
  if [ ! -s $DIR/tts/$1.mp3 ]
  then
    flite -t "can't find audio file"
    echo "can't find audio file"
  else
    mplayer -really-quiet $DIR/tts/$1.mp3 2> /dev/null
  fi
}

TEXT_LEFT=$1

# turn newlines into spaces
TEXT_LEFT=$(echo $TEXT_LEFT | tr --squeeze-repeats '\n' ' ')

while [ ${#TEXT_LEFT} -gt 1 ]
do
  # echo "TEXT_LEFT is starting off at size" ${#TEXT_LEFT}
  TEXT_TAKEN=$( echo $TEXT_LEFT | grep -Po '^.{0,'$MAX_LENGTH'}(\s|$)' )
  # echo "SIZE OF TEXT_TAKEN is" ${#TEXT_TAKEN}
  SIZE=${#TEXT_TAKEN}
  TEXT_LEFT=${TEXT_LEFT:SIZE}
  create_file_name "$TEXT_TAKEN"
  play_audio $FILE_NAME
  echo "Text to say:" $TEXT_TAKEN
  echo "filename:" $FILE_NAME
  echo ""
done







# curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' | mplayer -really-quiet - -cache 1024 2> /dev/null
# curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' > temp.audio
# flite -t $1
