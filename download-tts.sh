#!/bin/bash

# usage: ./download-tts.sh "Text that you want to turn into tts mp3 file"
#
# Script uses Google Translate to turn text into speech, in the form of an mp3 file
# File is saved to tts/ directory with the md5 hash as the root name and .mp3 as the extension
#
# Because of a Google Translate limitation, text has to be chopped up into 90 character sections
# Then we concatenate the sections into one mp3

# if file already exists, we exit

SECTION_LENGTH=90
MAX_LENGTH=300

DIR="$( cd "$( dirname "$0" )" && pwd )"

# make the tts directory if it doesn't exist
mkdir -p $DIR/tts

FILE_NAME=$( echo $1 | md5sum | cut --delimiter ' ' --fields 1-1 )

echo -e "Text to download:" "$1"

# if file already exists, exit
if [ -e $DIR/tts/$FILE_NAME.mp3 ]; then
  echo -e $FILE_NAME.mp3 "already exists. no need to download.\n"
  exit 0
fi

# turn newlines into spaces
TEXT_LEFT=$(echo $1 | tr --squeeze-repeats '\n' ' ')

if [ ${#TEXT_LEFT} -gt $MAX_LENGTH ]; then
  echo "text is too long. not downloading"
  exit 1
fi

while [ ${#TEXT_LEFT} -gt 1 ]; do
  TEXT_TAKEN=$( echo $TEXT_LEFT | grep -Po '^.{0,'$SECTION_LENGTH'}(\s|$)' )
  # echo "SIZE OF TEXT_TAKEN is" ${#TEXT_TAKEN}
  SIZE=${#TEXT_TAKEN}
  TEXT_LEFT=${TEXT_LEFT:SIZE}
  curl --silent --show-error --get --data-urlencode "q=$TEXT_TAKEN" https://translate.google.com/translate_tts?tl=en \
    -H 'user-agent:' >> $DIR/tts/$FILE_NAME.mp3
done

echo "Done downloading" $FILE_NAME.mp3

# if the file size is 0 we got a problem
if [ ! -s $DIR/tts/$FILE_NAME.mp3 ]; then
  echo "File size is zero. We have a problem!"
  exit 1
fi


