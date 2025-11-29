
from dotenv import load_dotenv
load_dotenv()

import json
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def load_menu_documents(menu_file="menu.json"):
    
    with open(menu_file, "r", encoding="utf-8") as f:
        menu_data = json.load(f)

    docs = []
    for meal_time, items in menu_data.items():

        
        readable_items = []
        for it in items:
            name = it.get("name", "")
            tags = ", ".join(it.get("tags", []))
            notes = it.get("notes", "")
            readable_items.append(f"{name} [{tags}] ({notes})")

    
        content = f"{meal_time}: {', '.join(readable_items)}"

        
        metadata = {
            "meal_time": meal_time,
            "items_joined": "; ".join(readable_items)  # keep readable list as ONE string
        }

        docs.append(Document(page_content=content, metadata=metadata))

    return docs


def create_vectorstore(docs):
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(
        docs,
        embedding=embeddings,
        collection_name="dining_menu"
    )
    return vectordb


def get_retriever():
    docs = load_menu_documents()
    vectordb = create_vectorstore(docs)
    return vectordb.as_retriever(search_kwargs={"k": 4})

