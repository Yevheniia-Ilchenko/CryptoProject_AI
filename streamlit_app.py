import streamlit as st
import json
from extract_data import get_project_data
from open_ai import ask_assistant

from transform_data import format_data, group_by_category, filter_status, search_project
import os
import pandas as pd


def ensure_data_exists():

    """
    Ensures data files exist. If missing, fetches and saves the data.
    """

    if not os.path.exists("formatted_projects.json"):
        st.info("No data found. Fetching data...")
        update_and_prepare_data()
    else:

        try:
            with open("formatted_projects.json", "r") as f:
                formatted_projects = json.load(f)
                last_updated = formatted_projects[0].get("last_updated", "Unknown")
            st.success(f"Data already exists. Last updated on: {last_updated}")
        except Exception as e:
            st.error(f"Error reading update date: {e}")


def update_and_prepare_data():

    """
        Fetches data for a predefined list of project IDs from the API, processes it,
        and saves the raw and formatted data into JSON files.
    """

    project_ids = [3, 20, 17, 100, 150]
    projects = []

    for dapp_id in project_ids:
        data = get_project_data(dapp_id)
        if data:
            projects.append(data)

    if not projects:
        st.error("No projects were fetched from the API.")
        return

    with open("raw_data.json", "w") as f:
        json.dump(projects, f, indent=4)

    formatted_projects = [format_data(project) for project in projects]
    with open("formatted_projects.json", "w") as f:
        json.dump(formatted_projects, f, indent=4)


def prepare_dataframe():

    """
    Loads and prepares the formatted_projects.json file into a DataFrame.

    """

    try:
        df = pd.read_json("formatted_projects.json")

        df["short_description"] = df["description"].apply(lambda x: x.get("short", "") if isinstance(x, dict) else "")
        df["full_description"] = df["description"].apply(lambda x: x.get("full", "") if isinstance(x, dict) else "")

        df["website"] = df["links"].apply(lambda x: x.get("website", ""))
        df["discord"] = df["links"].apply(lambda x: x["social"].get("discord", "") if "social" in x else "")
        df["telegram"] = df["links"].apply(lambda x: x["social"].get("telegram", "") if "social" in x else "")
        df["twitter"] = df["links"].apply(lambda x: x["social"].get("twitter", "") if "social" in x else "")

        df["chains"] = df["requirements"].apply(lambda x: x[0].get("chains", []) if isinstance(x, list) else [])
        df["balance"] = df["requirements"].apply(lambda x: x[0].get("balance", 0) if isinstance(x, list) else 0)

        df = df.drop(columns=["links", "description", "requirements"])
        return df
    except FileNotFoundError:
        st.error("Formatted data file not found. Please update the data.")
        return pd.DataFrame()


def streamlit_interface():

    """
        Provides a user interface for the Crypto Projects Dashboard using Streamlit.

    Sidebar Functionality:
    - Filter by project status.
    - Search for projects by keyword.
    - Update data with a button click.
    - Download filtered data as a CSV file.

    Main Page:
    - Displays a filtered DataFrame of projects.
    - Provides an AI Assistant to answer project-related queries:
        - Initiates a conversation using Streamlit's session state.
        - Stores and displays chat history.
        - Sends user input to the AI assistant via the `ask_assistant` function.
    - Displays a bar chart of projects grouped by category.
    """

    st.set_page_config(layout="wide")
    ensure_data_exists()

    st.sidebar.header("Filters")
    status = st.sidebar.selectbox("Project status:", ["active", "ended"])
    search_keyword = st.sidebar.text_input("Search projects by keyword:")

    df = prepare_dataframe()
    filtered_data = filter_status(status, df)

    if search_keyword:
        filtered_data = search_project(search_keyword, filtered_data)

    if st.sidebar.button("Update Data"):
        st.info("Updating data ...")
        update_and_prepare_data()
        with open("formatted_projects.json", "r") as f:
            formatted_projects = json.load(f)
            last_updated = formatted_projects[0].get("last_updated", "Unknown")
        st.success(f"Data updated! {last_updated} ")

    st.sidebar.download_button(
        label="Download Filtered Data",
        data=filtered_data.to_csv(index=False),
        file_name="filtered_projects.csv",
        mime="text/csv",
    )

    st.title("Crypto Projects Dashboard")

    st.subheader("Filtered Projects")
    st.dataframe(filtered_data, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("AI Assistant")

        if 'greeted' not in st.session_state:
            st.session_state.greeted = False
        if 'greeting_messages' not in st.session_state:
            st.session_state.greeting_messages = [
                {"role": "system",
                 "content": "Hi! I can help you with questions about the crypto project. How can I help you today?"}
            ]
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if not st.session_state.greeted:
            st.session_state.greeted = True
            for msg in st.session_state.greeting_messages:
                role = "Assistant" if msg['role'] == "system" else msg['role'].capitalize()
                st.write(f"{role}: {msg['content']}")

        user_input = st.text_input("You: ", key="input")

        if st.button("Send"):
            if user_input:
                response = ask_assistant(user_input)
                st.session_state.chat_history.append((user_input, response))

        if st.session_state.chat_history:
            st.write("### Chat History")
            for question, answer in reversed(st.session_state.chat_history):
                st.write(f"**You:** {question}")
                st.write(f"**Assistant:** {answer}")
    with col2:

        st.subheader("Projects by Category")
        category_counts = group_by_category(filtered_data)
        st.bar_chart(category_counts)


def main():
    streamlit_interface()


if __name__ == "__main__":
    main()

