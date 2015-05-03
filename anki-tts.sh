#!/bin/bash

# curl --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' | mplayer - -cache 1024
curl --silent --show-error --get --data-urlencode "q=$1" https://translate.google.com/translate_tts?tl=en -H 'user-agent:' | mplayer -really-quiet - -cache 1024 2> /dev/null
# flite -t $1
