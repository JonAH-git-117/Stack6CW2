# Sky Engineering Team Directory
## 5COSC021W Coursework 2 — Group 6

A Django web application for Sky's Engineering Department to manage and view internal engineering teams, departments, dependencies and more.

## Group Members
- Jonathan Chamberlain
- Sedra Elawi
- Ishaq Choudhury
- Munsar Mahamed
- Ahmed Morshed
- Uthman Ali

## Features
- Team directory with search and filters (department, manager, status)
- Team detail pages (members, repositories, skills, dependencies)
- Reports dashboard with PDF (WeasyPrint) and Excel (openpyxl) export
- Data visualisation with Bokeh charts
- User accounts (register, login, profile, update profile, change password)
- Admin dashboard with team management, user access and audit trail
- Django admin report generation for teams

## Setup Instructions

### First Time Setup

1. Open the `Stack6CW2` folder in VS Code

2. If using PowerShell, run this first:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

3. Create a virtual environment (first time only, see troubleshooting for command):

4. Activate the virtual environment (You should see `(venv)` appear in your terminal.):

.\venv\Scripts\activate

5. Install all dependencies:

pip install -r requirements.txt

6. Apply database migrations:

python manage.py migrate

7. Create a superuser (admin account):

python manage.py createsuperuser

8. Run the development server:

python manage.py runserver

9. Open your browser and go to `http://127.0.0.1:8000/`

### Returning to the Project

1. Activate the virtual environment:

.\venv\Scripts\activate

2. Run the server:

python manage.py runserver

### Stopping the Server

Press `Ctrl + C` in the terminal.

## Troubleshooting

- **ImportError: Couldn't import Django** — make sure your virtual environment 
  is activated (`.\venv\Scripts\activate`)
- **SecurityError in PowerShell** — run `Set-ExecutionPolicy -ExecutionPolicy 
  RemoteSigned -Scope Process` before activating
- **Command Prompt alternative** — click the `+` dropdown in the VS Code 
  terminal and select Command Prompt, then run `Scripts\activate`