
execfile('common.py')

# for keyboard input
import select
import tty
import termios

switches = 0
# pull-to-ground switches input
try:
    import RPi.GPIO as GPIO
    switches = 1
except:
    print "problems importing"
    pass

print "filesystemencoding is " + sys.getfilesystemencoding().lower()

# for switches
pull_to_ground_switches = [ 12, 11, 10, 7, 5, 3 ]

if switches == 1:
    crap_tts ( "on raspberry pi, using pull-to-ground switches" )
    GPIO.setmode ( GPIO.BCM )
    for pin in enumerate(pull_to_ground_switches):
        GPIO.setup ( pin, GPIO.IN, pull_up_down=GPIO.PUD_UP )

# these are for the membrane keypad
rows = [ 2, 3, 4 ]
columns = [ 17, 27, 22 ] 
keys = [[1, 2, 3], [4,5,6], [7, 8, 9]]

previous_input = -1

def check_pull_to_ground_switches ():
    global previous_input, pull_to_ground_switches
    for switch, pin in enumerate(pull_to_ground_switches):
        if GPIO.input( pin ) == 0:
            current_input = switch
    if previous_input != current_input:
        previous_input = current_input
        print current_input
        return current_input
    return -1

currentCard = 0

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
        write_to_log("got card with cid " + str(currentCard.id) + " and did " + str(currentCard.did))
        if re.search('<img', currentCard.a()) == None:
            break
        else:
            write_to_log("card had img in it")
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
    print event_input
    try:
        if int(event_input) >= 1 and int(event_input) <= 4:
            answerQuestion(int(event_input))
            getNewCardAndAsk()
            return
    except:
        pass
    if event_input == "q":
        repeatQuestion()
    elif event_input == 'a':
        repeatAnswer()
    elif event_input == 's':
        suspendCard()
        getNewCardAndAsk()
    elif event_input == 'y':
        sync()

# try syncing on startup
sync()

try:
    crap_tts("There are {} cards in your collection".format(collection.cardCount()))
except:
    pass

#get new card and ask it
getNewCardAndAsk()

old_settings = 0

# got this idea for non-blocking keyboard input from Graham King at
# http://www.darkcoding.net/software/non-blocking-console-io-is-not-possible/
try:
   # this assignment will fail if there's no stdin
   # in which case we'll go to the exception
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
except:
    print "no keyboard"

while (1):
    # is there any keyboard input
    if old_settings: 
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            c = sys.stdin.read(1)
            if c:
                eventHappened ( c )
    elif ( switches == 1 ):
        switch_input = check_pull_to_ground_switches ()
        if switch_input != -1:
            eventHappened ( switch_input )
        
# finally:
#     termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
