from flask import Flask, render_template, request, redirect, url_for, session
import lesson_planner 
from worksheet_generator import generate_worksheet_and_fact_sheet
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
    return render_template('prompt_selection.html')

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
        # Render the appropriate prompt form based on the selected prompt
        prompt = session.get('prompt')
        if prompt:
            form_template = f"prompt{prompt[-1]}_form.html"
            return render_template(form_template)
        else:
            # If no prompt is selected, redirect back to prompt selection
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

@app.route('/output')
def output():
    input_data = session.get('input_data', {})
    worksheet_data = session.get('worksheet_data', {})
    
    lesson_plan = None
    worksheet_content = None
    fact_sheet_content = None
    answer_bank_content = None
    
    # Check if we have lesson plan data in the session
    if input_data:
        lesson_plan = lesson_planner.generate_lesson_plan(input_data)
    
    # Check if we have worksheet data in the session
    if worksheet_data:
        worksheet_content, fact_sheet_content, answer_bank_content = generate_worksheet_and_fact_sheet(
            worksheet_data['topic'], 
            worksheet_data['num_questions'], 
            worksheet_data['question_types'],
            worksheet_data['formatting_delimiter']
        )
    
    return render_template('unit_plan.html', 
                           unit_plan=lesson_plan, 
                           worksheet_content=worksheet_content, 
                           fact_sheet_content=fact_sheet_content,
                           answer_bank_content=answer_bank_content,
                           grade_level=input_data.get('grade_level', ''), 
                           num_students=input_data.get('number_of_students', ''), 
                           state=input_data.get('state', ''))


if __name__ == "__main__":
    app.run(debug=True)

