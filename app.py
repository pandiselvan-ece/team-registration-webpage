from flask import Flask, render_template, request, redirect, session, url_for, send_file
import csv
import os
import json

app = Flask(__name__)
app.secret_key = 'raam_secret'

problem_statements = [
    "AI Therapist for Daily Mood Logging and Support",
    "Stress Level Analyzer from Daily Journal Entries",
    "Dream Journal to Story Generator",
    "Mental Health Checker from Handwriting Samples",
    "Fashion Assistant from Image Input",
    "Abnormality Detector in X-ray or CT Images",
    "Emotion Recognition from Short Video Clips",
    "Vehicle Type and Plate Recognition from CCTV Footage",
    "Trash Classifier: Sort Recyclables from Waste Images",
    "Outfit Matcher from Wardrobe Photo",
    "Video Summary Generator for Surveillance Footage",
    "Chemistry Subject Tutor Chatbot",
    "Flowchart to Python Code Generator",
    "Interactive Comic Book Creator for Kids",
    "Quiz Generator from Any PDF Textbook",
    "Food Ingredient to Recipe Generator",
    "Calorie Estimator from Meal Image",
    "Generate Song Lyrics Based on Mood and Genre",
    "Rap Generator from User Voice Input",
    "Story Completion from a Given Prompt and Style",
    "Sketch-to-Story Generator",
    "Custom Voice AI Chatbot That Mimics Celebrity Voices",
    "Artwork Generator from User's Doodle",
    "Interior Design Planner from Room Photo",
    "Virtual Try-On for Jewelry and Accessories",
    "Pet Health Checker from Uploaded Image",
    "Personalized Yoga Pose Generator from Fitness Goals",
    "Math Equation Solver from Handwritten Input",
    "3D Object Creator from Sketch or Image",
    "Color Palette Generator from Uploaded Image",
    "Image-to-Story Generator for Children's Books",
    "Image Generator from Text Description in Regional Language",
    "Virtual Museum Guide with Image Recognition",
    "AI Legal Assistant to Explain Laws in Simple Terms",
    "Document Summarizer for Legal or Research PDFs",
    "Whiteboard Diagram to Editable PowerPoint Generator",
    "Dance Move Generator Based on Song Rhythm",
    "AI Assistant for Gardening using Plant Image",
    "Image-Based Puzzle Generator for Kids",
    "AI Companion Bot for Seniors with Face Recognition"
]

@app.route('/')
def index():
    taken_teams = set()
    taken_problems = set()
    if os.path.isfile('submissions.csv'):
        with open('submissions.csv', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                taken_teams.add(row['Team Number'])
                taken_problems.add(row['Problem Statement'])
    return render_template(
        'form.html',
        problems=problem_statements,
        taken_teams=taken_teams,
        taken_problems=taken_problems,
        error=None,
        prev_data={}
    )

@app.route('/submit', methods=['POST'])
def submit():
    team_number = request.form['teamNumber']
    name1 = request.form['name1']
    regno1 = request.form['regno1']
    name2 = request.form['name2']
    regno2 = request.form['regno2']
    name3 = request.form['name3']
    regno3 = request.form['regno3']
    problem = request.form['problem']
    custom_problem = request.form.get('custom_problem', '').strip()

    actual_problem = custom_problem if problem == 'Other' else problem

    taken_teams = set()
    taken_problems = set()
    if os.path.isfile('submissions.csv'):
        with open('submissions.csv', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                taken_teams.add(row['Team Number'])
                taken_problems.add(row['Problem Statement'])

    error = None
    if problem == 'Other' and not custom_problem:
        error = "You selected 'Other' but did not enter a problem statement."
    elif team_number in taken_teams:
        error = f"Team number {team_number} is already registered."
    elif actual_problem in taken_problems:
        error = f"Problem statement '{actual_problem}' is already taken."

    if error:
        return render_template(
            'form.html',
            problems=problem_statements,
            taken_teams=taken_teams,
            taken_problems=taken_problems,
            error=error,
            prev_data={
                'teamNumber': team_number,
                'name1': name1,
                'regno1': regno1,
                'name2': name2,
                'regno2': regno2,
                'name3': name3,
                'regno3': regno3,
                'problem': '',  # Clear problem because invalid or duplicate
                'custom_problem': ''
            }
        )

    data = [
        team_number,
        name1, regno1,
        name2, regno2,
        name3, regno3,
        actual_problem
    ]

    file_exists = os.path.isfile('submissions.csv')
    with open('submissions.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Team Number', 'Name1', 'RegNo1', 'Name2', 'RegNo2', 'Name3', 'RegNo3', 'Problem Statement'])
        writer.writerow(data)

    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        with open('data.json') as f:
            users = json.load(f)
        uname = request.form['username']
        pwd = request.form['password']
        if uname == users['admin']['username'] and pwd == users['admin']['password']:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        error = "Invalid username or password. Please try again."
    return render_template('login.html', error=error)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not os.path.isfile('submissions.csv'):
        return render_template('admin.html', rows=[], headers=[])
    with open('submissions.csv', newline='') as file:
        reader = list(csv.reader(file))
        headers = reader[0]
        rows = reader[1:]
    return render_template('admin.html', headers=headers, rows=rows)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/download')
def download():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not os.path.exists("submissions.csv"):
        return "<h3>No data to download.</h3>"

    return send_file("submissions.csv", as_attachment=True, download_name="team_submissions.csv")

@app.route('/clear')
def clear():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if os.path.exists("submissions.csv"):
        os.remove("submissions.csv")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
