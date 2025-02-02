# Data Query and Plot Generator Project

## Overview

The **Data Query and Plot Generator** project is a web-based application that allows users to interact with a database, execute SQL queries, and visualize the results as plots. It uses **FastAPI** for the backend API, **Streamlit** for the front-end user interface, and **LangChain** for natural language query interpretation and plot generation.

Users can:
1. Execute SQL queries on their databases using natural language.
2. Automatically generate plots based on the query result.
3. View the results and plots in an interactive web UI.

---

## Components

### Backend

- **FastAPI**: Provides the API for executing SQL queries and generating plots.
- **SQLAlchemy**: Used to connect to and execute queries on the database.
- **LangChain**: Processes the query results and generates Python code for plotting using natural language.
- **Matplotlib**: Used to generate plots.
- **dotenv**: Loads environment variables such as database credentials and API keys.

### Frontend

- **Streamlit**: Provides an interactive web interface to the user.
- **Pandas**: Used to display query results in a tabular format on the frontend.
- **Requests**: Sends HTTP requests to the FastAPI backend from the Streamlit frontend.

---

## Setup

### Prerequisites

- Python 3.8+
- Required libraries (listed below in the Installation section)
- A running database instance (e.g., PostgreSQL) with accessible credentials.
- OpenAI access for generating structured output from the LangChain model.

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/PruthvirajChavan98/langchain-sql-agent.git
   cd langchain-sql-agent
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   .\venv\Scripts\activate   # For Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the project root directory and add the necessary variables for OpenAI API access.

   Example `.env` file:

   ```
   OPENAI_API_KEY=<your_api_key>
   ```

5. **Database configuration:**

   - Ensure your database (e.g., PostgreSQL) is up and running.
   - Provide the database URI when prompted on the frontend.

---

## Running the Application

1. **Start the FastAPI server:**

   ```bash
   uvicorn main:app --reload
   ```

   The FastAPI backend will run on `http://localhost:8000`.

2. **Start the Streamlit frontend:**

   ```bash
   streamlit run ui.py
   ```

   The Streamlit UI will run on `http://localhost:8501`.

---

## How It Works

### Step 1: Execute a Query
The user provides:
- **Database URI** (e.g., `postgresql://username:password@localhost:5432/dbname`).
- **Natural Language Query** (e.g., "Show me the sales data for the last month.").

The backend receives the query, invokes the **LangChain** model, and uses **SQLAlchemy** to execute the translated SQL query.

### Step 2: View Query Result
Once the query is executed, the results are displayed in the frontend in a tabular format using **Pandas**. The user can also see the raw SQL query that was executed.

### Step 3: Generate Plot
Based on the query result, the LangChain model generates the necessary Python code for plotting (using **Matplotlib**). The backend executes the code, generates the plot in memory, and sends the plot image back to the frontend in base64 format.

The user can then view the plot on the UI.

---

## API Endpoints

### 1. **POST /execute_query/**
Executes an SQL query on the provided database URI.

**Request Body:**
```json
{
  "db_uri": "your_database_uri",
  "query": "your_sql_query"
}
```

**Response:**
```json
{
  "task_id": "unique_task_id",
  "executed_query": "sql_query_executed",
  "result": "natural_language_result",
  "query_data": [
    {"column1": "value1", "column2": "value2", ...}
  ]
}
```

---

### 2. **POST /generate_plot/{task_id}**
Generates a plot based on the query results and the task ID.

**Request:**
- `task_id` (required): The ID of the task returned from the `/execute_query/` endpoint.

**Response:**
```json
{
  "task_id": "unique_task_id",
  "plot_base64": "base64_encoded_image_data"
}
```

The `plot_base64` field contains the generated plot in base64 format.

---

## UI Interaction

### Query Input
The user provides:
1. **Database URI**: The URI to their database.
2. **Query**: A natural language query.

After clicking the **Ask** button, the query is executed on the backend.

### Query Result Display
The query results are displayed in:
- A **natural language response** (from the LangChain model).
- The **executed SQL query**.
- A **tabular view** of the query result (using Pandas DataFrame).

### Plot Generation
After query execution, the user can click **Generate Plot**, which triggers the backend to generate a plot. The plot is displayed in the UI.

---

## Troubleshooting

- **Error executing query**: Check the database URI and ensure the database is accessible.
- **Plot not generated**: Ensure the LangChain model is configured correctly and the data returned by the query is suitable for plotting.
- **Environment variables**: Ensure that the `.env` file is correctly configured with your OpenAI API credentials.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- **FastAPI**: For creating a fast and efficient backend API.
- **Streamlit**: For building a simple, interactive web frontend.
- **LangChain**: For natural language processing and structured output generation.
- **Matplotlib**: For creating visualizations from query data.
