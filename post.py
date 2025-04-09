import requests
import json

base_url = "http://127.0.0.1:5000"
path = "/new"
url = base_url + path

text ='''The stars twinkled above like scattered diamonds, their light piercing the darkness with an elegance that could only be described as timeless. Below, the earth stirred in a quiet symphony, as if the very soil and trees were listening for a melody. In the distance, a river meandered lazily, its surface shimmering under the pale moonlight, as though the water itself was contemplating the weight of centuries. Every breath of air seemed filled with secrets, like the kind shared only between old friends. Time moved in slow motion here, like a forgotten page from a well-worn book, waiting to be read again and again.'''


data = {"text":text,"doc_id":"892","user_id": "22"}
headers = {"Content-Type":"application/json"}

response = requests.post(url,data=json.dumps(data),headers=headers)

if response.status_code == 200:
    print("req successful")
    print(response.json())
else:
    print(response.status_code)