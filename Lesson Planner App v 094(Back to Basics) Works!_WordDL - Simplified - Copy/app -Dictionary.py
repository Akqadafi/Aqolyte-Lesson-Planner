from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import lesson_planner
from worksheet_generator import generate_worksheet, extract_questions_and_answers
import logging
import pypandoc  # Importing pypandoc

logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = '198019812022'
app.config['SESSION_TYPE'] = 'filesystem'

# Function to convert HTML to DOCX
def html_to_docx(html_content, output_filename):
    output_path = os.path.join(os.getcwd(), output_filename)
    with open("temp.html", "w") as f:
        f.write(html_content)
    pypandoc.convert_file("temp.html", "docx", outputfile=output_path)
    os.remove("temp.html")
    return output_path

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
        input_data = session.get('input_data', {})
        worksheet_data = session.get('worksheet_data', {})

        if request.method == 'POST' and request.form.get('download_word'):
            content = None  # Initialize content
            if session.get('content_type') == 'Lesson Plan':
                content = render_template(
                    'unit_plan.html',
                    unit_plan=session.get('content', {}),
                    grade_level=input_data.get('grade_level', ''),
                    num_students=input_data.get('number_of_students', ''),
                    state=input_data.get('state', '')
                )
            elif session.get('content_type') == 'Worksheet':
                content = render_template(
                    'worksheet_display.html',
                    questions=session['content'].get('questions', []),
                    answers=session['content'].get('answers', [])
                )
            if content:
                output_path = html_to_docx(content, f"{session.get('content_type')}.docx")
                return send_file(output_path, as_attachment=True, download_name=f"{session.get('content_type')}.docx")

        if input_data:
            lesson_plan_dict, ordered_sections = lesson_planner.generate_lesson_plan(input_data)
            session['content_type'] = 'Lesson Plan'
            session['content'] = lesson_plan_dict
            return render_template(
                'unit_plan.html',
                unit_plan=lesson_plan_dict,
                grade_level=input_data.get('grade_level', ''),
                num_students=input_data.get('number_of_students', ''),
                state=input_data.get('state', '')
            )

        elif worksheet_data:
            worksheet, answer_bank = generate_worksheet(
                worksheet_data['topic'],
                worksheet_data['num_questions'],
                worksheet_data['question_types'],
                worksheet_data['formatting_delimiter']
            )
            questions, answers = extract_questions_and_answers(worksheet, answer_bank)
            session['content_type'] = 'Worksheet'
            session['content'] = {'questions': questions, 'answers': answers}
            return render_template('worksheet_display.html', questions=questions, answers=answers)

        else:
            return "No data found for rendering. Please go back and try again."
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "An error occurred. Please try again."

if __name__ == "__main__":
    app.run(debug=True)

