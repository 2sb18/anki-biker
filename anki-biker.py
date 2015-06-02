
execfile('common.py')

# for keyboard input
import select
import tty
import termios

print "filesystemencoding is " + sys.getfilesystemencoding().lower()

def crap_tts(text):
    print "saying this crappily: " + text
    try:
        subprocess.call(['flite', '-t', text])
    except OSError:
        sys.exit("looks like you need to install flite. run 'sudo apt-get install flite'")

# for input to raspberry pi
# if we aren't using the raspberry (ie we are developing or debugging), this
# module shouldn't exist
try:
    import pifacedigitalio as p
    p.init()
    pifacedigital = p.PiFaceDigital()
    listener = p.InputEventListener(chip=pifacedigital)
    def print_input(event):
        global input
        # print(event.pin_num)
        mapthing = [3,6,2,5,8,1,4,7]
        # debounce for 50ms	
        time.sleep ( 0.05 )
        if p.digital_read(event.pin_num):
            input = mapthing[event.pin_num]
        # eventHappened(mapthing[event.pin_num])
    for i in range(8):
        listener.register(i,p.IODIR_FALLING_EDGE, print_input)
    listener.activate()
    crap_tts ( "PiFaceDigital detected" )
except:
    crap_tts ( "PiFaceDigital not detected" )
    pass

currentCard = 0

currentVolume = 80

# state can be "idle", "asked_question", "said_answer"
state = "idle"

input = 0

print ankitts_file

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

def getNewCardAndAsk():
    global state
    if getNewCard():
        tts(cleanCard(currentCard.q()))
    else:
        crap_tts("can't get another card")
    state = "asked_question"

def repeatQuestion():
    if currentCard:
        tts(cleanCard(currentCard.q()))
        state = "asked_question"
    else:
        crap_tts("no question to repeat")

def repeatAnswer():
    # repeat answer
    if currentCard:
        tts(cleanCard(currentCard.a()))
        state = "said_answer"
    else:
        crap_tts("no answer to repeat")

# this doesn't seem to mark the card
def markAndBuryCard():
    if currentCard:
        collection.markReview(currentCard)
        collection.sched.buryNote(currentCard.nid)
        crap_tts("mark and bury")
    else:
        crap_tts("no card to bury")

def suspendCard():
    if currentCard:
        collection.sched.suspendCards([currentCard.id])
        crap_tts("suspended")
    else:
        crap_tts("no card to suspend")

def answerQuestion(input):
    # answer question
    collection.sched.answerCard(currentCard,input)
    collection.save()
    crap_tts(str(input))

# collection.cardCount(): get total number of cards in collection
# collection.save(): save database state?

# sched is part of a collection
# sched.deckDueList(): returns array of all the decks with info about how much is due
# sched.getCard(): pop next card from queue. None if finished
# sched.reset(): reset the due queue.
# sched.answerCard(card, ease): answer a card
# sched.counts(card=None): not sure about this




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
    global state
    if state == "special_menu":
        if event_input == 8:
            crap_tts("exiting special menu")
            state = "idle"
        elif event_input == 7:
            sync()
    else:
        if event_input >= 1 and event_input <= 4:
            answerQuestion(event_input)
            getNewCardAndAsk()
        elif event_input == 5:
            repeatQuestion()
        elif event_input == 6:
            repeatAnswer()
        elif event_input == 7:
            suspendCard()
            getNewCardAndAsk()
        elif event_input == 8:
            crap_tts("special menu")
            state = "special_menu"


# try syncing on startup
sync()

try:
    crap_tts("There are {} cards in your collection".format(collection.cardCount()))
except:
    pass

#get new card and ask it
getNewCardAndAsk()


# got this idea for non-blocking keyboard input from Graham King at
# http://www.darkcoding.net/software/non-blocking-console-io-is-not-possible/
try:
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    while (1):
        # is there any keyboard input
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            c = sys.stdin.read(1)
            if c >= '1' and c <= '8':
                print c
                input = int(c)
        if ( input != 0 ):
            eventHappened ( input )
            input = 0
except:
    while (1):
        if ( input != 0 ):
            eventHappened ( input )
            input = 0
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
