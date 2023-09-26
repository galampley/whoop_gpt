from fastapi import FastAPI
from pydantic import BaseModel
import openai
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from langchain.tools.python.tool import PythonAstREPLTool
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from datetime import datetime
from pandas import json_normalize
from fastapi.middleware.cors import CORSMiddleware

load_dotenv("/Users/galampley/Documents/secrets.env")

openai.api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(    
    openai_api_key=openai.api_key , 
    model_name="gpt-3.5-turbo", 
    temperature=0.0
    )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the actual origin you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def today_date(query:str) -> str:
    return datetime.now().strftime("%Y-%m-%d")

def fetch_sleep_data(token: str):
    sleep_endpoint_url = 'https://api.prod.whoop.com/developer/v1/activity/sleep'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    all_records = []
    next_token = None

    df_main = pd.DataFrame()
    df_score = pd.DataFrame()
    df_stage_summary = pd.DataFrame()
    df_sleep_needed = pd.DataFrame()

    while True:
        params = {}
        if next_token:
            params["nextToken"] = next_token

        response = requests.get(sleep_endpoint_url, headers=headers, params=params)
        all_data = response.json()

        all_records.extend(all_data.get("records", []))
        next_token = all_data.get("next_token")

        if not next_token:
            break

    for record in all_records:
        temp_df_main = json_normalize(record, sep='_')
        df_main = pd.concat([df_main, temp_df_main])

        temp_df_score = json_normalize(record['score'], sep='_')
        temp_df_score['id'] = record['id']
        df_score = pd.concat([df_score, temp_df_score])

        temp_df_stage_summary = json_normalize(record['score']['stage_summary'], sep='_')
        temp_df_stage_summary['id'] = record['id']
        df_stage_summary = pd.concat([df_stage_summary, temp_df_stage_summary])

        temp_df_sleep_needed = json_normalize(record['score']['sleep_needed'], sep='_')
        temp_df_sleep_needed['id'] = record['id']
        df_sleep_needed = pd.concat([df_sleep_needed, temp_df_sleep_needed])

    df_2 = pd.merge(df_main, df_score, on='id')
    df_2 = pd.merge(df_2, df_stage_summary, on='id')
    df_2 = pd.merge(df_2, df_sleep_needed, on='id')

    # Drop duplicate columns
    duplicate_columns = ['respiratory_rate',
        'sleep_performance_percentage', 'sleep_consistency_percentage',
        'sleep_efficiency_percentage', 'stage_summary_total_in_bed_time_milli',
        'stage_summary_total_awake_time_milli',
        'stage_summary_total_no_data_time_milli',
        'stage_summary_total_light_sleep_time_milli',
        'stage_summary_total_slow_wave_sleep_time_milli',
        'stage_summary_total_rem_sleep_time_milli',
        'stage_summary_sleep_cycle_count', 'stage_summary_disturbance_count',
        'sleep_needed_baseline_milli',
        'sleep_needed_need_from_sleep_debt_milli',
        'sleep_needed_need_from_recent_strain_milli',
        'sleep_needed_need_from_recent_nap_milli', 'total_in_bed_time_milli',
        'total_awake_time_milli', 'total_no_data_time_milli',
        'total_light_sleep_time_milli', 'total_slow_wave_sleep_time_milli',
        'total_rem_sleep_time_milli', 'sleep_cycle_count', 'disturbance_count','baseline_milli',
        'need_from_sleep_debt_milli', 'need_from_recent_strain_milli',
        'need_from_recent_nap_milli']

    df_sleep = df_2.drop(columns=duplicate_columns)
    print("Data fetched:", df_sleep)
    
    return(df_sleep)
     
class Query(BaseModel):
    query: str
    token: str 

@app.post("/query")
def handle_query(query: Query):
    print(f"Received query: {query.dict()}")  # Debugging line

    # Prepare data using separate functions
    sleep_data = fetch_sleep_data(query.token)
    # workout_data = fetch_workout_data(query.token)
    # ... fetch other types of data as needed

    if sleep_data is None:
        return {"error": "No sleep data available"}
    
    python = PythonAstREPLTool(locals={
        "df_sleep": sleep_data,
        # "df_workout": df_workout,
        # "df_recovery": df_recovery,
        # ... add more DataFrames as needed
    })
    
    df_sleep_columns = sleep_data.columns.to_list()
    # df_workout_columns = df_sleep.columns.to_list()

    tools = [
        Tool(
            name = "Whoop Sleep Data",
            func=python.run,
            description = f"""
            Useful for when you need to answer questions about Whoop data stored in pandas dataframe 'df_sleep'. 
            Run python pandas operations on 'df_sleep' to help you get the right answer.
            'df_sleep' has the following columns: {df_sleep_columns}.
            
            Each column ({df_sleep_columns}) from 'df_sleep' is defined below between '####'
            
            ####
            id: Unique identifier for the sleep activity.
            user_id: The WHOOP User who performed the sleep activity.
            created_at: The time the sleep activity was recorded in WHOOP.
            updated_at: The time the sleep activity was last updated in WHOOP.
            start: Start time bound of the sleep. Represented as ISO 8601 timestamp.
            end: End time bound of the sleep. Represented as ISO 8601 timestamp.
            timezone_offset: The user's timezone offset at the time the sleep was recorded.
            nap: If true, this sleep activity was a nap for the user.
            score_state: The scoring state of the sleep activity. (Enum values: SCORED, PENDING_SCORE, UNSCORABLE)
            score_stage_summary_total_in_bed_time_milli: Total time in bed in milliseconds.
            score_stage_summary_total_awake_time_milli: Total awake time in milliseconds.
            score_stage_summary_total_no_data_time_milli: Total time with no data in milliseconds.
            score_stage_summary_total_light_sleep_time_milli: Total light sleep time in milliseconds.
            score_stage_summary_total_slow_wave_sleep_time_milli: Total slow-wave sleep time in milliseconds.
            score_stage_summary_total_rem_sleep_time_milli: Total REM sleep time in milliseconds.
            score_stage_summary_sleep_cycle_count: Total number of sleep cycles.
            score_stage_summary_disturbance_count: Total number of disturbances during sleep.
            score_sleep_needed_baseline_milli: Baseline sleep needed in milliseconds.
            score_sleep_needed_need_from_sleep_debt_milli: Additional sleep needed due to sleep debt, in milliseconds.
            score_sleep_needed_need_from_recent_strain_milli: Additional sleep needed due to recent strain, in milliseconds.
            score_sleep_needed_need_from_recent_nap_milli: Sleep needed adjustment due to recent nap, in milliseconds.
            score_respiratory_rate: Rate of breathing while asleep.
            score_sleep_performance_percentage: How well the Whoop User slept.
            score_sleep_consistency_percentage: How consistent the Whoop User slept.
            score_sleep_efficiency_percentage: How efficient the Whoop User slept.
            ####
            
            Example below between '####'
            
            ####
            <user>: What was my total baseline sleep needed, from 8/28/23 to 9/2/23, in hours?
            <assistant>: df[["score_sleep_needed_baseline_milli"]
            <assistant>: You're total baseline sleep needed was n 
            ####
            """
        ),
        Tool.from_function(
            func = today_date,
            name = "today_date",
            description=f"""
            Useful for when you need to know today's date when querying Whoop Sleep Data. Use to filter 'df_sleep' to a relevant subset. 
            'start' and 'end' date values in 'df_sleep' are of format ISO 8601 and look like this for example, '2023-08-29T13:26:21.600Z'. You will need to convert
            to match user query format with 'df_sleep' format.
            
            Examples of logic between '####'
            
            ####
            If today is 9/22/2023 then yesterday was 9/21/2023. 
            If today is 9/22/2023 then 2 (two) days ago was 9/20/2023, 3 days ago was 9/19/2023. So on and so forth through the calendar.
            ####
            """
        )
    ]

    # change the value of the prefix argument in the initialize_agent function. This will overwrite the default prompt template of the zero shot agent type
    agent_kwargs = {'prefix': f'You are friendly fitness assistant. You are tasked to assist the current user on questions related to their personal Whoop data. You have access to the following tools:'}
   
    # initialize the LLM agent
    agent = initialize_agent(tools, 
                            llm, 
                            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
                            verbose=True, 
                            agent_kwargs=agent_kwargs
                            )
    user_input = query.query 
    response = agent.run(user_input)
    # print("Returning this response:", {"response": response})  # Debugging line
    return {"response": response}
    