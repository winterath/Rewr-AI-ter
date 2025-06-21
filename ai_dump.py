import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv  
import json

# Load environment variables
load_dotenv() 

# Text splitting
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_text(text, user_id, document_id,notebook_id):
    doc = Document(page_content=text,metadata={"user_id":user_id,"document_id":document_id,'notebook_id':notebook_id})
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=40, add_start_index = True)
    splits = text_splitter.split_documents([doc])
    return splits  


from embed_and_store import vector_store, add_documents  


from langchain_google_genai import ChatGoogleGenerativeAI 



llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-preview-02-05",
)

app = Flask(__name__)

@app.route('/new', methods=['POST'])
def ingest_document():
    """
    Ingests a document: splits into chunks, embeds, and stores vectors.
    Request JSON: {"user_id": str, "notebook_id": str, "doc_id": str, "text": str}
    Response JSON: {"num_of_chunks": int}
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    notebook_id = data.get('notebook_id')
    doc_id = data.get('doc_id')
    text = data.get('text')

    if not all([user_id, notebook_id, doc_id, text]):
        return jsonify({'error': 'Missing required fields'}), 400

  
    chunks = split_text(text, user_id, doc_id, notebook_id) 


    add_documents(chunks)  
    try:
        vector_store.persist() 
    except AttributeError:
        pass

    return jsonify({'num_of_chunks': len(chunks)}), 200

@app.route('/query', methods=['POST'])
def query_qa():
    """
    Queries the RAG service: retrieves relevant chunks, calls LLM, returns answer.
    Request JSON: {"query": str, "k": int (optional)}
    Response JSON: {"answer": str}
    """
    data = request.get_json() or {}
    query = data.get('query')
    history = data.get('history')
   
    print(history)
    k = data.get('k', 5)

    if not query:
        return jsonify({'error': 'Query field is required'}), 400

    # Retrieve top-k relevant documents
    docs = vector_store.similarity_search(query, k=k)  
    # Prepare context
    context = "\n\n".join(doc.page_content for doc in docs)

    # Build prompt
    system_prompt = (
        "Rewrite the user's following prompt with a decent amount of the words and completely idenitcal writing style and mannerisms and personality of the given text, while conveying the exact same message as the original prompt. Your previous responses are those with the role 'bot', and the user's questions are with the role 'user'. YOU MUST KEEP YOUR RESPONSE THE SAME NUMBER OF WORDS AS THE USER'S PROMPT."
        "If you don't know how, say you don't know."
    )  #
    user_prompt = f"Context:\n{context}\n\nChat history:{json.dumps(history)}\n\nQuestion: {query}"

    # Call LLM with message tuples
    messages = [
        ("system", system_prompt),
        ("human", user_prompt),
    ]  # 
    response = llm.invoke(messages)
    answer = response.content


    return jsonify({'answer': answer}), 200

if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'production':
        print('Flask app ready for WSGI server in production')    
    else: 
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)), debug=True)



#api.py code

# import random
# from flask import Flask, request
# from split import split_text

# app = Flask(__name__)

# test_text ='''The stars twinkled above like scattered diamonds, their light piercing the darkness with an elegance that could only be described as timeless. Below, the earth stirred in a quiet symphony, as if the very soil and trees were listening for a melody. In the distance, a river meandered lazily, its surface shimmering under the pale moonlight, as though the water itself was contemplating the weight of centuries. Every breath of air seemed filled with secrets, like the kind shared only between old friends. Time moved in slow motion here, like a forgotten page from a well-worn book, waiting to be read again and again.'''


# @app.route("/new", methods=['POST'])
# def handle_upload():
#     body = request.get_json()
#     user_id = body.get('user_id')
#     doc_id = body.get('doc_id')
#     user_id = body.get('user_id')
#     notebook_id = body.get('notebook_id')
#     text = body.get('text')

#     splits = split_text(text,user_id,doc_id,notebook_id)
#     return {"num_of_splits":len(splits)}


#     if not user_id or not notebook_id or not doc_id or not text:
#         return {'status':400}

# if __name__ == "__main__":
#     app.run(debug=True)
    
