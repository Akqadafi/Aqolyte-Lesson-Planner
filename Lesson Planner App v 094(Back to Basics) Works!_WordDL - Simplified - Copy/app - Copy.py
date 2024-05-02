from flask import Flask, render_template, request, redirect, url_for, session
import lesson_planner 
from worksheet_generator import generate_worksheet_and_fact_sheet


app = Flask(__name__)
app.secret_key = '198019812022'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/prompt_selection', methods=['GET', 'POST'])
def prompt_selection():
    if request.method == 'POST':
        session['prompt'] = request.form['prompt']
        print("Stored prompt in session:", session['prompt'])  # Debug print
        session['worksheet'] = 'worksheet' in request.form
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

        if session.get('worksheet'):
            return redirect(url_for('worksheet'))
        else:
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
    print("Retrieved prompt from session:", session.get('prompt'))  # Debug print
    if request.method == 'POST':
        topic = session.get('input_data')['topic']
        question_types = request.form['question_types']
        num_questions = int(request.form['num_questions'])
        
        session['worksheet_data'] = {
            'topic': topic,
            'question_types': question_types,
            'num_questions': num_questions
        }
        return redirect(url_for('output'))
    return render_template('worksheet_input_form.html')

@app.route('/output')
def output():
    input_data = session.get('input_data', {})
    print("Received prompt in /output:", input_data.get('prompt'))  # Debug print
    if input_data is None:
        return "No input data.", 400

    lesson_plan = lesson_planner.generate_lesson_plan(input_data)
    worksheet_content = fact_sheet_content = None

    if session.get('worksheet'):
        worksheet_data = session.get('worksheet_data')
        worksheet_content, fact_sheet_content = generate_worksheet_and_fact_sheet(
            worksheet_data['topic'], 
            worksheet_data['num_questions'], 
            worksheet_data['question_types']
        )

    return render_template('unit_plan.html', 
                           unit_plan=lesson_plan, 
                           worksheet_content=worksheet_content, 
                           fact_sheet_content=fact_sheet_content,
                           grade_level=input_data['grade_level'], 
                           num_students=input_data['number_of_students'], 
                           state=input_data['state'])

if __name__ == "__main__":
    app.run(debug=True)

