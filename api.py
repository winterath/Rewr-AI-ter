import random
from flask import Flask, request
from split import split_text

app = Flask(__name__)

test_text ='''The stars twinkled above like scattered diamonds, their light piercing the darkness with an elegance that could only be described as timeless. Below, the earth stirred in a quiet symphony, as if the very soil and trees were listening for a melody. In the distance, a river meandered lazily, its surface shimmering under the pale moonlight, as though the water itself was contemplating the weight of centuries. Every breath of air seemed filled with secrets, like the kind shared only between old friends. Time moved in slow motion here, like a forgotten page from a well-worn book, waiting to be read again and again.'''


@app.route("/new", methods=['POST'])
def handle_upload():
    body = request.get_json()
    user_id = body.get('user_id')
    doc_id = body.get('doc_id')
    user_id = body.get('user_id')
    notebook_id = body.get('notebook_id')
    text = body.get('text')

    splits = split_text(text,user_id,doc_id,notebook_id)
    return {"num_of_splits":len(splits)}


    if not user_id or not notebook_id or not doc_id or not text:
        return {'status':400}

if __name__ == "__main__":
    app.run(debug=True)
    