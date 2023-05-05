import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import time
import os

openai.api_key = os.environ['OPENAI_API_KEY']

@st.cache(allow_output_mutation=True)
def get_input_list():
    return []

history = get_input_list()

def show_progress_bar(delay: int) -> None:
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(delay / 100)
        progress_bar.progress(i + 1)

def post_process_response(response: str) -> str:
    response = response.replace("```python", "")
    response = response.replace("fig.show()", "")
    response = response.replace("```", "")

    return response


def request_plotly_code(history) -> str:
    messages = [
                {"role": "system", "content": """You are Flomaster, a data visualization assistant. I will give you information about my data
and will tell you what chart I want you to plot. In response you will provide me Python code
form the Plotly package will will produce my desired chart. You will not use any other
package apart from Plotly Python. Sometimes I may give you exact chart name. In those
cases you will use your best knowledge to decide on the best possible chart to produce. I will
also provide you feedback on what I like or what I do not like in the chart. You will modify your
response accordingly to fit my desires.
My input will look like this:
Data: [NECESSARY INFORMATION ON MY DATA]
Ask: [MY REQUEST FOR DATA VISUALIZATION]
Your response should strictly be limited to Python code inside a Markdown block. Do not
explain code, do not write anything else, don't include the start and end of markdown block, only the content, always provide the column names in lowercase. The only thing you are allowed to respond other
than Python code are clarifying questions. When referring to data in Python use "data" variable
with column names that I will provide."""},
                ]
    if history:
        messages.extend(history)

    st.write("History:")
    st.code(messages)
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages)
                   

    return response['choices'][0]['message']['content'].strip()

st.title("Automatic Data Visualization with Flomaster")

# File upload
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Read data
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    
    st.write("Data preview:")
    st.write(data.head())

    # Natural language input for chart type and columns
    chart_input = st.text_input("Describe the chart you'd like to create, including the columns to use")

    data_prompt = f"""Data:\n data has {len(data)} rows, the columns with their data type are {str(data.dtypes)}"""

    if chart_input:
        # Request plotly code
        prompt = data_prompt + "\n" + f"Ask:\n {chart_input}"
        print(f"Time {time.localtime()}")
        print(f"Prompt: {prompt}")

        history.append({"role": "user", "content": chart_input})

        print(f"\n \nHisory {history}")


        plotly_code = request_plotly_code(history)
        print('\n \n before preprocess', plotly_code)
        



        plotly_code = post_process_response(plotly_code)
        # print('\n \nafter preprocess', plotly_code)

        history.append({"role": "assistant", "content": plotly_code})

        delay = 2  # Adjust the delay as needed (in seconds)
        show_progress_bar(delay)

        st.code(plotly_code, language="python")#, line_numbers=True)

        # Execute plotly code and display chart
        try:
            exec(f"{plotly_code}")
            st.plotly_chart(fig)
        except Exception as e:
            st.write("Error: Unable to generate the chart. Please check your input and try again.")
            st.write(f"Error details: {str(e)}")

