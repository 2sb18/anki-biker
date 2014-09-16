import json
import getpass

collection_filename = raw_input('What is the filename of your collection?\n')

username = raw_input('What is your username?\n')

password = getpass.getpass('What is your password?\n')

config = {'collection_filename': collection_filename, 'username': username, 'password': password }

json.dump(config, open('config.json', 'w'))
