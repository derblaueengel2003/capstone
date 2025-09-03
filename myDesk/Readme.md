This project is called "myDesk" and is a simple tool that allows employees of a company to request vacation time to their manager.
The difficulty was to implement an app that has 3 different user types: administrator, manager and employee.
Each one of them has specific permissions and can complete different tasks:
    - the Administrators are the ones that build the structure of the app: they define the company names, the total vacation days allowed in a year for each company, set-up teams and employees and finally grant permissions to the users;
    - the Managers can approve or deny vacation request, can add and remove employees from teams, can add a new employee or remove those who left the company;
    - the Employees can send a vacation request to their manager and have an overview of all vacation requested, approved and denied per year. They can withdraw a request. 

For Administrators I wanted to create a dashboard where they can manage companies, teams and employees. They are of course Superusers and the first one must be created via command line using python manage.py createsuperuser.
At first I created the structure for adding, editing and deleting companies. Then I realized that I should probably abstract the code in order to avoid repetition (teams and employees records will need the same interaction) and to make the app easily scalable. The index.js file can now manage future Models by simply adding an array with the Model's field and calling a function.