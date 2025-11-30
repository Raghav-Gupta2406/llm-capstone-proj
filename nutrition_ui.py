import json
import re
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

MENU_FILE = Path("menu_week.json")
if not MENU_FILE.exists():
    raise FileNotFoundError("menu_week.json not found. Add your weekly menu JSON file.")

with open(MENU_FILE, "r", encoding="utf-8") as f:
    MENU_WEEK = json.load(f)

USE_LANGCHAIN = False
USE_LANGGRAPH = False
llm = None
PromptTemplate = None
LLMChain = None
ChatPromptTemplate = None
HumanMessagePromptTemplate = None
SystemMessagePromptTemplate = None

try:
   
    from langchain.chat_models import ChatOpenAI
    from langchain import LLMChain
    from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
    llm = ChatOpenAI(temperature=0)
    ChatPromptTemplate = ChatPromptTemplate
    HumanMessagePromptTemplate = HumanMessagePromptTemplate
    SystemMessagePromptTemplate = SystemMessagePromptTemplate
    LLMChain = LLMChain
    USE_LANGCHAIN = True
except Exception:
    try:
        # fallback: simple OpenAI wrapper
        from langchain import OpenAI, LLMChain
        from langchain.prompts import PromptTemplate

        llm = OpenAI(temperature=0)
        PromptTemplate = PromptTemplate
        LLMChain = LLMChain
        USE_LANGCHAIN = True
    except Exception:
        USE_LANGCHAIN = False

try:
    from langgraph.graph import StateGraph, START, END

    USE_LANGGRAPH = True
except Exception:
    USE_LANGGRAPH = False

print("LangChain available:", USE_LANGCHAIN)
print("LangGraph available:", USE_LANGGRAPH)


# ---------- Utilities ----------
def find_day(text: str) -> Optional[str]:
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    t = text.lower()
    for d in days:
        if d in t:
            return d
    return None


def find_meal(text: str) -> Optional[str]:
    mapping = {
        "breakfast": "breakfast",
        "lunch": "lunch",
        "dinner": "dinner",
        "evening": "evening_snacks",
        "snack": "evening_snacks",
        "midnight": "midnight_mess",
        "midnight_mess": "midnight_mess",
        "evening_snacks": "evening_snacks",
    }
    t = text.lower()
    for k,v in mapping.items():
        if k in t:
            return v
    return None


# ---------- Pure-Python handlers (same logic as before) ----------
def handle_menu_lookup(day: Optional[str], meal: Optional[str]) -> str:
    if not day or not meal:
        return "Please specify the day and meal (e.g., 'monday lunch')."
    items = MENU_WEEK.get(day, {}).get(meal, [])
    if not items:
        return f"No menu found for {meal} on {day}."
    lines = [f"Menu -> {day.capitalize()} / {meal.replace('_',' ')}:\n"]
    for it in items:
        tags = ",".join(it.get("tags", []))
        lines.append(f"- {it['name']} | {tags} | {it.get('calories',0)} kcal | protein {it.get('protein',0)}g | portion: {it.get('portion','1')}")
    return "\n".join(lines)


def handle_protein_target(day: Optional[str], meal: Optional[str], target: Optional[float]) -> str:
    if not day or not meal or not target:
        return "I need day, meal and a protein target (e.g., 'I need 30 protein for dinner on friday')."
    items = MENU_WEEK.get(day, {}).get(meal, [])
    if not items:
        return f"No items available for {meal} on {day}."
    # choose a multi-item greedy plan rather than single item. We will return integer portions; try to minimize portions.
    # Simple greedy: pick highest protein per portion items until target met
    items_sorted = sorted(items, key=lambda x: x.get("protein", 0), reverse=True)
    plan = []
    remaining = target
    for it in items_sorted:
        prot = it.get("protein", 0)
        if prot <= 0:
            continue
        need = int((remaining + prot - 1) // prot)  # ceil
        if need <= 0:
            continue
        # cap need to reasonable number
        if need > 10:
            need = 10
        plan.append((it, need))
        remaining -= need * prot
        if remaining <= 0:
            break
    if not plan:
        return "Protein data missing for items."

    lines = [f"Plan to reach {target}g protein at {day.capitalize()} {meal.replace('_',' ')}:"]
    total_prot = 0
    total_cal = 0
    for it, cnt in plan:
        total_prot += cnt * it.get("protein", 0)
        total_cal += cnt * it.get("calories", 0)
        lines.append(f"- {cnt} x {it['name']} -> protein {cnt*it.get('protein',0)}g, calories {cnt*it.get('calories',0)} kcal")
    lines.append(f"\nApprox protein: {total_prot}g | Approx calories: {total_cal} kcal")
    return "\n".join(lines)


def handle_portion_calc(day: Optional[str], items: List[Dict[str,Any]]) -> str:
    if not day or not items:
        return "Provide day and items with quantities (e.g., '2.5 Paneer Lababdar and 3 roti on sunday lunch')."
    # build lookup
    lookup = {}
    for meal_items in MENU_WEEK.get(day, {}).values():
        for it in meal_items:
            lookup[it['name'].lower()] = it
    results = []
    total_prot = 0.0
    total_cal = 0.0
    for entry in items:
        qty = float(entry.get("qty", 0))
        name = entry.get("name","").lower().strip()
        found = lookup.get(name)
        if not found:
            # try substring match
            for k,v in lookup.items():
                if name in k:
                    found = v
                    break
        if not found:
            results.append(f"- Could not find item '{entry.get('name')}' on {day}")
            continue
        p = qty * found.get("protein", 0)
        c = qty * found.get("calories", 0)
        total_prot += p
        total_cal += c
        results.append(f"- {qty} x {found['name']} -> protein {p:.1f}g, calories {c:.1f} kcal")
    if not results:
        return "No items matched."
    results.append(f"\nTotal protein: {total_prot:.1f}g | Total calories: {total_cal:.1f} kcal")
    return "\n".join(results)


def handle_full_day_plan(day: Optional[str], target: Optional[int]) -> str:
    if not day or not target:
        return "Need day and calorie target (e.g., 'planner for wednesday 1500 calories')."
    day_data = MENU_WEEK.get(day, {})
    if not day_data:
        return f"No menu info for {day}."
    # Simple integer partition: split target into 3 roughly equal parts (breakfast/lunch/dinner)
    per_meal = int(target // 3)
    out = [f"Planner for {day.capitalize()} aiming {target} kcal (integer portions):"]
    total_cals = 0
    total_protein = 0.0

    # prefer 2 items per meal and optionally a roti if available
    roti = None
    for mitems in day_data.values():
        for it in mitems:
            if "roti" in it["name"].lower():
                roti = it
                break
        if roti:
            break

    for meal in ["breakfast", "lunch", "dinner"]:
        items = list(day_data.get(meal, []))
        if not items:
            out.append(f"\n{meal.capitalize()}: no items")
            continue
        # sort by calories descending; choose top two and try integer counts
        items_sorted = sorted(items, key=lambda x: x.get("calories",0), reverse=True)
        a = items_sorted[0]
        b = items_sorted[1] if len(items_sorted) > 1 else items_sorted[0]
        # start with one portion each
        pa = 1
        pb = 1
        meal_cal = pa*a.get("calories",0) + pb*b.get("calories",0)
        # increment the smaller-calorie item first until near per_meal
        while True:
            cand_a = meal_cal + a.get("calories",0)
            cand_b = meal_cal + b.get("calories",0)
            if cand_a <= per_meal or cand_b <= per_meal:
                # pick the one that gives closer to per_meal
                diffa = per_meal - cand_a if cand_a <= per_meal else 1e9
                diffb = per_meal - cand_b if cand_b <= per_meal else 1e9
                if diffa <= diffb:
                    pa += 1
                    meal_cal = cand_a
                else:
                    pb += 1
                    meal_cal = cand_b
            else:
                break
        roti_cnt = 0
        if roti and meal in ("lunch","dinner"):
            if meal_cal + roti.get("calories",0) <= per_meal:
                roti_cnt = 1
                meal_cal += roti.get("calories",0)
                # try add more but keep integer and <= per_meal
                while meal_cal + roti.get("calories",0) <= per_meal:
                    roti_cnt += 1
                    meal_cal += roti.get("calories",0)
        meal_prot = pa*a.get("protein",0) + pb*b.get("protein",0) + roti_cnt*(roti.get("protein",0) if roti else 0)
        total_cals += meal_cal
        total_protein += meal_prot
        out.append(f"\n{meal.capitalize()}:")
        out.append(f"- {a['name']} : {pa} portion(s) -> {pa*a.get('calories',0)} kcal")
        out.append(f"- {b['name']} : {pb} portion(s) -> {pb*b.get('calories',0)} kcal")
        if roti_cnt:
            out.append(f"- {roti['name']} : {roti_cnt} portion(s) -> {roti_cnt*roti.get('calories',0)} kcal")
        out.append(f"Meal total: {meal_cal} kcal | approx protein: {meal_prot:.1f} g")

    out.append(f"\nDay total approx calories: {total_cals} kcal | total protein: {total_protein:.1f} g")
    out.append("(Note: integer portions used so totals may be slightly less than target.)")
    return "\n".join(out)


# ---------- LLM parsing helpers ----------
PROMPT_SYSTEM = """
You are a JSON intent parser. Convert a user's single-line request about the mess menu into a JSON object only.
Do not add any extra text. The JSON keys:
- action: one of ["menu","protein","portion_calc","plan","unknown"]
- day: lowercase weekday or null
- meal: one of ["breakfast","lunch","dinner","evening_snacks","midnight_mess"] or null
- target: numeric for protein or calories when applicable (else null)
- items: for portion_calc a list like [{"qty":2.5,"name":"Paneer Lababdar"}, ...] else []
Example outputs:
{"action":"menu","day":"monday","meal":"lunch","target":null,"items":[]}
{"action":"protein","day":"friday","meal":"dinner","target":30,"items":[]}
{"action":"portion_calc","day":"sunday","meal":"lunch","target":null,"items":[{"qty":2.5,"name":"Paneer Lababdar"},{"qty":3,"name":"roti"}]}
{"action":"plan","day":"wednesday","meal":null,"target":1500,"items":[]}
"""

def robust_llm_call(prompt_text: str) -> Optional[str]:
    """Call the LangChain LLM object with several common call patterns and return text or None."""
    global llm
    if not USE_LANGCHAIN or llm is None:
        return None

    try:
        # prefer many versions: if llm has 'predict'
        if hasattr(llm, "predict"):
            return llm.predict(prompt_text)
        # if llm is a Chat model expecting messages: try chat-style call
        if hasattr(llm, "generate") or hasattr(llm, "__call__"):
            # try ChatOpenAI-like call with messages
            try:
                from langchain.schema import HumanMessage, SystemMessage
                messages = [SystemMessage(content=PROMPT_SYSTEM), HumanMessage(content=prompt_text)]
                # Some ChatOpenAI versions are callable with messages -> return ChatResult-like
                res = llm(messages)
                # res may be LLMResult or ChatResult; try get text
                if isinstance(res, str):
                    return res
                if hasattr(res, "content"):
                    return res.content
                if hasattr(res, "generations"):
                    # new-style LLMResult
                    gens = res.generations
                    if gens and gens[0]:
                        if isinstance(gens[0], list):
                            return gens[0][0].text
                        else:
                            return gens[0].text
                # fallback to string
                return str(res)
            except Exception:
                pass
        # fallback try generate with list of messages
        try:
            out = llm.generate([{"role":"system","content":PROMPT_SYSTEM},{"role":"user","content":prompt_text}])
            if hasattr(out, "generations"):
                gens = out.generations
                if gens and gens[0] and gens[0][0]:
                    return gens[0][0].text
            return str(out)
        except Exception:
            pass
    except Exception:
        pass
    return None


def parse_user_with_llm(user_text: str) -> Dict[str,Any]:
    """Return intent dict parsed by LLM or None if parse fails."""
    if not USE_LANGCHAIN or llm is None:
        return None
    # call LLM
    resp = robust_llm_call(user_text)
    if not resp:
        return None
    # extract JSON substring
    j = resp.strip()
    i = j.find("{")
    k = j.rfind("}")
    if i >= 0 and k >= 0:
        j = j[i:k+1]
    try:
        parsed = json.loads(j)
        return parsed
    except Exception:
        return None


# ---------- Heuristic fallback parser ----------
def heuristic_parse(text: str) -> Dict[str,Any]:
    t = text.lower()
    day = find_day(t)
    meal = find_meal(t)
    # plan request
    if "planner" in t or "planner for" in t or "plan for" in t:
        m = re.search(r"(\d{3,4})", t)
        target = int(m.group(1)) if m else None
        return {"action":"plan","day":day,"meal":meal,"target":target,"items":[]}
    # protein request: '30 protein'
    m = re.search(r"(\d+(\.\d+)?)\s*(g|grams)?\s*protein", t)
    if m:
        target = float(m.group(1))
        return {"action":"protein","day":day,"meal":meal,"target":target,"items":[]}
    # portion calc: find qty+item patterns
    parts = re.findall(r"(\d+(\.\d+)?)\s*([A-Za-z][A-Za-z0-9 \-']+)", t)
    items = []
    for p in parts:
        qty = float(p[0])
        name = p[2].strip()
        items.append({"qty":qty,"name":name})
    if items:
        return {"action":"portion_calc","day":day,"meal":meal,"target":None,"items":items}
    # menu questions
    if any(kw in t for kw in ("what's for","what is for","menu","what's available","what is available","what for")):
        return {"action":"menu","day":day,"meal":meal,"target":None,"items":[]}
    return {"action":"unknown","day":day,"meal":meal,"target":None,"items":[]}


# ---------- Graph orchestration and runner ----------
def run_with_graph(user_text: str) -> str:
    """
    Create a simple StateGraph with three nodes: parse -> exec -> format
    If LangGraph is unavailable, run handlers directly.
    """
    if not USE_LANGGRAPH:
        # fallback: parse with llm or heuristics, then call handlers
        parsed = parse_user_with_llm(user_text) or heuristic_parse(user_text)
        return execute_parsed(parsed)
    try:
        # build graph
        graph = StateGraph()
        # parse node
        def parse_node(state: dict):
            state["parsed"] = parse_user_with_llm(state.get("input")) or heuristic_parse(state.get("input"))
            return state
        # exec node
        def exec_node(state: dict):
            parsed = state.get("parsed", {})
            state["result"] = execute_parsed(parsed)
            return state
        # answer node (pass-through)
        def answer_node(state: dict):
            return state

        graph.add_node("PARSE", parse_node, START)
        graph.add_node("EXEC", exec_node, "PARSE")
        graph.add_node("ANSWER", answer_node, "EXEC")
        state = {"input": user_text}
        out = graph.invoke(state)
        return out.get("result", "Could not produce an answer.")
    except Exception:
        # fallback
        parsed = parse_user_with_llm(user_text) or heuristic_parse(user_text)
        return execute_parsed(parsed)


def execute_parsed(parsed: Dict[str,Any]) -> str:
    """Given parsed intent dict call the appropriate handler."""
    action = parsed.get("action")
    day = parsed.get("day")
    meal = parsed.get("meal")
    if action == "menu":
        return handle_menu_lookup(day, meal)
    if action == "protein":
        return handle_protein_target(day, meal, parsed.get("target"))
    if action == "portion_calc":
        return handle_portion_calc(parsed.get("day"), parsed.get("items", []))
    if action == "plan":
        return handle_full_day_plan(day, parsed.get("target"))
    return "I couldn't understand your request. Type 'help' for examples."


# ---------- Interactive CLI ----------
def main():
    print("\nSNU Mess Nutrition Assistant (LangChain + LangGraph if available). Type 'help' for examples.\n")
    while True:
        u = input("Your request> ").strip()
        if not u:
            continue
        if u.lower() in ("quit","exit"):
            print("Goodbye.")
            break
        if u.lower() == "help":
            print(
                "\nExamples:\n"
                "- monday lunch menu\n"
                "- what's for dinner on friday\n"
                "- i need 30 protein for dinner on friday\n"
                "- how much protein from 2.5 Paneer Lababdar and 3 roti on sunday lunch\n"
                "- planner for wednesday 1500 calories\n"
                "- quit -> exit\n"
            )
            continue
        try:
            ans = run_with_graph(u)
        except Exception as e:
            ans = f"Error processing request: {e}"
        print("\n" + ans + "\n")


if __name__ == "__main__":
    main()
