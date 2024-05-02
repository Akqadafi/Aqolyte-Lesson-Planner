import os
import random
import openai
from dotenv import load_dotenv

load_dotenv()

# Fetch API key from the environment variables
API_KEY = os.environ.get('OPENAI_API_KEY')

if API_KEY is None:
    print("API Key not found. Make sure you set the OPENAI_API_KEY environment variable in the .env file.")
else:
    openai.api_key = API_KEY

def generate_worksheet_and_fact_sheet(topic, num_questions, question_type, formatting_delimiter):
    # Define the fact sheet prompt
    fact_prompt = f"Provide a detailed fact sheet about {topic}."
    fact_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": fact_prompt}
        ]
    )
    fact_sheet = fact_response['choices'][0]['message']['content'].strip()

    # Define the worksheet prompt based on the question type
    if question_type == "Short Answer Questions":
        prompt = f"Generate {num_questions} short answer questions about {topic} and provide their answers."
    elif question_type == "Fill in the Blanks":
        prompt = f"Generate {num_questions} fill in the blank questions about {topic} and provide their answers."
    elif question_type == "Matching":
        prompt = f"Generate {num_questions} matching questions about {topic} and provide their answers."
    elif question_type == "Mix":
        num_short_answer = num_fill_in = num_matching = num_questions // 3
        prompt = (f"Generate a worksheet about {topic}. Provide:\n"
                  f"- {num_short_answer} short answer questions\n"
                  f"- {num_fill_in} fill in the blank questions\n"
                  f"- {num_matching} matching definition questions.")
    else:
        raise ValueError(f"Invalid question type: {question_type}")

    # Request the worksheet questions and answers from the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    worksheet_with_answers = response['choices'][0]['message']['content'].strip()

    # Here, you'll need to extract questions and answers from the worksheet_with_answers
    # This extraction method might need to be refined based on how the output looks.
    questions, answers = extract_questions_and_answers(worksheet_with_answers)
    
    worksheet = questions + formatting_delimiter
    answer_bank = "Answer Bank:\n" + answers

    return worksheet, fact_sheet, answer_bank

def extract_questions_and_answers(worksheet_with_answers):
    questions = []
    answers = []
    
    # Split the worksheet content based on the ' Q: ' delimiter
    items = worksheet_with_answers.split(' Q: ')[1:]
    
    for item in items:
        # Split each item into question and answer using ' A: ' delimiter
        q, a = item.split(' A: ')
        questions.append('Q: ' + q)
        answers.append(a)
    
    return "\n".join(questions), "\n".join(answers)


def collect_teacher_input():
    topic = input("Enter the topic for the worksheet: ")
    question_type = input("Enter the type of question: ")
    num_questions = int(input("Enter the number of questions: "))
    formatting_delimiter = input("Enter the delimiter to separate questions (e.g., '----' or '*****'): ")

    return topic, question_type, num_questions, formatting_delimiter

if __name__ == '__main__':
    topic = input("Enter the topic for the worksheet: ")
    question_type = input("Enter the type of question: ")
    num_questions = int(input("Enter the number of questions: "))
    formatting_delimiter = input("Enter the delimiter to separate questions (e.g., '----' or '*****'): ")

    worksheet, fact_sheet, answer_bank = generate_worksheet_and_fact_sheet(topic, num_questions, question_type, formatting_delimiter)
    print("\nGenerated Worksheet Content:")
    print(worksheet)
    print("\nGenerated Fact Sheet Content:")
    print(fact_sheet)
    print("\nGenerated Answer Bank:")
    print(answer_bank)

