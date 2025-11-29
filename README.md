## Title: SNU Dining Query Bot

## Overview

This project is a small AI assistant I developed to quickly check what food is available in my college dining hall. By using LangChain, LangGraph, and embeddings, the system retrieves menu information and answers questions like “What’s for lunch?” or “Show vegetarian options.” It’s a simple real-world use case demonstrating basic RAG and state management.

## Reason for picking up this project

I chose this project because I wanted to work on something small, practical, and directly connected to my daily life on campus. Since I check the dining hall menu frequently, building an AI assistant that can answer simple meal-related queries felt meaningful and useful. Instead of choosing a big or complicated idea, I wanted a project that I could realistically complete while still applying all the important concepts taught in the course.

This topic allowed me to cover multiple key areas from the syllabus in a clean and focused way. I used LangChain to manage the LLM interactions and prompting, and LangGraph to design a simple state-based workflow with nodes handling retrieval and response generation. I incorporated Retrieval-Augmented Generation (RAG) using embeddings and ChromaDB, which helped me demonstrate how vector stores and semantic search work in a real use case. By storing structured mess menu data and retrieving it based on the user’s natural language question, I could show my understanding of document loading, embeddings, vector indexing, retrieval, and context construction.

I also selected this project because it was ideal for practicing prompt engineering, controlled output formats, and parsing, which are essential skills when working with LLMs. Even though the problem is simple, the pipeline includes all major steps—state management, retrieval, prompt design, LLM invocation, and producing a clean answer—which aligns perfectly with the course requirements.

Overall, I picked this idea because it is simple, relevant to me as a student, and showcases all the core topics from the course in a practical and easy-to-understand way.

## Plan

I planned to execute these steps to complete my project:

- [DONE] Step 1: I started by creating a new project folder and setting up a virtual environment so everything stays clean and organized. Then I installed all the required libraries like LangChain, LangGraph, ChromaDB, and OpenAI. This gave me the base setup needed to start building the project.

- [DONE] Step 2: In this step, I created a structured menu.json file containing all five meal slots from my college mess. I made sure the data was clean and consistent so it could be easily processed by my retriever later. This became the main dataset for my project.
- [DONE] Step 3: Here, I loaded the menu data, generated embeddings using OpenAI, and stored them in a Chroma vector database. I then created a retriever that searches the mess menu semantically, so the system can understand natural questions like “What’s for dinner?”. This forms the core of the RAG pipeline.
- [DONE] Step 4: I wrote a prompt template that guides the LLM on how to use the retrieved context and answer the user properly. This step helped me control the response format and avoid unnecessary or incorrect output. It made the system more reliable and readable.
- [DONE] Step 5: In this step I created the graph structure using LangGraph with two nodes: one for retrieval and one for generating the final answer. I set up how data moves between the nodes using edges, so the question, context and answer flow smoothly through the pipeline.

## Conclusion:

I had planned to achieve {this this}. I think I have/have-not achieved the conclusion satisfactorily. The reason for your satisfaction/unsatisfaction.


# Grading: total 25 marks

- Coverage of most of topics in this class: 20
- Creativity: 5
  
