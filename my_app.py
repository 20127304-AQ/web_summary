import streamlit as st
import requests
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
import ollama

MODEL = 'llama3.2'

class Website:
     url: str
     title: str
     text: str

     def __init__(self, url):
        self.url = url 
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body.find_all(['script', 'style', 'image', 'input']):
            # remove script, style, image, input (unnecessary for summarization)
            irrelevant.decompose()
        #Get text, split with new line and remove whitespace
        self.text = soup.get_text(separator='\n', strip=True)

# Design system prompt
system_prompt = 'You are an assistant that analyzes the contents of a website \
and provides a summary of the main topics and ideas contained in the text. \
The summary should be written in a clear and concise manner. Respond in marrkdown format.'

# A function that writes a User prompt that asks for the summary of the website
def user_prompt(website):
    user_prompt = f'Write a summary of the website {website.title}:\n{website.text}'
    return user_prompt

def message_format(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt(website)}
    ]

def summarize_website(url):
    website = Website(url)
    messages = message_format(website)
    response = ollama.chat(model=MODEL, messages=messages)
    return response['message']['content']

# def display_summary(url):
#     summary = summarize_website(url)
#     display(Markdown(summary))
# display_summary('https://www.anthropic.com/')

# streamlit app
st.title('Website Summarizer')
st.markdown('Enter the URL to summarize its content.')

url = st.text_input('Enter a URL: ', '')

if st.button('Summarize'):
    if url:
        with st.spinner('Summarizing...'):
            summary = summarize_website(url)
        st.markdown(summary)
    else:
        st.warning('Please enter a valid URL.')
