
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

from langchain.chains import LLMMathChain
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from dotenv import load_dotenv
import time
from openai import RateLimitError
import os
import openai


# Load environment variables from the .env file
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')


db = SQLDatabase.from_uri("sqlite:///Chinook.db")



llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    openai_api_key=openai_api_key,
    verbose=True,
)

#MEMORY
memory = ConversationBufferMemory(memory_key="memory", return_messages=True)


import re
class CleanSQLDatabaseChain(SQLDatabaseChain):
    def _strip_markdown(self, sql: str) -> str:
        """Remove triple backticks and 'sql' language hints."""
        return re.sub(r"```(?:sql)?|```", "", sql).strip()
    
    def _call(self, inputs: dict, run_manager=None):
        # Get the response from the LLM as usual
        response = super()._call(inputs, run_manager)
        
        # Clean the SQL query before execution
        if 'sql_cmd' in response:
            response['sql_cmd'] = self._strip_markdown(response['sql_cmd'])
        
        return response
    def sql_database_run(self, query: str) -> str:
        """Override the SQL execution to clean SQL before executing."""
        clean_query = self._strip_markdown(query)
        print(f"[Executing SQL]: {clean_query}")  # Debug
        return self.sql_database.run(clean_query)
    
    def run(self, input: str) -> str:
        response = super()._call({"query": input})
        
        if 'sql_cmd' in response:
            response['sql_cmd'] = self._strip_markdown(response['sql_cmd'])

        return response['result']  # This is what .run() is expected to return



# class CustomQuerySQLDataBaseTool(QuerySQLDataBaseTool):
#     def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Union[str, Sequence[Dict[str, Any]], Result]:
#         # Clean up the query by removing triple backticks
#         cleaned_query = query.strip("```sql\n").strip("\n```")
#         return self.db.run_no_throw(cleaned_query)

#Connect SQL database chain

# db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, memory=memory)

db_chain = CleanSQLDatabaseChain.from_llm(llm, db, verbose=True)
# db_chain._sql_database.run = db_chain.sql_database_run  # 🔧 Add this line
# Override the run method with the cleaned one
# db_chain.sql_database.run = db_chain.sql_database_run


llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)


serpapi_api_key = os.getenv('SERPAPI_API_KEY')
search = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)

def cleaned_sql_executor(query: str) -> str:
    cleaned_query = clean_sql_code(query)
    print(f"[Executing cleaned SQL]: {cleaned_query}")  # Optional debug
    return db.run(cleaned_query)  # ✅ FIXED: call the method with the query

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math",
    ),
    Tool(
        name="FooBar-DB",
        func=db_chain.run,
        description="useful for when you need to answer questions about FooBar. Input should be in the form of a question containing full context",
    ),
    Tool(
        name="SQLExecutor",
        func=cleaned_sql_executor,
        description="Executes SQL queries on the Chinook database."
    )
]




agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
}


agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
)



def clean_sql_code(sql: str) -> str:
    # Strip markdown-style code blocks like ```sql ... ```
    return re.sub(r"^```(?:sql)?\s*|```$", "", sql.strip(), flags=re.MULTILINE)
 



# Define the handle_chat function

def handle_chat(query, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = agent.invoke({"input": query})
            return response
        except RateLimitError:
            print(f"[Retry {attempt+1}] Rate limit hit. Waiting {delay} seconds...")
            time.sleep(delay)
    raise Exception("Rate limit exceeded after multiple retries.")



ONE_MILLION = 1000000
def calculate_cost(query, model, response):
    prompt = query.strip()
    num_input_token = len(prompt.split())
    num_output_token = len(response['output'].split())
    if model == 'gpt-4o-mini':
        return (0.6*num_input_token/ONE_MILLION) + (2.4*num_output_token/ONE_MILLION)
    elif model == 'gpt-4o':
        return (5*num_input_token/ONE_MILLION) + (20*num_output_token/ONE_MILLION)
    

# %%


# %%
# Example usage 01
# query = 'How many Artists are there in our database?'
# response = handle_chat(query)
# print(response) 
# query2 = 'Select * from Artist where ArtistId = 1'
# response2 = handle_chat(query2)
# print(response2) 
# cost = calculate_cost(query, llm.model_name ,response)
# print("Cost of this prompt: " + str(cost) )



# query = "How many artists are there in our database?"
# response = handle_chat(query)
# print(response)

# %% [markdown]
# UI For Chatbot

# %%

#testikng
