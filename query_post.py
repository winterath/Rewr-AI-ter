import requests
import json
from authors import scrolls, list_of_authors
import os
from time import sleep #aight this and os are weird imports but they're for quality of life just trust the process

base_url = "http://127.0.0.1:3000"
path = "/query"
url = base_url + path
running = True


text = 'given text' + input("Give a text:\n-->")

query_query = 'filler'

while not query_query.isnumeric():
    os.system('clear')
    query_query = input("Rewrite in the style of (type a number):\nType L to see list of authors\n-->")
    if query_query.lower() == 'l':
        print(f"list of authors and their respective texts (THIS LIST WILL BE UP FOR 20 SECONDS):\n{list_of_authors}")
        sleep(20)
query = scrolls[int(query_query) - 1]






data = {"query": query, "k": 4, "query_for_the_query": query_query}
headers = {"Content-Type":"application/json"}

response = requests.post(url,data=json.dumps(data),headers=headers)

print(response.json())





#data = {"query": query, "k": 4, "history": history}
#history = [{ "role": "user", "message": "Tell me somethign interesting..." }, { "role": "bot", "message": "first reponse" }]
# history = []


# while True:
#     query = input("What do you want me to rewrite? \n")
#     if query == '':
#         break

#     history.append({ "role": "user", "message": query });


#     data = {"query": query, "k": 4, "history": history}
#     headers = {"Content-Type":"application/json"}

#     response = requests.post(url,data=json.dumps(data),headers=headers)
#     history.append({ "role": "bot", "message": response.json() })

#     print(response.json())

