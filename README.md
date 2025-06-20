# KnotebookLM

## Overview

Currently, this code is a RAG that (creates a website, then) sends a post request with text, document, and user IDs. As of right now, the code only sends a request, then checks the status of the request and connection (as well as creates embeddings), but that will be changed/added to in the coming weeks. 

## Models 

It currently uses Google GenAI.

Dependencies

Flask
pysqlite3-binary
json
requests
sys
langchain_text_splitters
langchain_core.documents

## How To Start

If you feel like it, put in your own Google API key in .env
Put in the text you desire or leave it be
python api.py (will start up website)
    -from there, open the website in the browser
python post.py
    -will see if the request is successful
        -if it is, the number of splits will be returned (according to specified chunk size + text size)
        -if not, (error) status code will be returned

Making request

see post.py

example of error:
```
if response.status_code == 200:
    print("req successful")
    print(response.json())
else:
    print(response.status_code)
```

# How the RAG system works

Alright. So we're in the website, ok? OK. we type in a query from the console, we give it to the AI, and bada bing bada boom, the AI gives you a magical response. But how does it actually work?

## Putting the sauce in the pizza

First, we put in a Document. On a cool website we would drag and drop it. But we, uncool as we are, put the text in the text variable. The embed_and_store file will create vectors (for similarity scores later on, so the AI can do its stuff). These vectors will be stored in chroma_langchain_db.
```
text ='''The stars twinkled above like scattered diamonds, their light piercing the darkness with an elegance that could only be described as timeless. Below, the earth stirred in a quiet symphony, as if the very soil and trees were listening for a melody.'''

#in split
def split_text(text, user_id, document_id,notebook_id):
    doc = Document(page_content=text,metadata={"user_id":user_id,"document_id":document_id,'notebook_id':notebook_id})
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=40, add_start_index = True)
    splits = text_splitter.split_documents([doc])
    return splits
```

## Starting the pizza maker

Starting the website is simple. I used to use python api.py to start it, but now we can use my extremely efficient ai-dump.py. This will start the website so we can either use post or query_post.py. 

```
#in api.py
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
#in post.py
if __name__ == "__main__":
    app.run(debug=True)
    
response = requests.post(url,data=json.dumps(data),headers=headers)

if response.status_code == 200:
    print("req successful")
    print(response.json())
else:
    print(response.status_code)
```

## Putting the pizza in the maker
Now, we use query_post.py to create a prompt based on the rewrite we ask it. It will use the vectors from embed_and_store to make a similarity search (so obviously, if there's nothing similar, the AI will say it doesn't know). It will then create a new prompt based on the most relevant points from the document.

```
def ingest_document():
    # deleted a buncha stuff becaouse I don't care

    # Retrieve top-k relevant documents
    docs = vector_store.similarity_search(query, k=k)  # ([api.python.langchain.com](https://api.python.langchain.com/en/latest/vectorstores/langchain_chroma.vectorstores.Chroma.html))

    # Prepare context
    context = "\n\n".join(doc.page_content for doc in docs)

    # Build prompt
    system_prompt = (
        "Use the following context to answer the question. "
        "If you don't know the answer, say you don't know."
    )  # ([raw.githubusercontent.com](https://raw.githubusercontent.com/winterath/knotebooklm-rag-service/main/embed_and_store.py))
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    # Call LLM with message tuples
    messages = [
        ("system", system_prompt),
        ("human", user_prompt),
    ]  # ([python.langchain.com](https://python.langchain.com/api_reference/google_genai/chat_models/langchain_google_genai.chat_models.ChatGoogleGenerativeAI.html))
    response = llm.invoke(messages)
    answer = response.content
```

## Eating the pizza

Enjoy the response the AI spits out to you. You've earned it. No, scratch that, **I** earned it. Go do something, you slackers.