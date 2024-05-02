from flask import Flask, render_template, request, redirect, url_for, session
import lesson_planner
from worksheet_generator import generate_worksheet, extract_questions_and_answers
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = '198019812022'
app.config['SESSION_TYPE'] = 'filesystem'

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
    try:
        return render_template('prompt_selection.html')
    except Exception as e:
        logging.error(f"Exception occurred while rendering prompt_selection.html: {e}")
        return str(e)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        input_data = request.form.to_dict()
        input_data['prompt'] = session.get('prompt')
        input_data.update({
            'culture_group': [input_data.get('culture_group', 'defaultCultureGroup')],
            'disabled': 'disabled' in input_data,
            'ell': 'ell' in input_data,
            'gifted': 'gifted' in input_data,
        })
        session['input_data'] = input_data
        return redirect(url_for('output'))
    else:
        prompt = session.get('prompt')
        if prompt:
            form_template = f"prompt{prompt[-1]}_form.html"
            try:
                return render_template(form_template)
            except Exception as e:
                logging.error(f"Exception occurred while rendering {form_template}: {e}")
                return str(e)
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
        logging.debug("Stored Session Data: %s", session['worksheet_data'])
        return redirect(url_for('output'))
    try:
        return render_template('worksheet_input_form.html')
    except Exception as e:
        logging.error(f"Exception occurred while rendering worksheet_input_form.html: {e}")
        return str(e)

@app.route('/output')
def output():
    input_data = session.get('input_data', {})
    worksheet_data = session.get('worksheet_data', {})
    logging.debug("Retrieved Session Data: %s", worksheet_data)

    # Check if we have lesson plan data in the session
    if input_data:
        lesson_plan = lesson_planner.generate_lesson_plan(input_data)
        session.pop('input_data', None)
        return render_template('unit_plan.html', 
                               unit_plan=lesson_plan, 
                               grade_level=input_data.get('grade_level', ''), 
                               num_students=input_data.get('number_of_students', ''), 
                               state=input_data.get('state', ''))

    # Check if we have worksheet data in the session
    if worksheet_data:
        worksheet_content, answer_bank_content = generate_worksheet(
            worksheet_data['topic'], 
            worksheet_data['num_questions'], 
            worksheet_data['question_types'],
            worksheet_data['formatting_delimiter']
        )
        print(f"Debug: worksheet_content = {worksheet_content}, type = {type(worksheet_content)}")
        print(f"Debug: answer_bank_content = {answer_bank_content}, type = {type(answer_bank_content)}")


        if worksheet_content is None or answer_bank_content is None:
            return "An error occurred while generating the worksheet."

        # Debug log to check what's returned by generate_worksheet
        logging.debug("Returned by generate_worksheet - Worksheet Content: %s", worksheet_content)
        logging.debug("Returned by generate_worksheet - Answer Bank Content: %s", answer_bank_content)

        # Debug log for full API response
        logging.debug("Full API Response: %s", worksheet_content)

        # Use only one method to extract questions and answers
        questions, answers = extract_questions_and_answers(worksheet_content)

        # Debug log to check the extracted questions and answers
        logging.debug("Questions for Render: %s", questions)
        logging.debug("Answers for Render: %s", answers)

        # Clear the session data for worksheets
        session.pop('worksheet_data', None)

        return render_template('worksheet_display.html',
                               questions=questions,
                               answers=answers)

        print(f"Debug: response type = {type(response)}")

    # Fallback if no data is found (this shouldn't typically happen)
    return "No data found for rendering. Please go back and try again."



if __name__ == "__main__":
    app.run(debug=True)

