import pandas as pd
import requests
import os
from jsonschema.exceptions import best_match
from pymongo import MongoClient
from urllib.parse import quote_plus
from rdflib.compare import similar
from faiss_search import Document_Handling

username = "abhibarde1799"
password = "iYa4ab7P3FtuTMlh"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)
client = MongoClient(f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.kfkd7.mongodb.net/mydatabase?retryWrites=true&w=majority")   # MongoDb Connection String
db = client["AI_ChatBot"]
collection = db["tbl_progress_record"]


class ChatBot:
    def data_frames(self):

        df = self.fetch_progress()

        if df.empty:
            df = None
        return df

    def fetch_progress(self):
        # fetch All record and return pandas frame
        data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB _id field
        return pd.DataFrame(data)

    def insert_progress(self, topic, solved, month):
        # insert progress data in mongoDb
        data = {"DSA Topic": topic, "No. of questions solved": solved, "Month": month}
        collection.insert_one(data)

class ChatBot_Functionality:

    def __init__(self):
        self.chat_collection = db["tbl_chat_history"]

    def save_chat(self, user_id, user_name, user_input, bot_response):
        """ Store chat messages in MongoDB """
        chat_data = {
            "user_id": user_id,
            "user_name": user_name,
            "user_message": user_input,
            "bot_response": bot_response,
            "timestamp": pd.Timestamp.now()
        }
        self.chat_collection.insert_one(chat_data)

    def call_llm(self, prompt):
        os.environ["GROQ_API_KEY"] = "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"

        headers = {
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json",
        }
        data = {
            # "model": "mixtral-8x7b-32768",
            "model": "llama3-70b-8192",  # ,Example Groq model; adjust as needed
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.json()}"


    def chat_assistance(self, query, user_id, user_name):

        # Call LLM
        prompt = f"""
You are expert in Data Structure and Algorithm concepts. Give response to user query in DSA.
user query : {query}

Do not give additional comments.
"""
        # If not present then call LLM
        response = self.call_llm(prompt= prompt)

        self.save_chat(user_id, user_name, query, response)

        return response


    def process_charts(self):
        obj = ChatBot()
        df = obj.data_frames()

        prompt = f"""
        Provide summary in detail according to the below dataframe. Also provide i which area I need to focus on. 

Dataframe: {df}

Output in below format - 
Overview: <overview>

Weak Area: [<weak_topics>]

Strong Area: [< strong_topics>]

Strictly note that do not provide additional comments and also output should be in output format.
"""
        summary = self.call_llm(prompt)
        return df, summary

    def progress(self):
        df, summary = self.process_charts()

        dsa_list = ["Array", "Linked List", "Stack", "Queue","Tree", "Graph", "Sorting","Searching","Dynamic Programming", "Quick Sort",
                    "Merge Sort","Insertion Sort","Bubble Sort","Linear Searching","Binary Searching","Time Complexity","Space Complexity"]

        completed_topic = []
        pending_topic = []
        for topic in dsa_list:
            if topic in df["DSA Topic"].to_list() and topic not in completed_topic:
                completed_topic.append(topic)
            elif topic not in pending_topic:
                pending_topic.append(topic)


        # Provides weak areas and strong areas
        weak_area = "Dynamic Programming"
        strong_area = "Array"

        return strong_area, weak_area, [completed_topic, pending_topic]

    def solve_coding(self, topic):
        prompt= f"""Suggest me 5 coding problem to solve for the below topic. Add links from Leetcode, Codechefs, Hackerank coding platfroms.
Topic : {topic}

Strictly note that do not give additional comments.
"""
        response = self.call_llm(prompt=prompt)
        return response
