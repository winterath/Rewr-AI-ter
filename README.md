# KnotebookLM

## Overview

Currently, this code is a RAG that (creates a website, then) sends a post request with text, document, and user IDs. As of right now, the code only sends a request, then checks the status of the request and connection (as well as creates embeddings), but that will be changed/added to in the coming weeks. 

## Models 

It currently uses Google GenAI just for embeddings (and soon LLM prompt interactions). And yes, the API key is hard-coded.

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
'''
if response.status_code == 200:
    print("req successful")
    print(response.json())
else:
    print(response.status_code)
'''