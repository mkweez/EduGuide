from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

USER_DATA_FILE = 'users.json'
TASKS_DATA_FILE = 'tasks.json'

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)

def load_tasks():
    try:
        with open(TASKS_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_tasks(data):
    with open(TASKS_DATA_FILE, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']

    users = load_user_data()

    if email in users and users[email] == password:
        return redirect(url_for('task_page'))
    else:
        return "Invalid credentials. Please try again."

@app.route('/register', methods=['POST'])
def register_post():
    email = request.form['email']
    password = request.form['password']

    users = load_user_data()

    if email in users:
        return "User already exists. Please log in."

    users[email] = password
    save_user_data(users)

    return redirect(url_for('task_page'))

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('task_page'))

@app.route('/tasks')
def task_page():
    tasks = load_tasks()
    return render_template('tasks.html', tasks=tasks)

@app.route('/parse_tasks', methods=['POST'])
def parse_tasks():
    url = 'https://inf-ege.sdamgia.ru/test?id=16285731'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'status': 'error', 'message': 'Failed to retrieve data'}), 500

    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлечение задач
    tasks = []
    for task_block in soup.find_all('div', class_='task'):
        condition = task_block.find('div', class_='condition').text.strip()
        solution = task_block.find('div', class_='solution').text.strip()
        tasks.append({'condition': condition, 'solution': solution})

    print('Parsed tasks:', tasks)

    if not tasks:
        return jsonify({'status': 'error', 'message': 'No tasks found'}), 404

    save_tasks(tasks)
    return jsonify({'status': 'success', 'tasks_parsed': len(tasks)})

@app.route('/evaluate_solution', methods=['POST'])
def evaluate_solution():
    user_solution = request.form['solution']
    correct_solution = request.form['correct_solution']

    score = user_solution == correct_solution

    return jsonify({'score': score})

if __name__ == '__main__':
    app.run(debug=True)

