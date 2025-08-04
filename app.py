from flask import Flask, render_template, request, redirect, session, url_for, send_file
import csv
import os
import json

app = Flask(__name__)
app.secret_key = 'raam_secret'

problem_statements = [
    "Smart Home Automation", "AI Chatbot for College", "E-Waste Management System",
    "IoT-based Health Monitor", "Campus Navigation App", "Virtual Lab for Physics",
    "Library Book Finder", "Women Safety Tracker", "AI Resume Builder",
    "Attendance via Face Recognition", "Smart Dustbin System", "Student Feedback Analyzer",
    "Vehicle Number Plate Detection", "Online Voting System", "Emergency Alert System",
    "Energy Consumption Optimizer", "Anti-Theft IoT Alarm", "Food Waste Tracker",
    "Crowd Density Monitor", "AI Career Guide", "Blood Donation Matcher",
    "Disaster Warning System", "College Event Scheduler", "Online Bus Tracker",
    "Smart Irrigation System"
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
        taken_problems=taken_problems
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

    # Check if 'Other' selected, get the textarea input
    if problem == 'Other':
        custom_problem = request.form.get('custom_problem', '').strip()
        if not custom_problem:
            return "<h3>Error: You selected 'Other' but did not enter a problem statement.<br><a href='/'>Go Back</a></h3>"
        problem = custom_problem

    data = [
        team_number,
        name1, regno1,
        name2, regno2,
        name3, regno3,
        problem
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
    if request.method == 'POST':
        with open('data.json') as f:
            users = json.load(f)
        uname = request.form['username']
        pwd = request.form['password']
        if uname == users['admin']['username'] and pwd == users['admin']['password']:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        return "<h3>Login failed. Try again.</h3>"
    return render_template('login.html')

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
