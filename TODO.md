# Ephergent Backend API TODO List

TODOS:

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

