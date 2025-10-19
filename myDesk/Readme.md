This project is called "myDesk" and is a tool that allows employees of a company to request vacation time to their managers.
The challenge was to implement an app that has 3 different user types: administrator, manager and employee.
Each one of them has specific role and can complete different tasks:

- the Administrators are the ones that build the structure of the app:
  define the company name,
  set-up teams,
  assign a role to the users (default is Employee),
  assign the total vacation days per year for each employee,
  add and remove employees from teams,
  deactivate employees when they leave the company;
  Administrators also report to a Manager and can submit vacation requests-

- the Managers can approve or deny vacation requests. They don't need to submit vacation requests for themselves.

- the Employees can send a vacation request to their manager and have an overview of all vacation requested, approved and denied per year. They can withdraw a request or edit it before approval/deny.

All users has a profile page where they can update their personal information.

For Administrators I wanted to create a dashboard where they can manage company's information, teams and employees. They are of course Superusers and the first one must be created via command line using python manage.py createsuperuser.
The admin dashboard uses javascript (index.js file).
At first I created the structure for adding, editing and deleting companies. Then I realized that I should probably abstract the code in order to avoid repetition (teams and employees records will need the same interaction) and to make the app easily scalable. The index.js file can now manage future Models by simply adding an array with the Model's field and calling a function.

Employees are created by registering a new account via the registration form. This will automatically create a linked profile of the user. Employees cannot be deleted, they can just be deactivated (user property is_active set to false). Inactive users cannot login.

Each user has a profile page where they can edit their information. This page uses only server-side python code whit no javascript.
