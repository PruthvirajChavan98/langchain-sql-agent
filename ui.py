import streamlit as st
import requests
import pandas as pd

# API base URL (replace with your actual API URL)
API_BASE_URL = "http://localhost:8000"  # Replace with the FastAPI URL

def execute_query(db_uri, query):
    # Endpoint to execute query
    url = f"{API_BASE_URL}/execute_query/"
    payload = {
        "db_uri": db_uri,
        "query": query
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error executing query.")
        return None

def generate_plot(task_id):
    # Endpoint to generate the plot
    url = f"{API_BASE_URL}/generate_plot/{task_id}"
    response = requests.post(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error generating plot.")
        return None

# Streamlit UI
st.title("Data Query and Plot Generator")

# Input Fields for the user to provide query parameters
db_uri = st.text_input("Database URI", type="password")
query = st.text_area("Natural Language Query")

# Step 1: Execute the query and get the task ID
if st.button("Ask"):
    if db_uri and query:
        result = execute_query(db_uri, query)
        if result:
            task_id = result.get("task_id")
            st.session_state.task_id = task_id
            st.session_state.query_result = result.get("result")
            st.session_state.query_data = result.get("query_data")
            st.session_state.query = result.get("executed_query")
    else:
        st.error("Please provide both Database URI and Query.")

# Step 2: Display the query result from session state if it exists
if 'query_result' in st.session_state:
    st.write("Natural Language Response:")
    st.markdown(f"```text\n{st.session_state.query_result}\n```")

if 'query' in st.session_state:
    st.write("Executed Query:")
    st.markdown(f"```sql\n{st.session_state.query}\n```")

if 'query_data' in st.session_state:
    query_df = pd.DataFrame(st.session_state.query_data)
    st.write("Tabular Result:")
    st.dataframe(query_df)  # Display data in a tabular format
    

# Step 3: Generate plot after query is executed
if 'task_id' in st.session_state:
    task_id = st.session_state.task_id
    if st.button("Generate Plot"):
        plot_result = generate_plot(task_id)
        if plot_result:
            # Save base64 plot string to session state
            st.session_state.plot_base64 = plot_result.get("plot_base64")
            
            # Success message
            st.success("Plot generated successfully!")
            
            # Display the plot immediately after generation
            image_data = st.session_state.plot_base64
            st.image(f"data:image/png;base64,{image_data}", caption="Generated Plot", use_container_width=True)
