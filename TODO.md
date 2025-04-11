# Ephergent Backend API TODO List

TODOS:

- [ ] FIX cannot add users to list:
  - Looks like data is sent in URL and not the data dictionary

  curl -X 'POST' \
  'http://127.0.0.1:5000/api/v1/mail-list/?address=beforegr8ness%40gmail.com&name=Before%20Greatness&subscribed=true&upsert=true' \
  -H 'accept: application/json' \
  -d ''

  - ERROR 2025-04-10 18:57:13,677 - werkzeug - INFO - 127.0.0.1 - - [10/Apr/2025 18:57:13] "POST /api/v1/mail-list/?address=beforegr8ness@gmail.com&subscribed=true&upsert=true HTTP/1.1" 400 -
  {
  "errors": {
    "address": "Email address cannot be blank Missing required parameter in the JSON body or the post body"
  },
  "message": "Input payload validation failed"
}



- [X] Read the Mailgun Docs and write a Flask API that does CRUD for mail list subscribers (`api/mail_list.py`, `services/mailgun_service.py`)
- [X] Use flask-restx to build the API (`api/__init__.py`, `api/mail_list.py`)
- [X] Use best practices of seperation of concerns (`services/` for logic, `api/` for endpoints, `config.py` for config)
- [X] Write usual Flask environment variables to env-example (`env-example`)

- [ ] The Ephergent blog will be POST subscribers, it is a static site,
  - [X] Provide example HTML form code to POST a subscriber email to the mail list. (`templates/subscribe_form.html`, route `/subscribe-example` in `app.py`)

- [ ] Update README.md with install and features


---


## Mailgun Docs:

CRUD Docs for working with mail list members

### Get mailing lists members

import requests

list_address = "YOUR_list_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members"

response = requests.get(url, auth=('<username>','<password>'))

data = response.json()
print(data)



### Create a mailing list member

import requests

list_address = "YOUR_list_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members"

data = {
  "address": "alice@example.com",
  "name": "Alice",
  "vars[gender]": "female",
  "vars[age]": "27",
  "subscribed": "true",
  "upsert": "true"
}

headers = {"Content-Type": "multipart/form-data"}

response = requests.post(url, data=data, headers=headers, auth=('<username>','<password>'))

data = response.json()
print(data)


### Get a member

import requests

list_address = "YOUR_list_address_PARAMETER"
member_address = "YOUR_member_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members/" + member_address

response = requests.get(url, auth=('<username>','<password>'))

data = response.json()
print(data)



### Update a mailing list member


import requests

list_address = "YOUR_list_address_PARAMETER"
member_address = "YOUR_member_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members/" + member_address

data = {
  "address": "alice@example.com",
  "name": "Alice",
  "vars[gender]": "female",
  "vars[age]": "27",
  "subscribed": "true"
}

headers = {"Content-Type": "multipart/form-data"}

response = requests.put(url, data=data, headers=headers, auth=('<username>','<password>'))

data = response.json()
print(data)



### Delete a member

import requests

list_address = "YOUR_list_address_PARAMETER"
member_address = "YOUR_member_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members/" + member_address

response = requests.delete(url, auth=('<username>','<password>'))

data = response.json()
print(data)


---


## Mailgun Docs:

CRUD Docs for working with mail list members

### Get mailing lists members

import requests

list_address = "YOUR_list_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members"

response = requests.get(url, auth=('<username>','<password>'))

data = response.json()
print(data)



### Create a mailing list member

import requests

list_address = "YOUR_list_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members"

data = {
  "address": "alice@example.com",
  "name": "Alice",
  "vars[gender]": "female",
  "vars[age]": "27",
  "subscribed": "true",
  "upsert": "true"
}

headers = {"Content-Type": "multipart/form-data"}

response = requests.post(url, data=data, headers=headers, auth=('<username>','<password>'))

data = response.json()
print(data)


### Get a member

import requests

list_address = "YOUR_list_address_PARAMETER"
member_address = "YOUR_member_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members/" + member_address

response = requests.get(url, auth=('<username>','<password>'))

data = response.json()
print(data)



### Update a mailing list member


import requests

list_address = "YOUR_list_address_PARAMETER"
member_address = "YOUR_member_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members/" + member_address

data = {
  "address": "alice@example.com",
  "name": "Alice",
  "vars[gender]": "female",
  "vars[age]": "27",
  "subscribed": "true"
}

headers = {"Content-Type": "multipart/form-data"}

response = requests.put(url, data=data, headers=headers, auth=('<username>','<password>'))

data = response.json()
print(data)



### Delete a member

import requests

list_address = "YOUR_list_address_PARAMETER"
member_address = "YOUR_member_address_PARAMETER"
url = "https://api.mailgun.net/v3/lists/" + list_address + "/members/" + member_address

response = requests.delete(url, auth=('<username>','<password>'))

data = response.json()
print(data)

