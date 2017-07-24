#!/bin/bash

# usage: ./download-tts.sh "Text that you want to turn into tts mp3 file"
#
# Script uses IBM Watson to turn text into speech, in the form of an mp3 file
# File is saved to tts/ directory with teh md5 hash as the root name and .mp3 as the extension

# if file already exists, we check that the file is an mp3. if it is, we exit. if it isn't
# we delete it and download. Then check to make sure file is an mp3. If it isn't we return an error.

DIR="$( cd "$( dirname "$0" )" && pwd )"

# still need to make this quit the script if it fails
USERNAME=$( jq --raw-output '.username' $DIR/credentials.json )
PASSWORD=$( jq --raw-output '.password' $DIR/credentials.json )

# make the tts directory if it doesn't exist
mkdir -p $DIR/tts

FILE_NAME=$( echo $1 | md5sum | cut --delimiter ' ' --fields 1-1 )

# if file already exists, we check that it's an mp3. if it is, we exit, if it isn't, we download.
if [ -e $DIR/tts/$FILE_NAME.mp3 ]; then
  if [ $(file $DIR/tts/$FILE_NAME.mp3 | grep -c MPEG) == 1 ]; then
    echo -e $FILE_NAME.mp3 "already exists. no need to download.\n"
    exit 0
  else
    echo -e $FILE_NAME.mp3 "already exists but isn't an mp3, deleting...\n"
    rm $DIR/tts/$FILE_NAME.mp3
  fi
fi

# turn newlines into spaces
TEXT=$(echo $1 | tr --squeeze-repeats '\n' ' ')
curl -X POST -u "$USERNAME:$PASSWORD" --header "Content-Type: application/json" --header "Accept: audio/mp3" --header "X-Watson-Learning-Opt-Out: true" --data "{\"text\":\"$TEXT\"}" --output $DIR/tts/$FILE_NAME.mp3 "https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize?voice=en-GB_KateVoice"

echo -e "Text to download:" "$1"
echo "Done downloading" $FILE_NAME.mp3

# if the file size is 0 we got a problem
if [ ! -s $DIR/tts/$FILE_NAME.mp3 ]; then
  echo "File size is zero. We have a problem!"
  exit 5
fi
