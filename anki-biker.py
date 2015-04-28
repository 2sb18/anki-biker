# idea from stackoverflow 279237
import os, sys, inspect
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

# for input to raspberry pi
# if we aren't using the raspberry (ie we are developing or debugging), this
# module shouldn't exist
try:
    import pifacedigitalio
    pifacedigital = pifacedigitalio.PiFaceDigital()
    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    def print_input(event):
        print(event.pin_num + 1)
    listener.register(0,pifacedigitalio.IODIR_FALLING_EDGE, print_input)
    listener.activate()
    raspberry = True
except ImportError:
    raspberry = False

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
    # in the case of clozes?
    ('[...]', 'what'),
    (';', 'semicolon'),
    ('{', 'open curly bracket'),
    ('}', 'close curly bracket'),
    ('[', 'open square bracket'),
    (']', 'close square bracket')
    ])

cmd_folder = "/usr/share/anki"
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import anki
import anki.sync

# the collection should be in the current directory
collection = anki.Collection(config['collection_filename'], log=True)

currentCard = 0

currentVolume = 80

# state can be "idle", "asked_question", "said_answer"
state = "idle"

# set the volume to 80 percent
# proc = subprocess.Popen(

# there's a method in decks called select
# that allows you to select a deck.
# currentDeck

# returns true if we could get a card, false if
# not
def getCard():
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

def tts(text):
    print "saying: " + text
    subprocess.call(["flite", "-t", text])
    print "done tts"

# make it so text is readable by flite
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
    return text

def sync():
    # saying "sinking" cause it sounds better
    tts("sinking")
    try:
        remoteServer = anki.sync.RemoteServer(None)
        # create the hostkey
        hostkey = remoteServer.hostKey(config['username'], config['password'])
        if not hostkey:
            tts("badAuth");
        syncer = anki.sync.Syncer(collection, remoteServer)
        # this is causing a problem
        syncResult = syncer.sync()
        if syncResult == "fullSync":
            tts("schemas differ. need to download. downloading...")
            fullSyncer = anki.sync.FullSyncer(collection, hostkey, None)
            fullSyncer.download()
            tts("collection downloaded from remote server")
        else:
            tts(syncer.sync())
    except Exception, e:
        log = traceback.format_exc()
        err = repr(str(e))
        if ( "Unable to find the server" in err or
                "Errno 2" in err):
            tss("offline");
        print(log);
        print sys.exc_info()
        tts(str(sys.exc_info()[0]))
        tts("There are {} cards in your collection".format(collection.cardCount()))


def getInput():
    return raw_input()

def getCardAndAsk():
    global state
    if getCard():
        tts(cleanCard(currentCard.q()))
    else:
        tts("can't get another card")
    state = "asked_question"


# try syncing on startup
sync()

#get new card and ask it
getCardAndAsk()

while(1):
    input = getInput()
    try:
        input = int(input)
        if input >= 1 and input <= 4:
            # answer question
            collection.sched.answerCard(currentCard,input)
            collection.save()
            # !!! change to "answering input"
            tts(str(input))
            # get new card and ask it
            getCardAndAsk()
        elif input == 5:
            # get new card and ask it
            getCardAndAsk()
        elif input == 6:
            # repeat question
            if currentCard:
                tts(cleanCard(currentCard.q()))
                state = "asked_question"
            else:
                tts("no question to repeat")
        elif input == 7:
            # repeat answer
            if currentCard:
                tts(cleanCard(currentCard.a()))
                state = "said_answer"
            else:
                tts("no answer to repeat")
        elif input == 8:
            if currentCard:
                # !!! at some point we just want to suspend
                # mark and bury card
                tts("mark and bury")
                # mark
                collection.markReview(currentCard)
                # buryCards in sched.py 
                collection.sched.buryNote(currentCard.nid)
                getCardAndAsk()
            else:
                tts("no card to bury")
        elif input == 9:
            tts("help")
            tts("1 to 4: select ease.")
            tts("5: get new card.")
            tts("6: repeat question.")
            tts("7: repeat answer.")
            tts("8: mark and bury.")
            tts("9: menu you dummy.")
            tts("0: sync")
        elif input == 0:
            sync()
    except ValueError:
        # input is not a number
        # state can be "idle", "asked_question", "said_answer"
        if input == '':
            print state
            if state == "asked_question":
                # going to say answer
                if currentCard:
                    tts(cleanCard(currentCard.a()))
                    # !!! don't know why this isn't sticking!
                    state = "said_answer"
                else:
                    tts("no answer to repeat")
            elif state == "said_answer":
                # going to answer three
                collection.sched.answerCard(currentCard,3)
                collection.save()
                tts("answering 3")
                # get new card and ask it
                getCardAndAsk()
        else:
            tts("Unrecognized thing entered")
