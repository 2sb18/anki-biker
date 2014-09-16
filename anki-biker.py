# idea from stackoverflow 279237
import os, sys, inspect
# regex functions
import re
# tts support
import subprocess

import string

# for import of config
import json

config = json.load(open('config.json'))

textReplacements = dict([
  ('>', 'greater than'),
  ('-', 'dash'),
  ('ctrl-', 'control'),
  # in the case of clozes?
  ('[...]', 'what'),
  (';', 'semicolon'),
  ('{', 'open curly bracket'),
  ('}', 'close curly bracket')
  ])

cmd_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe() ))[0], "anki")))
if cmd_folder not in sys.path:
  sys.path.insert(0, cmd_folder)

# move into the anki dev folder
# os.chdir('anki')
# print os.system('pwd')
import anki
import anki.sync

# the collection should be in the current directory
collection = anki.Collection(config['collection_filename'])

currentCard = 0



# there's a method in decks called select
# that allows you to select a deck.
# currentDeck

def getCard():
  global currentCard
  # if there's an "<img" then get another card
  while ( 1 ):
    currentCard = collection.sched.getCard()
    if re.search('<img', currentCard.a()) == None:
      break

def tts(text):
  print "saying: " + text
  subprocess.call(["flite", "-t", text])

# make it so text is readable by flite
def cleanCard(text):
  # return re.sub( r'<style>.*</style>', r'', text, flags=re.DOTALL)

  # if it's an answer, there's going to be an <hr id=answer> remove
  # everything up to it
  text = re.sub ( r'^.*<hr id=answer>', '', text, flags=re.DOTALL)

  # if it's a cloze answer, remove everything except the cloze
  if re.search( '<span class=cloze>', text ) != None and re.search ( 
      '<span class=cloze>\[\.\.\.]</span>', text ) == None:
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
    remoteServer.hostKey(config['username'], config['password'])
    syncer = anki.sync.Syncer(collection, remoteServer)
    tts(syncer.sync())
  except:
    tts(str(sys.exc_info()[0]))

def getInput():
  return raw_input()

# try syncing on startup
sync()

while(1):
  input = int(getInput())
  if input >= 1 and input <= 4:
    # answer question
    collection.sched.answerCard(currentCard,input)
    tts(str(input))
    # get new card and ask it
    getCard()
    tts(cleanCard(currentCard.q()))
  elif input == 5:
    # get new card and ask it
    getCard()
    tts(cleanCard(currentCard.q()))
  elif input == 6:
    # repeat question
    tts(cleanCard(currentCard.q()))
  elif input == 7:
    # repeat answer
    tts(cleanCard(currentCard.a()))
  elif input == 8:
    # mark and bury card
    tts("mark and bury")
    # mark
    collection.markReview(currentCard)
    # buryCards in sched.py 
    collection.sched.buryNote(currentCard.nid)
    getCard()
    tts(cleanCard(currentCard.q()))
  elif input == 9:
    #say menu
    tts("1 to 4: select ease.")
    tts("5: get new card.")
    tts("6: repeat question.")
    tts("7: repeat answer.")
    tts("8: mark and bury.")
    tts("9: menu you dummy.")
    tts("0: sync")
  elif input == 0:
    sync()
  # elif input == 
