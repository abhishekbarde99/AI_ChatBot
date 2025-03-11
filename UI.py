from http.client import responses

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from streamlit import graphviz_chart
from faiss_search import Document_Handling
# import graphviz


from login import LoginApp
from streamlit_agraph import agraph, Node, Edge, Config



# from Tools.scripts.verify_ensurepip_wheels import print_notice

from main import ChatBot, ChatBot_Functionality
import numpy as np

class UI:
    def __init__(self):

        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content":"Hey What's up!"}]

        if "coding_messages" not in st.session_state:
            st.session_state["coding_messages"] = []

        if "user_coding" not in st.session_state:
            st.session_state.user_coding = None

        if "button" not in st.session_state:
            st.session_state["button"] = None

        if "is_logged_in" not in st.session_state:
            st.session_state.is_logged_in = False
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if "user_name" not in st.session_state:
            st.session_state.user_name = None

        if "history_loaded" not in st.session_state:
            st.session_state.history_loaded = False

        if "awaiting_topic" not in st.session_state:
            st.session_state.awaiting_topic = True
        if "chat_enabled" not in st.session_state:
            st.session_state.chat_enabled=False


    def sidebar_button(self):
        st.sidebar.title("Personal Assistance AI ChatBot")
        st.sidebar.title(f"Welcome, {st.session_state.user_name} 👋")
        button = st.sidebar.radio(label="Select Functionality",
                                  options=["Chat Assistance", "DSA Topics", "View Progress",
                                           "Coding Recommendation","Logout"])

        st.session_state.button = button
        return button


    def load_previous_chat_history(self):
        """Fetch chat history from the database and update session state."""
        app = LoginApp()
        chat_history = app.get_chat_history(st.session_state.user_id)

        if chat_history:
            st.session_state.history_loaded = True
            st.session_state.messages = [{"role": "assistant", "content": "Here is your previous chat history:"}]
            for chat in chat_history:
                if isinstance(chat, dict):
                    user_msg = chat.get("user_message", "N/A")
                    bot_msg = chat.get("bot_response", "N/A")
                    st.session_state.messages.append({"role": "user", "content": user_msg})
                    st.session_state.messages.append({"role": "assistant", "content": bot_msg})
            st.success("Chat history loaded successfully!")
        else:
            st.warning("No previous chat history found.")

    def chat_assistance(self, user_input , user_id, user_name):
        faiss_obj = Document_Handling()
        best_match, similarity = faiss_obj.search_faiss_index(user_input)

        if best_match:
            # Check in Faiss
            response = best_match
            # self.save_chat(user_id, user_name, user_input, response)

        else:
            obj = ChatBot_Functionality()
            response = obj.chat_assistance(query = user_input, user_id = user_id, user_name=user_name)
        return response

    def view_progress(self):
        obj = ChatBot_Functionality()
        df = obj.process_charts()
        return df

    def coding_recommendation(self, user_input):
        obj = ChatBot_Functionality()
        response = obj.solve_coding(topic = user_input)
        return response

    def run_ui(self):

        if not st.session_state.is_logged_in:
            st.title("Login")

            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                app = LoginApp()
                user_data = app.store_user_data(full_name, username, password)

                if isinstance(user_data, list) and len(user_data) > 0:
                    user_data = user_data[0]  # ✅ Take the first user record if it's a list

                if user_data and isinstance(user_data, dict):
                    st.session_state.is_logged_in = True
                    st.session_state.user_id = str(user_data["user_id"])
                    # Store user ID
                    st.session_state.user_name = user_data["user_name"]  # Store Name

                else:
                    st.error("Login failed. Check your username and password.")
                    st.session_state.is_logged_in = False
        else:

            button = self.sidebar_button()

            if button == "Chat Assistance":
                st.title("Chat")

                if not st.session_state.history_loaded:
                    if st.button("Previous Chat History"):
                        self.load_previous_chat_history()
                        st.rerun()

                st.markdown(
                    """
                    <style>
                        .st-emotion-cache-janbn0 {
                            flex-direction: row-reverse;
                            text-align: right;
                            margin-left: auto;
                            width: 100%;
                            max-width :50%;
                            border-radius: 10px
                    }
                    .st-emotion-cache-10ffz5o{
                            width: fit-content;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                # Chat history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"], avatar="user" if message["role"] == "user" else "assistant"):
                        st.write(message["content"])

                user_input = st.chat_input(placeholder="Write your query")
                if user_input:
                    # result = self.chat_assistance(user_input)
                    with st.chat_message("user", avatar="user"):
                        st.write(user_input)

                    with st.spinner("Processing ..."):
                        result = self.chat_assistance(user_input, st.session_state.user_id, st.session_state.user_name)

                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.messages.append({"role": "assistant", "content": result})

                    with st.chat_message("assistant", avatar="assistant"):
                        st.write(result)


            if button ==  "DSA Topics":
                st.title("DSA Roadmap")

                # Define nodes (topics)
                nodes = [
                    Node(id="DSA", label="DSA", size=40, color="red"),  # Root node
                    Node(id="Data Structures", label="Data Structures", size=35, color="blue"),
                    Node(id="Algorithms", label="Algorithms", size=35, color="blue"),
                    Node(id="Advanced", label="Advanced", size=35, color="blue"),
                    Node(id="Complexity", label="Complexity", size=35, color="blue"),

                    # Data Structures
                    Node(id="Array", label="Array", size=20, color="green"),
                    Node(id="Linked List", label="Linked List", size=20, color="green"),
                    Node(id="Stack", label="Stack", size=20, color="green"),
                    Node(id="Queue", label="Queue", size=20, color="green"),
                    Node(id="Tree", label="Tree", size=20, color="green"),
                    Node(id="Graph", label="Graph", size=20, color="green"),

                    # Algorithms
                    Node(id="Sorting", label="Sorting", size=20, color="orange"),
                    Node(id="Searching", label="Searching", size=20, color="orange"),

                    # Advanced
                    Node(id="Dynamic Programming", label="Dynamic Programming", size=20, color="green"),

                    # Complexity
                    Node(id="Time Complexity", label="Time Complexity", size=20, color="green"),
                    Node(id="Space Complexity", label="Space Complexity", size=20, color="green"),

                    # Sorting
                    Node(id="Quick Sort", label="Quick Sort", size=20, color="green"),
                    Node(id="Merge Sort", label="Merge Sort", size=20, color="green"),
                    Node(id="Insertion Sort", label="Insertion Sort", size=20, color="green"),
                    Node(id="Bubble Sort", label="Bubble Sort", size=20, color="green"),

                    # Searching
                    Node(id="Linear Searching", label="Linear Searching", size=20, color="green"),
                    Node(id="Binary Searching", label="Binary Searching", size=20, color="green"),
                    ]

                # Define edges (relationships)
                edges = [
                    Edge(source="DSA", target="Data Structures"),
                    Edge(source="DSA", target="Algorithms"),
                    Edge(source="DSA", target="Advanced"),
                    Edge(source="DSA", target="Complexity"),

                    # Data Structures connections
                    Edge(source="Data Structures", target="Array"),
                    Edge(source="Data Structures", target="Linked List"),
                    Edge(source="Data Structures", target="Stack"),
                    Edge(source="Data Structures", target="Queue"),
                    Edge(source="Data Structures", target="Tree"),
                    Edge(source="Data Structures", target="Graph"),

                    # Algorithms connections
                    Edge(source="Algorithms", target="Sorting"),
                    Edge(source="Algorithms", target="Searching"),

                    # Sorting
                    Edge(source="Sorting", target="Quick Sort"),
                    Edge(source="Sorting", target="Merge Sort"),
                    Edge(source="Sorting", target="Insertion Sort"),
                    Edge(source="Sorting", target="Bubble Sort"),

                    # Searching
                    Edge(source="Searching", target="Linear Searching"),
                    Edge(source="Searching", target="Binary Searching"),

                    # Advanced
                    Edge(source="Advanced", target="Dynamic Programming"),

                    # Complexity
                    Edge(source="Complexity", target="Time Complexity"),
                    Edge(source="Complexity", target="Space Complexity"),
                ]

                # Define graph configuration
                config = Config(
                    directed=True,  # Hierarchical flow
                    physics=True,
                    hierarchical=True,
                    height=600,
                    width=800
                )
                # Render the graph
                agraph(nodes=nodes, edges=edges,config = config)

                Cobj = ChatBot_Functionality()
                strong_area, weak_area, progress_list = Cobj.progress()

                if "completed_topics" not in st.session_state:
                    st.session_state.completed_topics =  progress_list[0]

                if "pending_topics" not in st.session_state:
                    st.session_state.pending_topics = progress_list[1]

                # Function to move a topic from pending to completed
                def mark_completed(topic):
                    if topic in st.session_state.pending_topics:
                        st.session_state.pending_topics.remove(topic)
                        st.session_state.completed_topics.append(topic)
                        c_obj = ChatBot()
                        c_obj.insert_progress(topic=topic, solved=1, month="August")
                        st.rerun()  # Refresh UI

                # Display Completed Topics
                st.subheader("✅ Completed Topics")
                if st.session_state.completed_topics:
                    for topic in st.session_state.completed_topics:
                        col1, col2 = st.columns([0.8, 0.2])
                        with col1:
                            st.write(topic)
                        with col2:
                            st.write("Completed")
                else:
                    st.write("No topics completed yet.")

                # Display Pending Topics with option to mark as completed
                st.subheader("⏳ Pending Topics")
                if st.session_state.pending_topics:
                    for topic in st.session_state.pending_topics:
                        col1, col2 = st.columns([0.8, 0.2])
                        with col1:
                            st.write(topic)
                        with col2:
                            if st.button("Mark as Done", key=topic):
                                mark_completed(topic)
                else:
                    st.write("All topics completed! 🎉")


            if button == "View Progress":
                st.title("View Progress")
                df, summary = self.view_progress()
                st.line_chart(df, x = "Month", y = "DSA Topic")
                # st.bar_chart(df, x = "No. of questions solved" , y = "Month")

                st.write(summary)

            if button == "Coding Recommendation":
                st.title("Coding")

                Cobj = ChatBot_Functionality()
                strong_area, weak_area, progress_list = Cobj.progress()

                st.markdown(
                    """
                    <style>
                        .st-emotion-cache-janbn0 {
                            flex-direction: row-reverse;
                            text-align: right;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                with st.chat_message("assistant", avatar="assistant"):
                    st.write("Hi, In which field you want to solve coding problem?")

                if st.session_state.awaiting_topic:
                    options = ["Array", "Linked List", "Stack", "Queue", "Tree", "Graph", "Sorting", "Searching",
                               "Dynamic Programming", "Other"]

                    with st.chat_message("assistant", avatar="assistant"):
                        st.write("Select a coding topic:")
                        selected_topic = st.radio(" ", options, index=None, key="topic_select",horizontal =True)

                    if selected_topic:
                        if selected_topic == "Other":

                            st.session_state.coding_messages.append({"role": "assistant",
                                                                     "content": f"""You can choose to solve from your strong area : "{strong_area}" or from weak area : "{weak_area}" """})

                            # Allow user to input their own topic
                            user_custom_topic = st.text_input("Enter your own topic:")

                            if user_custom_topic:
                                user_msg = f"I want to work on: {user_custom_topic}"
                                st.session_state.coding_messages.append({"role": "user", "content": user_msg})
                                with st.chat_message("user", avatar="user"):
                                    st.write(user_custom_topic)

                                with st.spinner("Processing ..."):
                                    result = self.coding_recommendation(user_custom_topic)

                                st.session_state.coding_messages.append({"role": "assistant", "content": result})

                                with st.chat_message("assistant", avatar="assistant"):
                                    st.write(result)
                                st.session_state.awaiting_topic = False
                                st.session_state.chat_enabled = True
                                st.rerun()

                        else:
                            bot_response = f"Great choice! {selected_topic}"
                            st.session_state.coding_messages.append({"role": "assistant", "content": bot_response})
                            with st.chat_message("user", avatar="user"):
                                st.write(selected_topic)

                            with st.spinner("Processing ..."):
                                result = self.coding_recommendation(selected_topic)

                            st.session_state.coding_messages.append({"role": "assistant", "content": result})

                            with st.chat_message("assistant", avatar="assistant"):
                                st.write(result)
                            st.session_state.awaiting_topic = False
                            st.session_state.chat_enabled = True
                            st.rerun()

                if st.session_state.chat_enabled:

                    for message in st.session_state.coding_messages:
                        with st.chat_message(message["role"],
                                             avatar="user" if message["role"] == "user" else "assistant"):
                            st.write(message["content"])

                    user_input = st.chat_input("Ask me anything...")

                    if user_input:
                        with st.chat_message("user", avatar="user"):
                            st.write(user_input)

                        with st.spinner("Processing ..."):
                            result = self.coding_recommendation(user_input)

                        st.session_state.coding_messages.append({"role": "user", "content": user_input})
                        st.session_state.coding_messages.append({"role": "assistant", "content": result})

                        with st.chat_message("assistant", avatar="assistant"):
                            st.write(result)

                        # st.rerun()

            if button == "Logout":
                st.session_state.clear()
                st.rerun()
