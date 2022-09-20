import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from dotenv import dotenv_values

config = {
    **dotenv_values(".env"),  # load shared development variables
    **os.environ,  # override loaded values with environment variables
}


domain = config['domain']
mail_template_file = config['template']
oAuthCredentials_file = config['client_secret_file']
service_account_file = config['service_account_file']
backup_signatures_folder = "backup_signatures"
new_signatures_folder="new_signatures"
mail_template = open(mail_template_file, "r").read()


def backupOldSignature(email, signature):
    # mkdir
    if not os.path.exists(backup_signatures_folder):
        os.mkdir(backup_signatures_folder)
    # write file
    with open(f"{backup_signatures_folder}/{email}.html", "w") as f:
        f.write(signature)


def updateSignature(email, fullName, title):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=[
            'https://www.googleapis.com/auth/gmail.settings.basic',
        ])

    impersonate = email

    credentials = credentials.with_subject(impersonate)
    try:

        # create gmail api client
        service = build('gmail', 'v1', credentials=credentials)
        primary_alias = None
        # pylint: disable=E1101
        aliases = service.users().settings().sendAs().list(userId='me')\
            .execute()
        for alias in aliases.get('sendAs'):
            if alias.get('isPrimary'):
                primary_alias = alias
                break

        # write file
        backupOldSignature(email, aliases['sendAs'][0]['signature'])

        ##Replace template variables
        template = mail_template.replace("#=name#", fullName)\
                                .replace("#=email#", email)\
                                .replace("#=title#", title)
         # mkdir
        if not os.path.exists(new_signatures_folder):
            os.mkdir(new_signatures_folder)
        # write file
        #write signature to file named with email
        with open(f"{new_signatures_folder}/{email}.html", "w") as f:
            f.write(template)
                    
        send_as_configuration = {
            'displayName': primary_alias.get('sendAsEmail'),
            'signature': template
        }

        result = service.users().settings().sendAs() \
            .patch(userId='me', sendAsEmail=primary_alias.get('sendAsEmail'),
                   body=send_as_configuration).execute()
        print(F'Updated signature for: {result.get("displayName")}')
        return

    except HttpError as error:
        print(F'An error occurred: {error}')
        result = None


def ensure_creds():
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file(
            'token.json', ['https://www.googleapis.com/auth/admin.directory.user'])
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                oAuthCredentials_file, ['https://www.googleapis.com/auth/admin.directory.user'])
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


if __name__ == '__main__':
    
    credentials = ensure_creds()
    service = build('admin', 'directory_v1', credentials=credentials)
    results = service.users().list(domain=domain, maxResults=300,orderBy='email').execute()
    users_with_title = [ user for user in results['users'] if 'organizations' in user ]
    # print(users_with_title)
    for user in users_with_title:
        fullName=user['name']['fullName']
        email = user['primaryEmail']
        title = user['organizations'][0]['title']
        print(fullName,email,title)
        if(email == config['testUser']): ##remove this line when you are ready to update all users signatures
          print("updating signature for",email)
          updateSignature(email,fullName,title)
