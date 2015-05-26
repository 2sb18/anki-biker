#!/usr/bin/python

# idea from stackoverflow 279237
import os, inspect, time
# regex functions
import re
# tts support
import subprocess

import string

# for import of config
import json

# for exiting from script prematurely
import sys

# for debugging
import pdb
import traceback

config_file = os.path.dirname(os.path.realpath(__file__)) + '/config.json'
ankitts_file = os.path.dirname(os.path.realpath(__file__)) + '/anki-tts.sh'
downloadtts_file = os.path.dirname(os.path.realpath(__file__)) + '/download-tts.sh'

try:
    config = json.load(open(config_file))
except IOError:
    sys.exit('config.json file missing. run "python create-config.py" to create one.')

try:
    subprocess.Popen( 'html2text', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
except OSError:
    sys.exit("looks like you need to install html2text. run 'sudo apt-get install html2text'")


cmd_folder = "/usr/share/anki"
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import anki
import anki.sync

# the collection should be in the current directory
collection_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + config['collection_filename']
collection = anki.Collection(collection_filename, log=True)

def tts(text):
    global ankitts_file
    print "saying: " + text
    # subprocess.call(['flite', '-t', text])
    # subprocess.call(['anki-tts.sh', text])
    subprocess.call([ankitts_file, text ])
    # print "done tts"

def crap_tts(text):
    print "saying this crappily: " + text
    subprocess.call(['flite', '-t', text])

# make it so text is readable by tts
def cleanCard(text):
    # return re.sub( r'<style>.*</style>', r'', text, flags=re.DOTALL)

    # if it's an answer, there's going to be an <hr id=answer> remove
    # everything up to it
    text = re.sub ( r'^.*<hr id=answer>', '', text, flags=re.DOTALL)

    # if it's a cloze answer, remove everything except the cloze
    if re.search( '<span class=cloze>', text ) != None and re.search ( '<span class=cloze>\[\.\.\.]</span>', text ) == None:
        text = re.findall( r'<span class=cloze>.*</span>', text )[0]

    # using html2text
    proc = subprocess.Popen(
        'html2text', stdout=subprocess.PIPE,
        stdin=subprocess.PIPE)
    proc.stdin.write(text)
    proc.stdin.close()
    text = proc.stdout.read()
    proc.wait()
    # replace various symbols with words
    for k, v in textReplacements.iteritems():
        # put spaces around the values
        text = string.replace(text, k, ' ' + v + ' ')
    return text.rstrip()

def sync():
    crap_tts("syncing")
    try:
        remoteServer = anki.sync.RemoteServer(None)
        # create the hostkey
        hostkey = remoteServer.hostKey(config['username'], config['password'])
        # if not hostkey:
        #     crap_tts("Bad Authorization");
        syncer = anki.sync.Syncer(collection, remoteServer)
        syncResult = syncer.sync()
        if syncResult == "fullSync":
            crap_tts("schemas differ. need to download. downloading...")
            fullSyncer = anki.sync.FullSyncer(collection, hostkey, None)
            fullSyncer.download()
            crap_tts("collection downloaded from remote server")
        else:
            crap_tts(syncer.sync())
    except Exception, e:
        crap_tts ( "Can't sync" )
        err = repr(str(e))
        if ( "501" in err ):
            crap_tts("You need to update Anki, your version is too old.")
        elif ( "Unable to find the server" in err or
                "Errno 2" in err):
            crap_tts("You need to be hooked up to the Internet to sync");
        else:
          log = traceback.format_exc()
          print(log);
          print sys.exc_info()
          crap_tts(str(sys.exc_info()[0]))


textReplacements = dict([
    ('>', 'greater than'),
    ('<', 'less than'),
    ('$', 'dollar sign'),
    ('-', 'dash'),
    ('ctrl-', 'control'),
    ('|', 'pipe'),
    (':', 'colon'),
    (';', 'semicolon'),
    ('!', 'bang'),
    ('`', 'backtick'),
    ('*', 'asterix'),
    ('#', 'hash sign'),
    ('&', 'ampersand'),
    ('\\', 'backslash'),
    ('/', 'slash'),
    ('etc', 'et see'),
    # in the case of clozes?
    ('[...]', 'what'),
    (';', 'semicolon'),
    ('{', 'open curly bracket'),
    ('}', 'close curly bracket'),
    ('[', 'open square bracket'),
    (']', 'close square bracket'),
    ('(', 'open bracket'),
    (')', 'close bracket')
    ])
