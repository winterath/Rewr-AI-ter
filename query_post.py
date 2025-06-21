import requests
import json
from authors import scrolls, list_of_authors
from time import sleep

base_url = "http://127.0.0.1:3000"
path = "/query"
url = base_url + path
running = True


text = 'given text' + input("Give a text:\n-->")

query = 'l'


history = []
data = {"query": query, "k": 4, "history": history}
headers = {"Content-Type":"application/json"}

response = requests.post(url,data=json.dumps(data),headers=headers)

#print(response.json())





#data = {"query": query, "k": 4, "history": history}
#history = [{ "role": "user", "message": "Tell me somethign interesting..." }, { "role": "bot", "message": "first reponse" }]
query2 = 'never gonna give you up, never gonna let you down'

while True:
    while not query2.isnumeric():
        query2 = input("\n\nIn whose style would you want me to rewrite? \nType a number or type L for a list of authors: \n-->")
        if query2.lower() == 'l':
            print(list_of_authors)
            sleep(5)
        if query2 == '':
            break
    query = scrolls[int(query2) - 1]
    history.append({ "role": "user", "message": query });


    data = {"query": query, "k": 4, "history": history}
    headers = {"Content-Type":"application/json"}

    response = requests.post(url,data=json.dumps(data),headers=headers)
    history.append({ "role": "bot", "message": response.json() })

    print(response.json())

