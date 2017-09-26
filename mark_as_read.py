import httplib2
import os
import sys
import re
import datetime
import progressbar

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'MarkAsRead'


def valid_date(datestring):
    """Validates a datestring to make sure it can be parsed into a datetime
    format.

    Args:
        datestring, a date in string format.

    Returns:
        valid, a boolean indicating True if the string is a valid date.
    """
    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        valid = True
    except ValueError:
        valid = False
    return valid


def ask_for_date():
    """Asks the user to input a valid date. 

    Exits the program after 3 invalid attempts. This date will be used 
    to filter emails so that only emails before the date are marked as read.

    Returns:
        date_string, the given date by the user.
    """
    attempts = 0
    print("Input a date to mark emails as read:")
    date_string = ''
    while not valid_date(date_string):
        date_string = input("YYYY-MM-DD: ")
        attempts += 1
        if not valid_date(date_string):
            print("Invalid input, please try again.\n")
        if attempts > 2:
            sys.exit("Too many invalid attempts. Exiting application.")
    return date_string


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'mark-as-read.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def list_messages_with_labels_query(service, user_id, label_ids=[], q=''):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id, q=q,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def mark_read(service, user_id, msg_id):
  """Marks the given Message as read by removing the UNREAD label.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The id of the message required.

  Returns:
    Modified message, containing updated labelIds, id and threadId.
  """
  try:
    message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                body={ 'removeLabelIds': 
                                                ['UNREAD'] }).execute()

    label_ids = message['labelIds']
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)
    raise(error)


def main():
    """<>
    """
    max_date = ask_for_date()

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    user_id = 'me'
    labels = ['INBOX','UNREAD']
    query_string = "older:" + max_date # This pulls only results before date
    unread_messages = list_messages_with_labels_query(service, user_id, label_ids=labels, q=query_string)

    if not unread_messages:
        print("No unread messages found.")
    else:
        count = 0 # Used to count successes
        with progressbar.ProgressBar(max_value=len(unread_messages)) as bar:
            for message in unread_messages:
                mark_read(service, user_id, message['id'])
                count += 1
                bar.update(count)

            print('\n\n\n')
            print("Finished " + str(count) + " messages." )
            print("Thanks for using my script!\n\n\n")


if __name__ == '__main__':
    main()