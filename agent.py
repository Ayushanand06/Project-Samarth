import pandas as pd
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import config
import data_loader

@tool
def query_rainfall_and_crops(states: list[str], start_year: int, end_year: int, top_m: int) -> str:
    """
    Compares average annual rainfall and lists top M most produced crops FOR A LIST OF STATES over a range of years.
    Rainfall data is available from 1901-2017. Crop data from 1997-2020.
    """
    df_rain = data_loader.get_rainfall_data()
    df_prod = data_loader.get_agriculture_data()

    if df_rain.empty or df_prod.empty:
        return 

    years = list(range(start_year, end_year + 1))
    query_states_upper = [s.upper() for s in states]

    # --- Rainfall Calculation ---
    rain_results = []
    for state in states:
        subdivisions = config.STATE_TO_SUBDIVISION_MAPPING.get(state.upper())
        if not subdivisions: continue
        
        df_rain_filtered = df_rain[df_rain['SUBDIVISION'].isin(subdivisions) & df_rain['YEAR'].isin(years)]
        if not df_rain_filtered.empty:
            avg_rain = df_rain_filtered.groupby('YEAR')['ANNUAL'].mean().reset_index()
            rain_results.append(f"#### Average Annual Rainfall for {state.title()} (mm)\n{avg_rain.to_markdown(index=False)}")

    # --- Crop Calculation (STATE-LEVEL AGGREGATION) ---
    df_prod_filtered = df_prod[df_prod['STATE_NAME'].isin(query_states_upper) & df_prod['CROP_YEAR'].isin(years)]
    if df_prod_filtered.empty:
        crop_results_md = "No crop production data found for the specified criteria."
    else:
        top_crops = (df_prod_filtered.groupby(['STATE_NAME', 'CROP'])['PRODUCTION']
                     .sum().reset_index()
                     .sort_values('PRODUCTION', ascending=False)
                     .groupby('STATE_NAME').head(top_m))
        crop_results_md = f"#### Top {top_m} Produced Crops (Total Tonnes over period)\n{top_crops.to_markdown(index=False)}"

    # --- Combine and Format the Final Response ---
    final_response = (
        "Here is the analysis based on the available data:\n\n"
        f"**--- Rainfall Comparison ({start_year}-{end_year}) ---**\n"
        f"{' '.join(rain_results) if rain_results else 'No rainfall data found for the specified criteria.'}\n"
        f"*Source: Sub-Division Wise Rainfall Data - Local CSV*\n\n"
        f"**--- Crop Production Comparison ({start_year}-{end_year}) ---**\n"
        f"{crop_results_md}\n"
        f"*Source: Crop Production Statistics of India - Local CSV*"
    )
    
    return final_response

def create_agent_executor():
    llm = ChatOpenAI(model=config.GROQ_MODEL_NAME, temperature=0, api_key=config.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    tools = [query_rainfall_and_crops]
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a data analyst for Indian agriculture. You have one powerful tool, `query_rainfall_and_crops`, to answer user questions by synthesizing data from multiple sources. You can handle state-level comparisons over multiple years."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt_template)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
