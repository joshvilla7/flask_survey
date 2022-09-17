from http.client import responses
from flask import Flask, request, redirect, render_template, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

key = "responses"
survey_key = 'current_survey'

@app.route('/')
def survey_picker():
    """view function that when user goes to root route,
    shows list of surveys they can pick from"""
    return render_template('pick-survey.html', surveys=surveys)

@app.route('/', methods=["POST"])
def pick_survey():
    """user picks survey"""
    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template('/already-finish.html')

    survey = surveys[survey_id]
    session[survey_key] = survey_id
    
    return render_template('survey_instructions.html', survey=survey)

@app.route('/start', methods=["POST"])
def survey_start():
    """clears responses, and redirects to first question"""
    session[key] = []
    return redirect('/questions/0')

@app.route('/questions/<int:questid>')
def show_question(questid):
    """route that shows a question based on questid"""
    responses = session.get(key)
    survey_code = session[survey_key]
    survey = surveys[survey_code]

    if (responses is None):
       return redirect('/')
       #if there is no response it means user is trying to access question page too soon

    if (len(responses) == len(survey.questions)):
        return redirect('/finish')
        #all questions have been answered, send to finish route

    if (len(responses) != questid):
        flash(f"Invalid question id: {questid}.")
        return redirect(f"/questions/{len(responses)}")
        #this means user is trying to access questions out of order

    question = survey.questions[questid]
    return render_template('questions.html', question_num=questid, question=question)

@app.route('/finish')
def finished_survey():
    """returns a finish html at the /finish route"""
    survey_id = session[survey_key]
    survey = surveys[survey_id]
    responses = session[key]
    html = render_template('finish.html', survey=survey, responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
    

@app.route('/answer', methods=["POST"])
def question_handler():
    """saves the user's answer and proceeds to the next question"""
    choice = request.form['answer']
    text = request.form.get('text', "")

    responses = session[key]
    responses.append({"choice": choice, "text": text})
    session[key] = responses
    survey_code = session[survey_key]
    survey = surveys[survey_code]

    #if all questions have been answered, redirect to /finish
    if (len(responses) == len(survey.questions)):
        return redirect('/finish')

    else: 
        return redirect(f"/questions/{len(responses)}")

