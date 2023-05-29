import os
import openai
import pandas as pd
from transformers import GPT2TokenizerFast

# Openai authorization
openai.organization = "org-us16wmNswbfs7htSVY2eiaYh" # zazu
openai.api_key = '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'


# cut text into chunks small enough for the GPT API
def chunker(text):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    chunks = []
    page = 0
    while page < len(text):
        page_count = 0
        chunk_tokens = 0
        chunk = ""
        # add pages until the page or token limit is reached
        while chunk_tokens <= 3500 and page_count < 5 and page < len(text):
            chunk += text.iloc[page][2]
            chunk_tokens += len(tokenizer(chunk)[0])
            page += 1
            page_count += 1
        chunks.append(chunk)
    return chunks

# takes list of chunks and runs them through the GPT API, returns list of answers, one for each chunk
def gpt(chunks):
    answers = []
    for chunk in chunks:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": """You are a helpful assistant that extracts validated clinical questionnaires and puts them into comma separated list with each questionnaire on a new line. Do not ask questions.
                If you can't find any questionnaires say: 'None found'.
                example text: 'European Medicines Agency', 'DLQI', 'Dermatology Life Quality Index', 'European Quality of Life 5-Dimension Questionnaire', 'FCBP'
                example answer: 
                - EQ-5D, European Quality of Life 5-Dimension Questionnaire
                - DLQI, Dermatology Life Quality Index"""},
                {"role": "user", "content": chunk},
            ]
        )
        answer = completion["choices"][0]["message"]["content"]
        answers.append(answer)

    return answers

def main():
    data = pd.read_csv(r'C:\Users\Jakub\Documents\zazu\openai-quickstart-python\demo_app_my/text610.csv')
    text = data.astype(str)
    chunks = chunker(text)
    answers = gpt(chunks)
    
    for answer in answers:
        print(answer)
    print(answers)
main()