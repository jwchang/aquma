from flask import Flask, render_template, request
import json
from dotenv import load_dotenv
from langchain.llms    import OpenAI
from langchain.chains  import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains  import SequentialChain

import traceback
import pandas as pd
from langchain.callbacks import get_openai_callback
from utils import parse_file, get_table_data, RESPONSE_JSON1, RESPONSE_JSON2, RESPONSE_JSON3, RESPONSE_JSON4

load_dotenv()

# Input fields
q_count    = 5    # 문제 갯수 기본 5개 
problemType = ""   # type1=사지선다 type2=T/F  type3=단답형  type4=빈칸채우기 
text       = ""
tone       = ""   # 문제 난이도 easy, medium, hard 

# This is an LLMChain to create 10 multiple choice questions from a given piece of text.
llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=-1)

def get_template(quiz_type, response_json_key):
    return f"""
    Text: {{text}}
    As an expert in creating {quiz_type} quizzes, your task is to construct a quiz comprising {{number}} questions, \
    tailored to students at a {{tone}} difficulty level. Make certain that there are no duplicate questions \
    and that all items directly correspond to the given text. Follow the JSON format provided below \
    as your guide for crafting your responses.
    Make sure to create exactly {{number}} questions, \
    and ensure that the distribution of correct answers is uniform. Please respond in Korean    
    ### response_json_key
    {{response_json}}
    """

# Define templates using the function
template1 = get_template('multiple-choice','RESPONSE_JSON1')
template2 = get_template('True/False' , 'RESPONSE_JSON2')
template3 = get_template('Short-Answer','RESPONSE_JSON3')
template4 = get_template('Fill-in-the-blank','RESPONSE_JSON4')


# created a prompt according to the type 
def create_prompt(template):
    return PromptTemplate(
        input_variables=["text", "number", "tone", "response_json"],
        template=template,
    )

quiz_generation_prompt1 = create_prompt(template1)
quiz_generation_prompt2 = create_prompt(template2)
quiz_generation_prompt3 = create_prompt(template3)
quiz_generation_prompt4 = create_prompt(template4)

# created a chain for the proper prompt 
def create_chain(llm, prompt):
    return LLMChain(llm=llm, prompt=prompt, output_key="quiz", verbose=True)

quiz_chain1 = create_chain(llm, quiz_generation_prompt1)
quiz_chain2 = create_chain(llm, quiz_generation_prompt2)
quiz_chain3 = create_chain(llm, quiz_generation_prompt3)
quiz_chain4 = create_chain(llm, quiz_generation_prompt4)


# This is an LLMChain to evaluate the multiple choice questions created by the above chain
llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
template = """You are an expert Korean grammarian and writer. Given the quiz for students.\
You need to evaluate complexity of the questions and give a complete analysis of the quiz if the students 
will be able to understand the questions and answer them. Only use at max 50 words for complexity analysis.
If quiz is not at par with the cognitive and analytical abilities of the students,\
update the quiz questions which need to be changed and change the tone such that it perfectly fits the students abilities. 
Quiz :
{quiz}
Critique from an expert Korean writer of the above quiz:"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["quiz"], template=template
)

review_chain = LLMChain(
    llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True
)

# This is the overall chain where we run these two chains in sequence.
def create_sequential_chain(chains):
    return SequentialChain(
        chains=chains,
        input_variables=["text", "number", "tone", "response_json"],
        output_variables=["quiz", "review"],
        verbose=True,
    )

generate_evaluate_chain1 = create_sequential_chain([quiz_chain1, review_chain])
generate_evaluate_chain2 = create_sequential_chain([quiz_chain2, review_chain])
generate_evaluate_chain3 = create_sequential_chain([quiz_chain3, review_chain])
generate_evaluate_chain4 = create_sequential_chain([quiz_chain4, review_chain])

# Check if all fields have inputs
def generatingQuiz():
   if  q_count and problemType and tone:
      print("starting...")
      
   try:
      # count tokens and cost of api call
      with get_openai_callback() as cb:
      
          if ( problemType == 'type1' ): 
              response = generate_evaluate_chain1(
                    {
                        "text": text,
                        "number": q_count,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON1),
                    }
              )
          elif ( problemType == 'type2'   ):
              response = generate_evaluate_chain2(
                    {
                        "text": text,
                        "number": q_count,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON2),
                    }
              )          
          elif ( problemType == 'type3'   ):   
              response = generate_evaluate_chain3(
                    {
                        "text": text,
                        "number": q_count,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON3),
                    }
              )
          else:
              response = generate_evaluate_chain4(
                    {
                        "text": text,
                        "number": q_count,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON4),
                    }
              )          
          
   except Exception as e:
       traceback.print_exception(type(e), e, e.__traceback__)
       print("Error")
   else:
       print(f"Total Tokens: {cb.total_tokens}")
       print(f"Prompt Tokens: {cb.prompt_tokens}")
       print(f"Completion Tokens: {cb.completion_tokens}")
       print(f"Total Cost (USD): ${cb.total_cost}")

       if isinstance(response, dict):
          # Extract quiz data from the response
          quiz = response["quiz"]
          # print( 'main->---------------->', response ,'-------------------main------------------')
          return quiz


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gen', methods=['POST'])
def gen():
    global text, q_count, tone, problemType
    text       = request.form.get('problemDesc')
    q_count    = request.form.get('problemNum')
    problemType = request.form.get('problemType')
    tone       = request.form.get('difficultyLevel')

    print("내용 입력: ", text)
    print("문제 유형: ", problemType)
    print("문제 갯수: ", q_count)
    print("난이도: ", tone)
    result = generatingQuiz()
    print( result )
    return result

if __name__ == '__main__':
    app.run(debug=True)