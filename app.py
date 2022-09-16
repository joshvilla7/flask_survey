from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

key = "responses"

@app.route('/')
def survey_instructions():
    """view function that when user goes to root route,
    shows survey"""
    return render_template('survey_instructions.html', survey=satisfaction_survey)

@app.route('/start', methods=["POST"])
def survey_start():
    """clears responses, and redirects to first question"""
    session[key] = []
    return redirect('/questions/0')

@app.route('/questions/<int:questid>')
def show_question(questid):
    """route that shows a question based on questid"""
    responses = session.get(key)

    if (responses is None):
       return redirect('/')
       #if there is no response it means user is trying to access question page too soon

    if (len(responses) == len(satisfaction_survey.questions)):
        return redirect('/finish')
        #all questions have been answered, send to finish route

    if (len(responses) != questid):
        flash(f"Invalid question id: {questid}.")
        return redirect(f"/questions/{len(responses)}")
        #this means user is trying to access questions out of order

    question = satisfaction_survey.questions[questid]
    return render_template('questions.html', question_num=questid, question=question)

@app.route('/finish')
def finished_survey():
    """returns a finish html at the /finish route"""
    return render_template('finish.html')

@app.route('/answer', methods=["POST"])
def question_handler():
    """saves the user's answer and proceeds to the next question"""
    choice = request.form['answer']

    responses = session[key]
    responses.append(choice)
    session[key] = responses

    #if all questions have been answered, redirect to /finish
    if (len(responses) == len(satisfaction_survey.questions)):
        return redirect('/finish')

    else: 
        return redirect(f"/questions/{len(responses)}")

