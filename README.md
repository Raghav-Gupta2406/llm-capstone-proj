Template for creating and submitting MAT496 capstone project.

# Overview of MAT496

In this course, we have primarily learned Langgraph. This is helpful tool to build apps which can process unstructured `text`, find information we are looking for, and present the format we choose. Some specific topics we have covered are:

- Prompting
- Structured Output 
- Semantic Search
- Retreaval Augmented Generation (RAG)
- Tool calling LLMs & MCP
- Langgraph: State, Nodes, Graph

We also learned that Langsmith is a nice tool for debugging Langgraph codes.

------

# Capstone Project objective

The first purpose of the capstone project is to give a chance to revise all the major above listed topics. The second purpose of the capstone is to show your creativity. Think about all the problems which you can not have solved earlier, but are not possible to solve with the concepts learned in this course. For example, We can use LLM to analyse all kinds of news: sports news, financial news, political news. Another example, we can use LLMs to build a legal assistant. Pretty much anything which requires lots of reading, can be outsourced to LLMs. Let your imagination run free.


-------------------------


## Title: SNU Dining Query Bot

## Overview

This project is a small AI assistant I developed to quickly check what food is available in my college dining hall. By using LangChain, LangGraph, and embeddings, the system retrieves menu information and answers questions like “What’s for lunch?” or “Show vegetarian options.” It’s a simple real-world use case demonstrating basic RAG and state management.

## Reason for picking up this project

I chose this project because I wanted to work on something small, practical, and directly connected to my daily life on campus. Since I check the dining hall menu frequently, building an AI assistant that can answer simple meal-related queries felt meaningful and useful. Instead of choosing a big or complicated idea, I wanted a project that I could realistically complete while still applying all the important concepts taught in the course.

This topic allowed me to cover multiple key areas from the syllabus in a clean and focused way. I used LangChain to manage the LLM interactions and prompting, and LangGraph to design a simple state-based workflow with nodes handling retrieval and response generation. I incorporated Retrieval-Augmented Generation (RAG) using embeddings and ChromaDB, which helped me demonstrate how vector stores and semantic search work in a real use case. By storing structured mess menu data and retrieving it based on the user’s natural language question, I could show my understanding of document loading, embeddings, vector indexing, retrieval, and context construction.

I also selected this project because it was ideal for practicing prompt engineering, controlled output formats, and parsing, which are essential skills when working with LLMs. Even though the problem is simple, the pipeline includes all major steps—state management, retrieval, prompt design, LLM invocation, and producing a clean answer—which aligns perfectly with the course requirements.

Overall, I picked this idea because it is simple, relevant to me as a student, and showcases all the core topics from the course in a practical and easy-to-understand way.

## Plan

I plan to excecute these steps to complete my project.

- [TODO] Step 1 involves blah blah
- [TODO] Step 2 involves blah blah
- [TODO] Step 3 involves blah blah
- ...
- [TODO] Step n involves blah blah

## Conclusion:

I had planned to achieve {this this}. I think I have/have-not achieved the conclusion satisfactorily. The reason for your satisfaction/unsatisfaction.

----------

# Added instructions:

- This is a `solo assignment`. Each of you will work alone. You are free to talk, discuss with chatgpt, but you are responsible for what you submit. Some students may be called for viva. You should be able to each and every line of work submitted by you.

- `commit` History maintenance.
  - Fork this respository and build on top of that.
  - For every step in your plan, there has to be a commit.
  - Change [TODO] to [DONE] in the plan, before you commit after that step. 
  - The commit history should show decent amount of work spread into minimum two dates. 
  - **All the commits done in one day will be rejected**. Even if you are capable of doing the whole thing in one day, refine it in two days.  
 
 - Deadline: Nov 30, Sunday 11:59 pm


# Grading: total 25 marks

- Coverage of most of topics in this class: 20
- Creativity: 5
  
