import sys
import imaplib
import getpass
import email
import datetime
from pprint import pprint
import re
import numpy as np
import pandas as pd
import webbrowser
import os


def login():
    try:
        email = str(raw_input("Email Address:"))
        tmpserver = "imap." + email.split('@')[1]
        serverinput = str(raw_input("IMAP Server [{}]:".format(tmpserver)))
        M = imaplib.IMAP4_SSL(serverinput if serverinput else tmpserver)
        M.login(email, getpass.getpass(prompt="Password: "))
        print "LOGIN SUCCESSFUL!"
        return M
    except:
        print "LOGIN FAILED!"
        login()


def selectMailbox(M):
    mailboxes = {i: box.split('"')[-2] for i, box in enumerate(M.list()[1])}
    pprint(mailboxes)
    mailcnt = int(M.select(selectMailboxInputHandler(mailboxes))[1][0])
    cls()
    print "Successful, {} mails selected!\n".format(mailcnt)
        
            
def selectMailboxInputHandler(mailboxes):
    try:
        return mailboxes.get(int(input("Choose a mailbox from the list: ")))
    except:
        print "Invalid choice. Please type in the index of the desired mailbox."
        selectMailboxInputHandler()
        
        
def scanMails(M):
    selectMailbox(M)
    print("Scanning mails:")
    regex = r"(?i)<a.*href=\"(.*)\".*>(.*([nN]otifications|[cC]lick here|[aA]bbestellen|[uU]nsubscribe).*)(<\/a>)"
    links = []
    data = M.search(None, "ALL")[1]
    for num in data[0].split():
        sys.stdout.flush()
        sys.stdout.write("\r{} emails scanned, {} links found!".format(num, len(links)))
        rv, mail = M.fetch(num, '(RFC822)')
        msg = email.message_from_string(mail[0][1])

        m = re.search(regex, str(msg))
        if m:
            links.append([msg['from'], msg['subject'], m.group(1), m.group(3)])

    a = np.array(links)
    if len(links) > 0:
        sys.stdout.write("\nFollowing links where found:\n")
        df = pd.DataFrame(data={'from': a[:,0], 'subject': a[:,1], 'link': a[:,2], 'label': a[:,3]})
        print(df['link'].to_string())
        if raw_input("Would you like to open them in your browser? (y/N)") == "y":
            openLinksInBrowser(df)
    
    if raw_input("Would you like to check another mailbox? (y/N)") == "y":
        scanMails(M)
    else:
        print("Bye! :)")

        
def openLinksInBrowser(df):
    for link in df.groupby(['from','label']).first()['link']:
        webbrowser.open_new_tab(link)

        
def cls():
    os.system('cls' if os.name=='nt' else 'clear')


M = login()
scanMails(M)

