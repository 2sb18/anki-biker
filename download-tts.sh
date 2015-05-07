#!/bin/bash

# takes in a text, outputs lines that no longer than $MAX_LENGTH.
# takes in a text, cuts it into lines that are no longer than $MAX_LENGTH.
# cuts lines off at spaces
# for each line, downloads an mp3 from google translate. then creates a hash
# of the line and stores the file at "hash".mp3

MAX_LENGTH=90

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# make the tts directory if it doesn't exist
mkdir -p $DIR/tts

create_file_name() {
  FILE_NAME=$( md5sum <<< "$1" | cut --delimiter ' ' --fields 1-1 )
}

# first argument is the text, second argument is the file_name
curl_thing () {
    curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' > $DIR/tts/$2.mp3
    echo "done download"
}

# uses the FILE_NAME variable created in this script
# the argument is the text to be downloaded
download_if_missing() {
  if [ ! -s $DIR/tts/$FILE_NAME.mp3 ]
  then
    echo "downloading tts file" $FILE_NAME
    curl_thing "$1" $FILE_NAME
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
  download_if_missing "$TEXT_TAKEN"
  echo "Text to download:" $TEXT_TAKEN
  echo "filename:" $FILE_NAME
  echo ""
done










