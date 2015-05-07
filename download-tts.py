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

# for keyboard input
import select
import tty
import termios


downloadtts_file = os.path.dirname(os.path.realpath(__file__)) + '/download-tts.sh'

try:
    config = json.load(open('config.json'))
except IOError:
    sys.exit('config.json file missing. run "python create-config.py" to create one.')

try:
    subprocess.Popen( 'html2text', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
except OSError:
    sys.exit("looks like you need to install html2text. run 'sudo apt-get install html2text'")

textReplacements = dict([
    ('>', 'greater than'),
    ('>', 'less than'),
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

cmd_folder = "/usr/share/anki"
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import anki
import anki.sync

currentCard = 0

# the collection should be in the current directory
collection = anki.Collection(config['collection_filename'], log=True)

# returns true if we could get a card, false if not
def getNewCard():
    global currentCard
    # if there's an "<img" then get another card
    if collection.cardCount() == 0:
        return False
    while ( 1 ):
        # sched.getCard() is really just cards.Card(collection) 
        currentCard = collection.sched.getCard()
        if re.search('<img', currentCard.a()) == None:
            break
    return True

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
    print "syncing"
    try:
        remoteServer = anki.sync.RemoteServer(None)
        # create the hostkey
        hostkey = remoteServer.hostKey(config['username'], config['password'])
        # if not hostkey:
        #     tts("Bad Authorization");
        syncer = anki.sync.Syncer(collection, remoteServer)
        syncResult = syncer.sync()
        if syncResult == "fullSync":
            print "schemas differ. need to download. downloading..."
            fullSyncer = anki.sync.FullSyncer(collection, hostkey, None)
            fullSyncer.download()
            print "collection downloaded from remote server"
        else:
            print syncer.sync()
    except Exception, e:
        print "Can't sync" 
        err = repr(str(e))
        if ( "501" in err ):
            print "You need to update Anki, your version is too old."
        elif ( "Unable to find the server" in err or
                "Errno 2" in err):
            print "You need to be hooked up to the Internet to sync"
        else:
          log = traceback.format_exc()
          print(log);
          print sys.exc_info()
          print str(sys.exc_info()[0])

def downloadCard():
    # currentCard has the card we want to download
    subprocess.call([downloadtts_file, cleanCard(currentCard.q())])
    subprocess.call([downloadtts_file, cleanCard(currentCard.a())])
        

sync()

x = 0

currentCard = collection.sched.getCard()
while currentCard:
    print "on card " + str(x)
    downloadCard()
    x = x + 1
    currentCard = collection.sched.getCard()

print x

while 1:
    pass







