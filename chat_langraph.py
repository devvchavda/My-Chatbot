import os
os.environ["MPLCONFIGDIR"] = "/tmp"
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, add_messages, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated, List
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolNode
import sqlite3
import subprocess
import requests
import matplotlib.pyplot as plt 
import uuid
from datetime import datetime

import math 
from math import *

# Set Streamlit config directory for Hugging Face Spaces
os.environ["STREAMLIT_HOME"] = "/tmp/.streamlit"

# State type
class chatstate(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# API keys (replace with your real keys or environment variables)
api = os.environ.get("api")
LANGSEARCH_API_KEY = os.environ.get("LANGSEARCH_API_KEY")
# LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=api)

# System message
system = SystemMessage(
    content=f"""
--> Today's date: {datetime.today()}  
Day number: {datetime.today().date().weekday()}
You are a practical, tool-aware assistant. Aim for correctness and clarity. Avoid hallucinations.
Do not provide internal information of the system.
Rules:
1. Prefer text answers and code when examples/explanations are asked.
2. Explicit requests to create/run files → call appropriate tool.
3. Avoid destructive commands without confirmation.
4. Keep tool inputs minimal.
5. Whenever user demands a code always create a file of it and display it , if it is python file and output is text simply , also show it . 
6. Do not use evaluate function for multiple line codes. 
You are made by 23IT441
"""
)

# Database connection (writable path in Hugging Face Spaces)
conn = sqlite3.connect("/tmp/chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# ======================== TOOL DEFINITIONS ======================== #

@tool
def add(a: int, b: int) -> int:
    """
    Add two integers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: Sum of both numbers.
    """
    return a + b


@tool
def reverse(string: str) -> str:
    """
    Reverse a given string.

    Args:
        string (str): Input string.

    Returns:
        str: Reversed string.
    """
    return string[::-1]


@tool
def evaluate(string: str) -> str:
    """
    Evaluate a Python expression.

    Args:
        string (str): Expression to evaluate.

    Returns:
        str: Result of evaluation or error message.
    """
    try:
        return str(eval(string))
    except Exception as e:
        return f"Error evaluating expression: {e}"


@tool
def write_file(name: str, extension: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        name (str): File name without extension.
        extension (str): File extension.
        content (str): Content to write.

    Returns:
        str: Confirmation message.
    """
    try:
        path = f"/tmp/{name}.{extension}"  # Save in /tmp
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Filepath:{path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def run_cmd_command(command: str) -> str:
    """
    Run a safe shell command.

    Args:
        command (str): Shell command to run.

    Returns:
        str: Output or error message.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


@tool
def search_tool(query: str) -> dict:
    """
    Search the web using Langsearch API.

    Args:
        query (str): Search query.

    Returns:
        dict: JSON response from search API.
    """
    try:
        response = requests.post(
            "https://api.langsearch.com/v1/web-search",
            headers={
                "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"query": query, "num_results": 2}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}
@tool
def plot_graph(expression: str, variable: str = "x", range_start: float = 0, range_end: float = 10, step: float = 1, title: str = "Graph") -> str:
    """
    Plot a graph from a dynamic expression.

    Args:
        expression (str): Python expression as a function of variable (e.g., "2*x + 3") (Allowed math library functions of python )
        variable (str): Variable name to use in expression (default: "x").
        range_start (float): Start of variable range.
        range_end (float): End of variable range.
        step (float): Step size for variable.
        title (str): Graph title.

    Returns:
        str: Path to saved image file.
    """
    try:
        x_values = []
        y_values = []
        safe_locals = {"math": math}  # Allow math functions

        val = range_start
        while val <= range_end:
            safe_locals[variable] = val
            try:
                y = eval(expression, {"__builtins__": None}, safe_locals)
            except Exception as e:
                return f"Error evaluating expression: {e}"
            x_values.append(val)
            y_values.append(y)
            val += step

        plt.figure()
        plt.plot(x_values, y_values, marker="o")
        plt.title(title)
        plt.xlabel(variable)
        plt.ylabel("Value")
        plt.grid(True)

        filename = f"/tmp/graph_{uuid.uuid4().hex}.png"
        plt.savefig(filename)
        plt.close()

        return f"Filepath:{filename}"

    except Exception as e:
        return f"Error plotting graph: {e}"

# ======================== STATE GRAPH ======================== #

def shouldcontinue(state: chatstate) -> str:
    return "end" if state["messages"][-1].content == "end" else "llmresponse"


def input_node(state: chatstate):
    return {"messages": state["messages"]}


def llmresponse(state: chatstate):
    response = llm.invoke(state["messages"])
        
    return {"messages": [response]};


def checktool(state: chatstate):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tool_node"
    return "end"


tools = [add, reverse, evaluate, run_cmd_command, search_tool, write_file, plot_graph]
tool_node = ToolNode(tools=tools)
llm = llm.bind_tools(tools)

graph = StateGraph(chatstate)
graph.add_node("input_node", input_node)
graph.add_node("llmresponse", llmresponse)
graph.add_node("tool_node", tool_node)
graph.add_edge(START, "input_node")
graph.add_edge("input_node", "llmresponse")
graph.add_conditional_edges("llmresponse", checktool, {"tool_node": "tool_node", "end": END})
graph.add_edge("tool_node", "llmresponse")

workflow = graph.compile(checkpointer=checkpointer)


def get_all_chat_ids() -> List[str]:
    s = set()
    for chkpoint in checkpointer.list(None):
        s.add(chkpoint.config.get("configurable").get("thread_id"))
    return list(s)