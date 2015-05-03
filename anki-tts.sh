#!/bin/bash

curl --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' | mplayer - -cache 1024
# flite -t $1
