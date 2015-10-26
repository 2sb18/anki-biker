
- anki-biker needs anki to be installed at /usr/share/anki

- if you want to have anki-biker start on bootup, you have to add a line to /etc/rc.local
- this is what I added to mine right before the "exit 0"

LC_ALL="en_GB.utf8" python /home/pi/anki-biker/anki-biker.py &

- the LC_ALL changes the locale to something anki can work with. Anki wants to see a UTF-8 locale. To figure out what locales you have, you can run "locale -a"

- The & at the end of the command runs the program in the background.


- After you're done using anki-biker, you'll have to press ctrl-c to quit it. Because of the way the program takes control of your stdin, you'll probably have to run the "reset" command to get back to normal. Note: you won't be able to see what you're typing when you type "reset".


- here's some useful info I learned about the anki library

# collection.cardCount(): get total number of cards in collection
# collection.save(): save database state?

# sched is part of a collection
# sched.deckDueList(): returns array of all the decks with info about how much is due
# sched.getCard(): pop next card from queue. None if finished
# sched.reset(): reset the due queue.
# sched.answerCard(card, ease): answer a card
# sched.counts(card=None): not sure about this

# notes.addtag( tag )

THINGS TO DO






