import streamlit as st
from pymongo import MongoClient
from urllib.parse import quote_plus


class LoginApp:
    def __init__(self):

        username = "abhibarde1799"
        password = "iYa4ab7P3FtuTMlh"
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)

        self.client = MongoClient(f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.kfkd7.mongodb.net/mydatabase?retryWrites=true&w=majority")   # MongoDb Connection String
        self.db = self.client["AI_ChatBot"]
        # self.collection = self.db["tbl_userDetails"]
        self.user_collection = self.db["tbl_userDetails"]
        self.chat_collection = self.db["tbl_chat_history"]

    def authenticate_user(self, username, password):
        """ Check if username & password match in DB """
        user = self.user_collection.find_one({"username": username, "password": password}, {"_id": 1, "full_name": 1})
        return user

    def get_chat_history(self, user_id):
        """ Fetch chat history for the logged-in user """
        chat_data = list(self.chat_collection.find({"user_id": user_id}, {"_id": 0}))
        return chat_data

    def store_user_data(self, full_name, username, password):
        """ Handle both Login & Registration """
        user = self.authenticate_user(username, password)

        if user:
            # ✅ User exists → Fetch chat history
            st.session_state.user_id = str(user["_id"])
            st.session_state.user_name = user["full_name"]
            st.session_state.is_logged_in = True

            chat_history = self.get_chat_history(st.session_state.user_id)
            return chat_history
        else:
            # ❌ User does NOT exist → Register them
            new_user = {"full_name": full_name, "username": username, "password": password}
            inserted_user = self.user_collection.insert_one(new_user)

            st.session_state.user_id = str(inserted_user.inserted_id)
            st.session_state.user_name = full_name
            st.session_state.is_logged_in = True

            return []