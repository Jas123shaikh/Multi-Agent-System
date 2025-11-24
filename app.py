def identity(x):
    return x

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.baidusearch import BaiduSearch
from dotenv import load_dotenv
import sqlite3
import os
from phi.playground import Playground, serve_playground_app

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

duck_tool = DuckDuckGo()
baidu_tool = BaiduSearch()

groq_model = Groq(
    id="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY,
)

web_search_agent = Agent(
    name="Web Search Agent",
    role="Search the web for the information",
    model=Groq(id="llama-3.1-8b-instant"),
    tools=[DuckDuckGo(), BaiduSearch()],
    instruction=["Always include sources"],
    show_tools_calls=True,
    markdown=True,
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=Groq(id="llama-3.1-8b-instant"),
    tools=[DuckDuckGo(), BaiduSearch()],
    instruction=[
        "Always structure analyst recommendations in a table with columns: Analyst, Rating, Target Price, Date.",
        "Use tables to display data",
        "Do NOT include any disclaimers or liability statements"
    ],
    show_tools_calls=True,
    markdown=True,
)

multi_ai_agent = Agent(
    model=Groq(id="llama-3.1-8b-instant"),
    team=[web_search_agent, finance_agent],
    instruction=[
        "Always include sources",
        "Use tables to display data"
    ],
    show_tools_calls=True,
    markdown=True,
)

def init_db():
    conn = sqlite3.connect("data.db")
    conn.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, text TEXT)")
    conn.close()

def create_note(text):
    conn = sqlite3.connect("data.db")
    conn.execute("INSERT INTO notes(text) VALUES(?)", (text,))
    conn.commit()
    conn.close()

def read_notes():
    conn = sqlite3.connect("data.db")
    rows = conn.execute("SELECT * FROM notes").fetchall()
    conn.close()
    return rows

def update_note(note_id, text):
    conn = sqlite3.connect("data.db")
    conn.execute("UPDATE notes SET text=? WHERE id=?", (text, note_id))
    conn.commit()
    conn.close()

def delete_note(note_id):
    conn = sqlite3.connect("data.db")
    conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

def main():
    init_db()

    print("\nChoose an option:")
    print("1. Create Note")
    print("2. Read Notes")
    print("3. Update Note")
    print("4. Delete Note")
    print("5. Ask AI (Your multi-agent)")
    print("6. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        text = input("Enter note text: ")
        create_note(text)
        print("Note saved!")

    elif choice == "2":
        print(read_notes())

    elif choice == "3":
        note_id = int(input("Note ID: "))
        new_text = input("New text: ")
        update_note(note_id, new_text)
        print("Updated!")

    elif choice == "4":
        note_id = int(input("Note ID: "))
        delete_note(note_id)
        print("Deleted!")

    elif choice == "5":
        query = input("Ask AI: ")
        multi_ai_agent.print_response(query)

    else:
        print("Goodbye!")

app = Playground(agents=[finance_agent, web_search_agent]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)     



