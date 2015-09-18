#!/bin/bash

# usage: ./download-tts.sh "Text that you want to turn into tts mp3 file"
#
# Script uses Google Translate to turn text into speech, in the form of an mp3 file
# File is saved to tts/ directory with the md5 hash as the root name and .mp3 as the extension
#
# Because of a Google Translate limitation, text has to be chopped up into 90 character sections
# Then we concatenate the sections into one mp3

# if file already exists, we check that the file is an mp3. if it is, we exit. if it isn't
# we delete it and download. Then check to make sure file is an mp3. If it isn't we return an error.

SECTION_LENGTH=90
MAX_LENGTH=300

DIR="$( cd "$( dirname "$0" )" && pwd )"

# make the tts directory if it doesn't exist
mkdir -p $DIR/tts

FILE_NAME=$( echo $1 | md5sum | cut --delimiter ' ' --fields 1-1 )

# if file already exists, we check that it's an mp3. if it is, we exit, if it isn't, we download.
if [ -e $DIR/tts/$FILE_NAME.mp3 ]; then
  if [ $(file $DIR/tts/$FILE_NAME.mp3 | grep -c MPEG) == 1 ]; then
    # echo -e $FILE_NAME.mp3 "already exists. no need to download.\n"
    exit 0
  else
    echo -e $FILE_NAME.mp3 "already exists but isn't an mp3, deleting...\n"
    rm $DIR/tts/$FILE_NAME.mp3
  fi
fi

# turn newlines into spaces
TEXT_LEFT=$(echo $1 | tr --squeeze-repeats '\n' ' ')

if [ ${#TEXT_LEFT} -gt $MAX_LENGTH ]; then
  echo -e "Text to download:" "$1"
  echo -e "text is too long. not downloading\n\n"
  exit 1
fi

while [ ${#TEXT_LEFT} -gt 1 ]; do
  TEXT_TAKEN=$( echo $TEXT_LEFT | grep -Po '^.{0,'$SECTION_LENGTH'}(\s|$)' )
  # echo "SIZE OF TEXT_TAKEN is" ${#TEXT_TAKEN}
  SIZE=${#TEXT_TAKEN}
  # this is ${parameter:offset}. 
  TEXT_LEFT=${TEXT_LEFT:SIZE}
  # the >> appends the mp3 onto the end 
  # to figure out the curl to send, use chrome to look at the network activity while playing
  # a tts, then copy the request url to see what's needed
  # google translate seems to need some kind of user-agent now
  curl 'https://translate.google.com/translate_tts?tl=en&client=t' --silent --show-error --get --header 'user-agent:meow' --data-urlencode "q=$TEXT_TAKEN" > temp.mp3
  # check to make sure temp.mp3 is really an mp3
  if [ $(file temp.mp3 | grep -c MPEG) != 1 ]; then
    echo "Problem with Google translate. Probably have to change the curl command"
    exit 1
  fi
  cat temp.mp3 >> $DIR/tts/$FILE_NAME.mp3
done

echo -e "Text to download:" "$1"
echo "Done downloading" $FILE_NAME.mp3

# if the file size is 0 we got a problem
if [ ! -s $DIR/tts/$FILE_NAME.mp3 ]; then
  echo "File size is zero. We have a problem!"
  exit 1
fi
