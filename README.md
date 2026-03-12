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

    Open the Project: Open the Stack6Cw2 folder in VS Code.

        Enable Scripts (Windows/PowerShell only): 
        If you see a "Scripts disabled" error, run this command to allow the environment to start:
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
        
        Create your Virtual Environment: This creates a private "toolbox" folder called venv inside the project. 
        Run: python -m venv venv
        
        Activate the Environment: This "wakes up" the toolbox so your terminal knows to use the project's specific tools. 
        Run: .\venv\Scripts\activate
        (Note: You must see (venv) in green text at the start of your terminal line before moving to the next step!)
        
        Install Django: Python doesn't come with Django automatically. 
        Run this to install it inside your venv: pip install django
        
        Install Other Requirements: Run this to install any other tools the team has added:
        pip install -r requirements.txt
        
        Sync the Database: This creates the tables (Organisations, Departments, Teams) on your local machine:
        python manage.py migrate
        
        Launch the App: Run the server to view the website in your browser:
        python manage.py runserver
        
        Important Note: Never upload the venv folder to GitHub. It is already included in our .gitignore file. 
        Each team member creates their own local venv using Step 3.
