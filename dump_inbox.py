import os
import queue
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from dotenv import dotenv_values
import base64

config = {
    **dotenv_values(".env"),  # load shared development variables
    **os.environ,  # override loaded values with environment variables
}


domain = config['domain']
oAuthCredentials_file = config['client_secret_file']
service_account_file = config['service_account_file']
dic_ ={} 

def searchMail(email,q):
    dic_[email]=[]
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=[
            'https://mail.google.com/',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.readonly',

        ])

    impersonate = email

    credentials = credentials.with_subject(impersonate)
    try:

        # create gmail api client
        service = build('gmail', 'v1', credentials=credentials)
        primary_alias = None
        # pylint: disable=E1101
        # results = service.users().messages().list(userId='me',labelIds = ['Label_21'], maxResults=600, q='before:yyyy/mm/dd').execute()
        results = service.users().messages().list(userId='me', maxResults=1000,q=q).execute()

        if('messages' in results ):
            x = len(results['messages'])
            print(f"{x} messages contain search for {q}")
            
            for message in results['messages']:
                id = message['id']
                m = service.users().messages().get(userId='me',id=id).execute()
                # print(m)
                if(m['payload'] ):
                    for p in m['payload']['parts']:
                        if(p['mimeType'] == "text/plain"):
                            b64 = p['body']['data']
                            d = base64.urlsafe_b64decode(b64)
                            headers=m["payload"]["headers"]
                            subject= [i['value'] for i in headers if i["name"]=="Subject"]
                            dic_[email].append(subject)
                            # print(d)
                        else:
                            t = p['mimeType']
                            # print(f" mimetype is different {t}")

        return

    except HttpError as error:
        print(F'An error occurred: {error}')
        result = None

if __name__ == '__main__':
    mails = ["muhammetdogan@sensemore.io","talhasarac@sensemore.io","pinarak@sensemore.io","mertdemir@sensemore.io","hikmetbahcebasi@sensemore.io"]
    query ="to:selim@likittech.com OR  to:gokhan@likittech.com OR  to:abdullah@likittech.com OR  to:serdar@likittech.com"
    query = "https://docs.google.com/forms/d/e/1FAIpQLSe8zmnHawUtfthtuaQ87q6RxoPweFFf6l0tbVGjz74dVe5x9Q/viewform?usp=sf_link"
    [searchMail(m,q="5x9Q") for m in mails]
    print(dic_)
