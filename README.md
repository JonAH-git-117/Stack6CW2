This project focuses on developing a web application for internal teams 
at Sky Broadband to see what teams others are in.

    The project aims to improve our communication and skills with Python and Django.

    The project also is aimed at improving upon our web development skills, as both 
    HTML and CSS are being utilised to improve upon the look of the webpages.

    If you see ImportError: Couldn't import Django or a SecurityError in PowerShell:

        Switch Terminal: In VS Code, click the + dropdown in the terminal and select Command Prompt.

        Activate: Run Scripts\activate. You should see (Scripts) appear at the start of your command line.

        Unblock PowerShell (Optional): If you must use PowerShell, run the following commands in the terminal: 
        - "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process" 
        - ".\Scripts\activate"

    Iniital Steps for project setup

        Open the `Stack6Cw2` folder in VS Code.

        Run this in the VS Code terminal: "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process"

        Only do this one time when working on this for the first time to create a virtual environment: "python -m venv venv"

        Activate Environment: ".\venv\Scripts\activate"

        (Confirm you see `(venv)` in green text in your terminal)

        Install Django & Requirements: "pip install -r requirements.txt"

        Sync Database: "python manage.py migrate"

        Run Server: "python manage.py runserver"