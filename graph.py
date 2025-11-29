from retriever import get_retriever
from prompts import DINING_PROMPT
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI


# Try importing LangGraph (if installed)
try:
    from langgraph.graph import StateGraph, START, END
    USE_GRAPH = True
except:
    USE_GRAPH = False


def retrieve_node(state: dict):
    
    retriever = get_retriever()
    try:
        docs = retriever.invoke(state["question"])
    except Exception as e:
        print("[Error invoking retriever]", e)
        # Propagate a readable error in state
        state["context"] = ""
        state["retrieve_error"] = str(e)
        return state

    # Diagnostic: show type and small sample
    print("DEBUG: retriever returned type:", type(docs), "len (if applicable):", getattr(docs, "__len__", lambda: None)())
    # If it's an iterator/generator, try to convert to list
    if not isinstance(docs, (list, tuple)):
        try:
            docs = list(docs)
            print("DEBUG: converted docs to list, length:", len(docs))
        except Exception:
            # leave as-is
            pass

    # Build lines of plain text
    lines = []
    for i, doc in enumerate(docs):
        # Print diagnostics for first few items
        if i < 3:
            print(f"DEBUG: item {i} type: {type(doc)} -- repr start: {repr(doc)[:200]}")

        # Case A: doc is a langchain Document-like object with page_content attr
        if hasattr(doc, "page_content"):
            content = doc.page_content
            meta = getattr(doc, "metadata", {}) or {}
        # Case B: doc is a dict-like object (Chroma sometimes returns dicts)
        elif isinstance(doc, dict):
            # Try common keys
            content = doc.get("page_content") or doc.get("content") or doc.get("text") or ""
            meta = doc.get("metadata") or doc.get("meta") or {}
        # Case C: doc is a plain string
        elif isinstance(doc, str):
            content = doc
            meta = {}
        else:
            # Fallback: convert to string
            content = str(doc)
            meta = {}

        # If metadata contains structured items (list of dicts), convert them into readable strings
        items = meta.get("items")
        if isinstance(items, (list, tuple)) and items and isinstance(items[0], dict):
            item_strings = []
            for it in items:
                name = it.get("name", str(it))
                tags = ", ".join(it.get("tags", [])) if isinstance(it.get("tags", []), (list,tuple)) else str(it.get("tags",""))
                notes = it.get("notes","")
                item_strings.append(f"{name} [{tags}] ({notes})".strip())
            joined_items = ", ".join(item_strings)
            lines.append(f"{meta.get('meal_time','')}: {joined_items}")
            continue

        # If content looks like JSON string of the structured data, attempt to parse
        if isinstance(content, str) and content.strip().startswith("{"):
            # try to parse small JSON
            try:
                import json
                parsed = json.loads(content)
                # If parsed is dict with metadata-like keys, format it
                if isinstance(parsed, dict) and "items" in parsed:
                    items = parsed.get("items", [])
                    item_strings = []
                    for it in items:
                        if isinstance(it, dict):
                            name = it.get("name", "")
                            tags = ", ".join(it.get("tags", [])) if isinstance(it.get("tags", []), (list,tuple)) else str(it.get("tags",""))
                            notes = it.get("notes","")
                            item_strings.append(f"{name} [{tags}] ({notes})".strip())
                        else:
                            item_strings.append(str(it))
                    lines.append(f"{parsed.get('meal_time','')}: " + ", ".join(item_strings))
                    continue
            except Exception:
                pass

        # Otherwise just use the content string (safe)
        # If content is a list of dicts accidentally placed here, convert elements
        if isinstance(content, (list,tuple)):
            # convert each element to string
            try:
                content = ", ".join([str(x) for x in content])
            except Exception:
                content = str(content)

        lines.append(str(content))

    # Final joined context must be a string
    final_context = "\n".join(lines)
    state["context"] = final_context
    return state





# ---- NODE 2: ANSWERING ----
def answer_node(state: dict):
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2
    )

    prompt = DINING_PROMPT.format(
        context=state.get("context", ""),
        question=state.get("question", "")
    )

    # Modern LangChain call
    response = llm.invoke(prompt)

    # Extract the result text
    state["answer"] = response.content
    return state



# ---- GRAPH BUILDING ----
if USE_GRAPH:
    def build_graph():
        graph = StateGraph(dict)

        graph.add_node("retrieve", retrieve_node)
        graph.add_node("answer", answer_node)

        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "answer")
        graph.add_edge("answer", END)

        return graph.compile()

else:
    # Fallback if langgraph version is old
    class SimplePipeline:
        def invoke(self, state: dict):
            state = retrieve_node(state)
            state = answer_node(state)
            return state

    def build_graph():
        return SimplePipeline()


# Manual test
if __name__ == "__main__":
    graph = build_graph()
    res = graph.invoke({"question": "What is available for dinner?"})
    print("CONTEXT:\n", res["context"])
    print("\nANSWER:\n", res["answer"])
