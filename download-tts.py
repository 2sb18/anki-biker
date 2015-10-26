#!/usr/bin/python

execfile('common.py')

sync()

# check out download-tts.sh for error codes
def download_and_check(card):
    note = card.note()
    
    def private_function(string):
        returncode = subprocess.call([downloadtts_file, cleanCard(string)])
        if returncode == 1:
            print "too long"
            note.addTag("too_long")
            collection.sched.suspendCards([card.id])
        if returncode == 5:
            print "file_size_zero"
            note.addTag("file_size_zero")
            collection.sched.suspendCards([card.id])
        if returncode == 10:
            die()
   
    private_function(card.q())
    private_function(card.a())
    note.flush()



# is this the best way to get all the cards?
for card_id in collection.findCards(""):
    current_card = collection.getCard(card_id)
    try:
        download_and_check(current_card)
    except UnicodeEncodeError:
        # at some point we'll do something more intelligent with this
        pass
    except Exception as e:
        print "meow"
        print e

collection.save()
sync()
