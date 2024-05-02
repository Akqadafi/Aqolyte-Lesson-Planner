from flask import Flask, render_template, request, redirect, url_for, session, send_file
from docx import Document
import os
import lesson_planner
from worksheet_generator import generate_worksheet, extract_questions_and_answers
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = '198019812022'
app.config['SESSION_TYPE'] = 'filesystem'

def download_as_word(content_type, content):
    logging.debug(f"Inside download_as_word with content_type = {content_type} and content = {content}")
    logging.debug(f"Session 'content_type': {session.get('content_type')}")
    logging.debug(f"Session 'content': {session.get('content')}")
    doc = Document()
    doc.add_heading(content_type, 0)

    if content_type == 'Worksheet':
        questions, answers = content
        doc.add_heading('Questions:', level=1)
        for question in questions:
            p = doc.add_paragraph()
            p.add_run(question.strip()).bold = True
            p.add_run('\n')

        doc.add_heading('Answers:', level=1)
        for answer in answers:
            p = doc.add_paragraph()
            p.add_run(answer.strip()).bold = True
            p.add_run('\n')

    elif content_type == 'Lesson Plan':
        doc.add_heading('Lesson Plan:', level=1)
        for section_title, section_content in content:
            doc.add_heading(f"{section_title}:", level=1)
            doc.add_paragraph(section_content)

    filepath = os.path.join(os.getcwd(), f"{content_type}.docx")
    doc.save(filepath)
    return send_file(filepath, as_attachment=True, download_name=f"{content_type}.docx")

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/choose')
def choose():
    return render_template('choose.html')

@app.route('/redirect_choice', methods=['POST'])
def redirect_choice():
    choice = request.form.get('choice')
    if choice == "lesson":
        return redirect(url_for('prompt_selection'))
    elif choice == "worksheet":
        return redirect(url_for('worksheet'))
    else:
        return redirect(url_for('landing'))

@app.route('/prompt_selection', methods=['GET', 'POST'])
def prompt_selection():
    if request.method == 'POST':
        session['prompt'] = request.form['prompt']
        return redirect(url_for('home'))
    return render_template('prompt_selection.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        input_data = request.form.to_dict()
        input_data['prompt'] = session.get('prompt')
        session['input_data'] = input_data
        return redirect(url_for('output'))
    else:
        prompt = session.get('prompt')
        if prompt:
            form_template = f"prompt{prompt[-1]}_form.html"
            return render_template(form_template)
        else:
            return redirect(url_for('prompt_selection'))

@app.route('/worksheet', methods=['GET', 'POST'])
def worksheet():
    if request.method == 'POST':
        topic = request.form['topic']
        question_types = request.form['question_types']
        num_questions = int(request.form['num_questions'])
        delimiter = request.form['delimiter']
        session['worksheet_data'] = {
            'topic': topic,
            'question_types': question_types,
            'num_questions': num_questions,
            'formatting_delimiter': delimiter
        }
        return redirect(url_for('output'))
    return render_template('worksheet_input_form.html')

@app.route('/output', methods=['GET', 'POST'])
def output():
    try:
        logging.debug(f"Session 'input_data': {session.get('input_data')}")
        logging.debug(f"Session 'worksheet_data': {session.get('worksheet_data')}")
        logging.debug(f"Session 'content_type': {session.get('content_type')}")
        logging.debug(f"Session 'content': {session.get('content')}")

        if request.method == 'POST' and request.form.get('download_word'):
            content_type = session.get('content_type')
            content = session.get('content')
            logging.debug(f"Session 'content_type': {session.get('content_type')}")
            logging.debug(f"Session 'content': {session.get('content')}")
            logging.debug(f"Calling download_as_word with content_type = {content_type} and content = {content}")
            logging.debug(f"Content Type: {content_type}")
            logging.debug(f"Content: {content}")

            return download_as_word(content_type, content)

        input_data = session.get('input_data', {})
        worksheet_data = session.get('worksheet_data', {})

        if input_data:
            # Debugging: Print before calling the function
            print("Calling generate_lesson_plan with input_data:", input_data)

            # Corrected function call to also get ordered_sections
            lesson_plan_dict, ordered_sections = lesson_planner.generate_lesson_plan(input_data)
            
            # Debugging: Print what you received
            print("Received lesson_plan_dict:", lesson_plan_dict)
            print("Received ordered_sections:", ordered_sections)

            session['content_type'] = 'Lesson Plan'
            session['content'] = [(section, lesson_plan_dict.get(section, '')) for section in ordered_sections]
            return render_template('unit_plan.html', 
                                    unit_plan=lesson_plan_dict, 
                                    grade_level=input_data.get('grade_level', ''), 
                                    num_students=input_data.get('number_of_students', ''), 
                                    state=input_data.get('state', ''))

        elif worksheet_data:
            worksheet, answer_bank = generate_worksheet(
                worksheet_data['topic'], 
                worksheet_data['num_questions'], 
                worksheet_data['question_types'], 
                worksheet_data['formatting_delimiter']
            )
            questions, answers = extract_questions_and_answers(worksheet, answer_bank)
            session['content_type'] = 'Worksheet'
            session['content'] = (questions, answers)
            return render_template('worksheet_display.html', 
                                    questions=questions, 
                                    answers=answers)

        else:
            return "No data found for rendering. Please go back and try again."
    except Exception as e:  # Exception handling
        logging.error(f"An error occurred: {e}")
        return "An error occurred. Please try again."

if __name__ == "__main__":
    app.run(debug=True)
