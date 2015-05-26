#!/usr/bin/python

execfile('common.py')


sync()

# is this the best way to get all the cards?
for card_id in collection.findCards(""):
    current_card = collection.getCard(card_id)
    try:
        subprocess.call([downloadtts_file, cleanCard(current_card.q())])
        subprocess.call([downloadtts_file, cleanCard(current_card.a())])
    except:
        pass
#
# currentCard = collection.sched.getCard()
# while currentCard:
#     print "on card " + str(x)
#     downloadCard()
#     x = x + 1
#     currentCard = collection.sched.getCard()
#
# print x
#
# while 1:
#     pass
#
#





