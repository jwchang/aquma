import PyPDF2
import json
import traceback

def parse_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except PyPDF2.utils.PdfReadError:
            raise Exception("Error reading the PDF file.")

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception(
            "Unsupported file format. Only PDF and TXT files are supported."
        )


def get_table_data(quiz_str):
    try:
        # convert the quiz from a str to dict
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []
        # Iterate over the quiz dictionary and extract the required information
        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " | ".join(
                [
                    f"{option}: {option_value}"
                    for option, option_value in value["options"].items()
                ]
            )
            correct = value["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False


RESPONSE_JSON1 = {
    "1": {
        "no": "1",
        "question": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": "correct answer",
    },
    "2": {
        "no": "2",
        "question": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": "correct answer",
    },
    "3": {
        "no": "3",
        "question": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": "correct answer",
    },
}

RESPONSE_JSON2 = {
    "1": {
        "no": "1",
        "question": "Content of true/false question",
        "correct": "True or False"
    },
    "2": {
        "no": "2",
        "question": "Content of true/false question",
        "correct": "True or False"
    },
    "3": {
        "no": "3",
        "question": "Content of true/false question",
        "correct": "True or False"
    },
}


RESPONSE_JSON3 = {
    "1": {
        "no": "1",
        "question": "Content of short-answer question",
        "correct": "Content of correct answer"
    },
    "2": {
        "no": "2",
        "question": "Content of short-answer question",
        "correct": "Content of correct answer"
    },
    "3": {
        "no": "3",
        "question": "Content of short-answer question",
        "correct": "Content of correct answer"
    },
}


RESPONSE_JSON4 = {
    "1": {
        "no": "1",
        "question": " ( ) is the capital city of Korea",
        "correct": "Seoul"
    },
    "2": {
        "no": "2",
        "question": "Tokyo is the capital city of ( )",
        "correct": "Japan"
    },
    "3": {
        "no": "3",
        "question": "The early bird ( ) the worm",
        "correct": "catches"
    },
}

