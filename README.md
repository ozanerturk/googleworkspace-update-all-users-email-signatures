Cautious! This script will updates all users email signatures with given template.html

download service account credentials and oath credentials from google console

create .env as following

```
domain=<your email domain name>
template=template.html
client_secret_file=client_secret.json
service_account_file=service_account.json
testUser=hello@sensemore.io
```

pip install -r requirements.txt

python main.py

