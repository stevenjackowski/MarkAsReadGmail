# Mark Unread Gmail Messages as Read

This is a quick script built using the Gmail API to mark email messages within your inbox as read. The script will prompt the user to input a date, and all messages received before the provided date will be marked as read. This can be helpful if you wish to remove those pesky unread email counts!

## Authenticating

To run the script, you will first need to follow the steps [here](https://developers.google.com/gmail/api/quickstart/python) to create an authentication file. Once you download the client_secret.json file, it should be placed in the same directory as the python script.

Note that when you first run the script, it will automatically create a JSON file in your home directory called mark-as-read.json. If for some reason you are running and modifying the script authentication scopes, note that you'll need to delete the file to force the OAuth flow to reauntheticate. 

## Dependencies
The script was tested on Python 3.6, but any Python 3.x version should work.

For dependencies, you can create a virtualenv and then run...
~~~~
$ pip3 install -r requirements.txt
~~~~
...to install all required Python modules. From there simply execute the script...
~~~~
$ python3 mark_as_read.py
~~~~
