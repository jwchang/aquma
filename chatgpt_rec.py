from flask import Flask, render_template, request
import json
from dotenv import load_dotenv
from langchain.llms   import OpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
import traceback

load_dotenv()

llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=-1)

# Removed redundant template code and created a function to reduce code repetition
def get_template(response_json_key):
    return f"""
    Text: {{text}}
    당신은 전문적인 문제 생성자입니다. 주어진 텍스트에 따라 {{number}}개의 문제를 {{tone}} 톤으로 학생들을 위해 만드세요.\
    문제가 반복되지 않도록 확인하고 모든 문제가 텍스트에 부합하는지 확인하세요.
    당신의 응답을 아래의 {response_json_key}처럼 포맷팅하세요. 이것을 가이드로 사용하세요.\
    {{number}}개의 문제를 반드시 만드세요. 정답의 분포는 균일하게 만드세요. 그리고 한국어로 답하세요.
    ### {response_json_key}
    {{response_json}}
    """

# Define templates using the function
template1 = get_template('RESPONSE_JSON1')
template2 = get_template('RESPONSE_JSON2')
template3 = get_template('RESPONSE_JSON3')
template4 = get_template('RESPONSE_JSON4')

# Removed redundant prompt creation code and created a function to reduce code repetition
def create_prompt(template):
    return PromptTemplate(
        input_variables=["text", "number", "tone", "response_json"],
        template=template,
    )

quiz_generation_prompt1 = create_prompt(template1)
quiz_generation_prompt2 = create_prompt(template2)
quiz_generation_prompt3 = create_prompt(template3)
quiz_generation_prompt4 = create_prompt(template4)

# Removed redundant LLMChain code and created a function to reduce code repetition
def create_chain(llm, prompt):
    return LLMChain(llm=llm, prompt=prompt, output_key="quiz", verbose=True)

quiz_chain1 = create_chain(llm, quiz_generation_prompt1)
quiz_chain2 = create_chain(llm, quiz_generation_prompt2)
quiz_chain3 = create_chain(llm, quiz_generation_prompt3)
quiz_chain4 = create_chain(llm, quiz_generation_prompt4)

# Removed redundant SequentialChain code and created a function to reduce code repetition
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

# Change function to take in arguments instead of using global variables
def generatingQuiz(text, number, tone, response_json):
    try:
        # Chain 1
        result = generate_evaluate_chain1(input={"text": text, "number": number, "tone": tone, "response_json": response_json})
        if result['quiz']:
            return result['quiz']

        # Chain 2
        result = generate_evaluate_chain2(input={"text": text, "number": number, "tone": tone, "response_json": response_json})
        if result['quiz']:
            return result['quiz']

        # Chain 3
        result = generate_evaluate_chain3(input={"text": text, "number": number, "tone": tone, "response_json": response_json})
        if result['quiz']:
            return result['quiz']

        # Chain 4
        result = generate_evaluate_chain4(input={"text": text, "number": number, "tone": tone, "response_json": response_json})
        if result['quiz']:
            return result['quiz']

    except Exception as e:
        print("An error occurred while generating the quiz: ", e)
        raise

    # Raise an error instead of returning None
    raise ValueError("Quiz could not be generated with the provided parameters")

app = Flask(__name__)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        text = request.json['text']
        number = request.json['number']
        tone = request.json['tone']
        response_json = request.json['response_json']

        try:
            result = generatingQuiz(text, number, tone, response_json)
            return json.dumps(result), 200
        except Exception as e:
            return json.dumps({"error": str(e)}), 500

    return render_template('quiz.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
