from pydantic import BaseModel
import openai
from app.repository.db import db


TOKEN_LIMIT = 4096

CATEGORIES = ["Geography", "Demographic", "Law", "Administration", "Europe", "Education", "Languages", "Science", "Politics", "International relations"\
            "Housing", "Immigration", "Social Services", "Work and Employment", "Pensions and Retirement", "Civic Duties", "Public Safety", "Business and Trade",\
            "Public Transportation", "Environmental Policies", "Cultural Affairs", "Taxation", "Public Infrastructure", "Consumer Protection"]

DIFFICULTY = ["Easy", "Medium", "Hard"]

PROMPT_CONTEXT = "This is a text about Switzerland : "# Switzerland is located in Europe. The three official languages of Switzerland are German, French and Italian."

PROMPT_1 ="Using the information provided about Switzerland, generate in english a series of two questions that can be answered based on the text. \
For each question, provide:\n\
    The corresponding answer.\n\
    A category from the following options: {}.\n\
    A difficulty tag chosen from: {}.\n\
Present the output in the following format:\n\
    Question: [Insert question here]\n\
    Answer: [Insert answer here]\n\
    Category: [Insert category here]\n\
    Difficulty: [Insert difficulty tag here]".format(CATEGORIES, DIFFICULTY)

# class QuestionAnswerBlock(BaseModel):
#     question : str
#     answer : str
#     category : str
#     difficulty : str

# class Quizz(BaseModel):
#     questions_and_answers : list[QuestionAnswerBlock]

def token_limit(messages):
    total_tokens = sum(len(msg["content"]) for msg in messages)
    if total_tokens > TOKEN_LIMIT:
        return False
    return True

#print(PROMPT_1)



def chat(prompt):
    client = openai.Client(api_key="sk-rc-SUzUu0Qs2oNMI63oMQPfQg", base_url="http://148.187.108.173:8080")
    res = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        messages=[
            {
                "content": prompt, 
                "role": "system",
            },
            {
                "content" : PROMPT_1,
                "role" : "user"
            }
        ],
       # response_format=Quizz
        stream=True
    )

    #print(res["choices"][0]["message"]["content"])

    for chunk in res:
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
        
def split_text_into_chunks(text, chunk_size=300):
    """
    Splits a large text into smaller chunks of approximately `chunk_size` words.

    :param text: The large text to split.
    :param chunk_size: The approximate number of words per chunk (default is 100).
    :return: A list of text chunks.
    """
    words = text.split()  # Split text into words
    chunks = ' '.join(words[0:chunk_size])
    return chunks

def load_md():
    md = db.load_md()
    chunk = split_text_into_chunks(md)
    print(PROMPT_CONTEXT + chunk)
    chat(PROMPT_CONTEXT + chunk)

load_md()
# client = openai.Client(api_key="sk-rc-SUzUu0Qs2oNMI63oMQPfQg", base_url="http://148.187.108.173:8080")
# res = client.chat.completions.create(
#     model="meta-llama/Meta-Llama-3.1-70B-Instruct",
#     messages=[
#         {
#             "content": "Who is Pablo Picasso?", 
#             "role": "user",
#         }
#     ],
#     stream=True,
# )

# for chunk in res:
#     if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content, end="", flush=True)
        