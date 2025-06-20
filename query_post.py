import requests
import json


base_url = "http://127.0.0.1:5000"
path = "/query"
url = base_url + path
running = True


text = input("Give a text:\n-->")
query = input("Rewrite the text:\n-->")
#history = [{ "role": "user", "message": "Tell me somethign interesting..." }, { "role": "bot", "message": "first reponse" }]
history = []

while True:
    query = input("What's your question? \n")
    if query == '':
        break

    history.append({ "role": "user", "message": query });


    data = {"query": query, "k": 4, "history": history}
    headers = {"Content-Type":"application/json"}

    response = requests.post(url,data=json.dumps(data),headers=headers)
    history.append({ "role": "bot", "message": response.json() })

    print(response.json())

