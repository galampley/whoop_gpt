from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
import openai
import requests
import pandas as pd
from dotenv import load_dotenv
import os
# from langchain.tools.python.tool import PythonAstREPLTool
from langchain_experimental.utilities import PythonREPL
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from datetime import datetime
from pandas import json_normalize
from fastapi.middleware.cors import CORSMiddleware

load_dotenv("/Users/galampley/Documents/secrets.env")

openai.api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(    
    openai_api_key=openai.api_key , 
    model_name="gpt-4", 
    temperature=0.0
    )

# app = FastAPI()
query_router = APIRouter()

'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the actual origin you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''

def today_date(query:str) -> str:
    return datetime.now().strftime("%Y-%m-%d")

def fetch_sleep_data(token: str):
    sleep_endpoint_url = 'https://api.prod.whoop.com/developer/v1/activity/sleep'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    all_records = []
    next_token = None

    '''
    df_main = pd.DataFrame()
    df_score = pd.DataFrame()
    df_stage_summary = pd.DataFrame()
    df_sleep_needed = pd.DataFrame()
    df_2 = pd.DataFrame() # moved out of loop for better org
    '''

    while True: 
        response = requests.get(sleep_endpoint_url, headers=headers, params={"nextToken": next_token})
        data = response.json()

        all_records.extend(data['records'])

        next_token = data.get('next_token')

        if not next_token:
            break

    df = pd.json_normalize(all_records)
    df_sleep = df.drop(columns=['score'])
    # print(new_df)
    return(df_sleep)
    '''
    # old version of above
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

        # old version of below
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
        
        # new version of above, handling Nones
        if record['score'] is not None:
            # Normalize and concatenate 'score' data
            temp_df_score = json_normalize(record['score'], sep='_')
            temp_df_score['id'] = record['id']
            df_score = pd.concat([df_score, temp_df_score], ignore_index=True)

            if 'stage_summary' in record['score']:
                temp_df_stage_summary = json_normalize(record['score']['stage_summary'], sep='_')
                temp_df_stage_summary['id'] = record['id']
                df_stage_summary = pd.concat([df_stage_summary, temp_df_stage_summary], ignore_index=True)

            if 'sleep_needed' in record['score']:
                temp_df_sleep_needed = json_normalize(record['score']['sleep_needed'], sep='_')
                temp_df_sleep_needed['id'] = record['id']
                df_sleep_needed = pd.concat([df_sleep_needed, temp_df_sleep_needed], ignore_index=True)

    # old version of below
    df_2 = pd.merge(df_main, df_score, on='id')
    df_2 = pd.merge(df_2, df_stage_summary, on='id')
    df_2 = pd.merge(df_2, df_sleep_needed, on='id')

    # new version of above, check if 'id' column exists in df_main and df_score, then merge; handles Nones
    if 'id' in df_main.columns and 'id' in df_score.columns:
        df_2 = pd.merge(df_main, df_score, on='id', how='outer')

    if 'id' in df_2.columns and 'id' in df_stage_summary.columns:
        df_2 = pd.merge(df_2, df_stage_summary, on='id', how='outer')

    if 'id' in df_2.columns and 'id' in df_sleep_needed.columns:
        df_2 = pd.merge(df_2, df_sleep_needed, on='id', how='outer')
    else:
        # Handle the case where 'id' is missing in one of the DataFrames
        print("Warning: 'id' column missing in one of the DataFrames")

    # Drop duplicate columns, when it WAS necessary but doesn't seem to be anymore
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
    
    # df_sleep = df_2.drop(columns=duplicate_columns)

    # new to replace above, check and filter out columns that actually exist in df_2
    columns_to_drop = [col for col in duplicate_columns if col in df_2.columns]
    df_sleep = df_2.drop(columns=columns_to_drop)

    print("Data fetched:", df_sleep)
    
    return(df_sleep)
    '''

class Query(BaseModel):
    query: str
    token: str 

# @app.post("/query")
@query_router.post("/query")
def handle_query(query: Query):
    print(f"Received query: {query.dict()}")  # Debugging line

    # Prepare data using separate functions
    sleep_data = fetch_sleep_data(query.token)
    # workout_data = fetch_workout_data(query.token)

    if sleep_data is None:
        return {"error": "No sleep data available"}
    
    '''
    python = PythonAstREPLTool(locals={
        "df_sleep": sleep_data
        })
    '''
    '''
    # new version of above given Langchain updates
    python = PythonREPL(locals={
    "df_sleep": sleep_data
    })
    '''

    python = PythonREPL()
    python.globals['sleep_data'] = sleep_data
    
    sleep_data_columns = sleep_data.columns.to_list()

    tools = [
        Tool(
            name = "Whoop Sleep Data",
            func=python.run,
            description = f"""
            Useful for when you need to answer questions about Whoop data stored in pandas dataframe 'sleep_data'. 
            Run python pandas operations on 'sleep_data' to help you get a valid answer. 
            'sleep_data' has the following columns: {sleep_data_columns}.
            
            Each column from 'sleep_data' is defined below between '####'
            
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
            score.stage_summary.total_in_bed_time_milli: Total time in bed in milliseconds.
            score.stage_summary.total_awake_time_milli: Total awake time in milliseconds.
            score.stage_summary.total_no_data_time_milli: Total time with no data in milliseconds.
            score.stage_summary.total_light_sleep_time_milli: Total light sleep time in milliseconds.
            score.stage_summary.total_slow_wave_sleep_time_milli: Total slow-wave sleep time in milliseconds.
            score.stage_summary.total_rem_sleep_time_milli: Total REM sleep time in milliseconds.
            score.stage_summary.sleep_cycle_count: Total number of sleep cycles.
            score.stage_summary.disturbance_count: Total number of disturbances during sleep.
            score.sleep_needed.baseline_milli: Baseline sleep needed in milliseconds.
            score.sleep_needed.need_from_sleep_debt_milli: Additional sleep needed due to sleep debt, in milliseconds.
            score.sleep_needed.need_from_recent_strain_milli: Additional sleep needed due to recent strain, in milliseconds.
            score.sleep_needed.need_from_recent_nap_milli: Sleep needed adjustment due to recent nap, in milliseconds.
            score.respiratory_rate: Rate of breathing while asleep.
            score.sleep_performance_percentage: How well the Whoop User slept.
            score.sleep_consistency_percentage: How consistent the Whoop User slept.
            score.sleep_efficiency_percentage: How efficient the Whoop User slept.
            ####
            """
        ),
        Tool.from_function(
            func = today_date,
            name = "today_date",
            description=f"""
            Useful for when you need to know today's date when querying Whoop Sleep Data. You will need to know today's date if asked a question regarding a 
            target date, like yesterday (last night) or x days/nights ago. You will determine today's date then determine the target date based on logic below. 
            
            Examples of logic between '####'
            
            ####
            If today is 9/22/2023 then yesterday was 9/21/2023. Subtract 1 day.
            If today is 9/22/2023 then 2 (two) days ago was 9/20/2023, 3 days ago was 9/19/2023. So on and so forth through the calendar.
            ####
            """
        )
    ]

    # change the value of the prefix argument in the initialize_agent function. This will overwrite the default prompt template of the zero shot agent type
    agent_kwargs = {'prefix': f'You are friendly fitness assistant. You are tasked to assist the current user on questions related to their personal Whoop data.\
    Whenever dealing with time, convert to minutes and seconds. You have access to the following tools:'}

    # initialize the LLM agent
    agent = initialize_agent(tools, 
                            llm, 
                            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
                            verbose=True, 
                            agent_kwargs=agent_kwargs
                            )
    user_input = query.query 
    response = agent.run(user_input)
    return {"response": response}
    