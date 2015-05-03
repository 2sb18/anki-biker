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

ankitts_file = os.path.dirname(os.path.realpath(__file__)) + '/anki-tts.sh'

# for input to raspberry pi
# if we aren't using the raspberry (ie we are developing or debugging), this
# module shouldn't exist
try:
    import pifacedigitalio
    pifacedigital = pifacedigitalio.PiFaceDigital()
    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    def print_input(event):
        global input
        # print(event.pin_num)
        mapthing = [3,6,2,5,8,1,4,7]
        tts(str(mapthing[event.pin_num]))
        input = mapthing[event.pin_num]
        # eventHappened(mapthing[event.pin_num])
    for i in range(8):
        listener.register(i,pifacedigitalio.IODIR_FALLING_EDGE, print_input)
    listener.activate()
except ImportError:
    pass

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

input = 0



print ankitts_file

def tts(text):
    global ankitts_file
    print "saying: " + text
    # subprocess.call(['flite', '-t', text])
    # subprocess.call(['anki-tts.sh', text])
    subprocess.call([ankitts_file, text])
    print "done tts"

# set the volume to 80 percent
# proc = subprocess.Popen(

# there's a method in decks called select
# that allows you to select a deck.
# currentDeck

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
    tts("syncing")
    try:
        remoteServer = anki.sync.RemoteServer(None)
        # create the hostkey
        hostkey = remoteServer.hostKey(config['username'], config['password'])
        if not hostkey:
            tts("badAuth");
        syncer = anki.sync.Syncer(collection, remoteServer)
        syncResult = syncer.sync()
        if syncResult == "fullSync":
            tts("schemas differ. need to download. downloading...")
            fullSyncer = anki.sync.FullSyncer(collection, hostkey, None)
            fullSyncer.download()
            tts("collection downloaded from remote server")
        else:
            tts(syncer.sync())
    except Exception, e:
        tts ( "Can't sync" )
        err = repr(str(e))
        if ( "501" in err ):
            tts("You need to update Anki, your version is too old.")
        elif ( "Unable to find the server" in err or
                "Errno 2" in err):
            tts("You need to be hooked up to the Internet to sync");
        else:
          log = traceback.format_exc()
          print(log);
          print sys.exc_info()
          tts(str(sys.exc_info()[0]))

def getInput():
    return raw_input()

def getNewCardAndAsk():
    global state
    if getNewCard():
        tts(cleanCard(currentCard.q()))
    else:
        tts("can't get another card")
    state = "asked_question"

def repeatQuestion():
    if currentCard:
        tts(cleanCard(currentCard.q()))
        state = "asked_question"
    else:
        tts("no question to repeat")

def repeatAnswer():
    # repeat answer
    if currentCard:
        tts(cleanCard(currentCard.a()))
        state = "said_answer"
    else:
        tts("no answer to repeat")

def markAndBuryCard():
    if currentCard:
        collection.markReview(currentCard)
        collection.sched.buryNote(currentCard.nid)
        tts("mark and bury")
    else:
        tts("no card to bury")


def answerQuestion(input):
    # answer question
    collection.sched.answerCard(currentCard,input)
    collection.save()
    tts(str(input))




# try syncing on startup
sync()

try:
    tts("There are {} cards in your collection".format(collection.cardCount()))
except:
    pass

#get new card and ask it
getNewCardAndAsk()

# right hand answers the questions
# index go forward (answer 3
# middle
# ring
# pinky
# 
# pinky 1, ring 2, middle 3, index 4
#
# left hand deals with extra commands

# (repeat question, repeat answer, sync, suspend


def eventHappened(event_input):
    if event_input >= 1 and event_input <= 4:
        answerQuestion(event_input)
        getNewCardAndAsk()
    elif event_input == 5:
        repeatQuestion()
    elif event_input == 6:
        repeatAnswer()
    elif event_input == 7:
        markAndBuryCard()
        getNewCardAndAsk()
    elif event_input == 8:
        state = "special_menu"

while (1):
    if ( input != 0 ):
        eventHappened ( input )
        input = 0

    #
    # input = getInput()
    # try:
    #     input = int ( input )
    #     eventHappened(input)
    # except ValueError:
    #     # input is not a number
    #     # state can be "idle", "asked_question", "said_answer"
    #     if input == '':
    #         print state
    #         if state == "asked_question":
    #             # going to say answer
    #             if currentCard:
    #                 tts(cleanCard(currentCard.a()))
    #                 # !!! don't know why this isn't sticking!
    #                 state = "said_answer"
    #             else:
    #                 tts("no answer to repeat")
    #         elif state == "said_answer":
    #             answerQuestion(3)
    #             getNewCardAndAsk()
    #     else:
    #         tts("Unrecognized thing entered")

