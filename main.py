import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend to avoid plot window opening

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import uuid
import io
import base64
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    """Model for executing SQL queries."""
    db_uri: str  # User must provide this in every request
    query: str

# LLM Configuration
llm = ChatOpenAI(
    model="gpt-4o"
)

# Define your desired data structure using Pydantic
class CoderPlot(BaseModel):
    appropriate_plot_name: str = Field(description="from given data given the name of appropriate plot (graph)")
    python_code_to_plot: str = Field(description="python (seaborn) code to plot the plot and save the plot as temp_plot.png")

structured_llm = llm.with_structured_output(CoderPlot)


# Store ongoing tasks (for illustration purposes, could be persisted)
ongoing_tasks = {}

@app.post("/execute_query/")
def execute_query(request: QueryRequest):
    """Execute an SQL query using the provided database URI."""

    task_id = str(uuid.uuid4())  # Generate a unique task ID for the request
    try:
        db = SQLDatabase.from_uri(request.db_uri)

        agent_executor = create_sql_agent(
            llm,
            db=db,
            suffix="YOU MUST ONLY USE SELECT QUERIES, NO OTHER THAN THAT!!!"
            "Note: USE 'postgresql' syntax",
            agent_type="openai-tools",
            verbose=True,
            agent_executor_kwargs={
                "return_intermediate_steps": True,
                "handle_parsing_errors": True
            }
        )

        result = agent_executor.invoke(request.query)

        print(result)

        # Ensure 'intermediate_steps' exists and is not empty
        if "intermediate_steps" in result and result["intermediate_steps"]:
            last_step = result["intermediate_steps"][-1]
            # print("last step >>>>>> ", last_step)

            # Ensure last_step contains a valid structure before accessing attributes
            if isinstance(last_step, tuple) and len(last_step) >= 2:
                executed_query = last_step[0].tool_input.get("query", "")
                
                # Validate the executed query before attempting to execute it
                if not executed_query.strip():
                    raise HTTPException(status_code=400, detail="Invalid SQL query")

                engine = create_engine(request.db_uri)
                with engine.connect() as conn:
                    with conn.begin():
                        executed_result = conn.execute(text(executed_query))
                        # Extract column names and rows
                        column_names = executed_result.keys()
                        data = [dict(zip(column_names, row)) for row in executed_result]

                # Store the intermediate data for later
                ongoing_tasks[task_id] = {
                    "executed_query": executed_query,
                    "result": result['output'],
                    "query_data": data,
                }
                return {
                    "task_id": task_id,
                    "executed_query": executed_query,
                    "result": result['output'],
                    "query_data": data,
                }

        # Default response when intermediate_steps is missing or empty
        return {
            "result": result,
            "message": "No intermediate steps found, raw response returned"
        }
    
    except Exception as e:
        raise e


# Define the endpoint to generate the plot
@app.post("/generate_plot/{task_id}")
async def generate_plot(task_id: str):
    # Check if the task exists
    if task_id not in ongoing_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = ongoing_tasks[task_id]
    data = task_data["query_data"]

    structured_result = structured_llm.invoke(str(data))

    # Assuming `structured_result.python_code_to_plot` contains the plotting code
    print(structured_result.python_code_to_plot)
    exec(structured_result.python_code_to_plot)

    # Plot generation in memory (no window will open)
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")  # Save directly to buffer, no GUI
    buffer.seek(0)

    # Encode the image as base64
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Update task with the plot data
    ongoing_tasks[task_id]["plot_base64"] = img_base64

    return {"task_id": task_id, "plot_base64": img_base64}
