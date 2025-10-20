# MyDesk

## Intro

My capstone project is called "myDesk" and is a tool built with Python and JavaScript that allows employees of a company to request vacation days to their managers.
The are 3 different user types: **administrator**, **manager** and **employee**. Each one of them has a specific role and can complete unique tasks:

1. Administrators are the ones that build the structure of the app:

- define the company name,
- set-up teams,
- assign a role to the users (default is Employee),
- assign the total vacation days per year for each employee,
- add and remove employees from teams,
- deactivate employees when they leave the company (Employees cannot be deleted, they can just be deactivated. Inactive users cannot login but their information is still available and they can be reactivated);
  Administrators also report to a Manager and can submit vacation requests.

2. Managers can approve or deny vacation requests. They don't need to submit vacation requests for themselves.

3. Employees can send vacation requests to their manager and have an overview of all vacation requested, approved and denied per year. They can withdraw a request or edit it before approval/deny.

## Setup

Run these commands:
`pip install -r requirements.txt` 
`python manage.py makemigrations`
`python manage.py migrate`.
You also need to create a superuser via `python manage.py createsuperuser`. That is your Admin.

After that please start the server and login to the app. **Please use the Chrome browser!** Navigate to the Admin Dashboard where you will at first create a company record.
When it's done, you will have the possibility to create Teams. Please create at least one Team.
Under New Employees you will find your profile. Click on Edit and fullfill the form with the missing information.

Now logout and register some new user via the registration form. It would be good to create at least 4 users.
Please **do not insert users via the Django Administration**. Users must be created by registering a new account via the registration form. This will automatically create a linked profile of the user.

Login again as Administrator, go to the Admin Dashboard page - New Employees section and complete the new profiles by adding the missing information: assign a team, grant a role and set start employment date. The employees will be moved under their respective team.
I suggest to create at least 2 Teams and assign them at least Manager and a normal Employee.

Now you can start using the app by logging into different accounts, send vacation requests and approve/deny them.

## How to use this app

For a normal employee the app is essentially a single page app. After login, they will see a welcome page with their personal and work information in a section called Profile.
The Vacation summary section shows them the vacation request status, the vacation days already taken and how many are left for the current year.
The section below is about vacation requests. Here they can see the requests they already sent, their status and can send a new one by simply filling the form.
Sent request that are not yet been processed by the manager can be edited or deleted. If a request was denied, it can be deleted.

For Managers there is a different visualization of the Welcome page. They see an alert if there are new requests to be processed and an overview of all requests. The ones to be processed are shown as forms with the buttons to approve or deny the request. There is also the possibility to leave a message for the employee if necessary.
Managers don't submit vacation requests for themselves.

Admin users has an additional admin page where they can create and edit Teams and manage new employees.
If a new user registered, the administrator will see a notification in the Welcome page that let him know that an action is required. He will find the new user in the New Employee section and can fill the missing information. Once a user is assigned to a team, he will appear in the relevant Team section.
Admin can also remove users from teams, change their role or vacation days number. Finally they can deactivate a user by clicking on Deactivate (the user will be moved to the bottom of the page in the section Inactive Employees and can be reactivated any time). As a precaution, Admin cannot deactivate their own account.
If an Admin delete a Team, all of its members will be moved under the New Employee section until further team assignment.
In the Welcome page they can submit vacation requests to their manager.

## Distinctiveness and Complexity

I believe the distinctiveness and complexity of this project resides in the different user's role and in the 3 apps that includes.

### User Role

I had to find a way to keep track of the current user role in order to show or hide features in the HTML templates and I also needed a way to filter database queries in order to provide tailored results to the user.

1. HTML template:

- Administrator should be the only ones who can access the admin dashboard. The dashboard requires a high awareness of what the user is doing, so I made sure to check that only members of the Django "is_staff" group (i.e. superusers) can see and access this section. An info appears in the welcome page if there are new users.
- Managers don't need to send vacation requests, so they don't see this section. However they are responsible for approving or denying their team members vacation requests, so they have a section just for that. An info appears if they need to process requests.
- Employees only see their vacation requests and can submit one.

2. Database queries:

- Administrator can edit and delete almost everything exept vacation requests (for that they should use the Django Administration). They also cannot deactivate their own account (as a safety measure).
- Managers can retreive only vacation request of their team (not from others). The query needed to do that was challenging. The function select_related() was very helpful to gather information in a more efficient way.

### Apps

There are 3 apps in this project: _authenticate_, _adminDashboard_ and _myDesk_.

1. _authenticate_ is the app responsible for the registration of new users and login/logout. When a new user registers, a new profile is created and linked uniquely to that user. After reading some articles on the matter, this was considered best practice. This way additional information about the employee (team assigned, employment start date etc) will be stored separately in the profile leaving the registration information untouched. I used here the standard Django authentication feature and just made firstname and lastname mandatory.
Each user has a profile page (profile.html) where they can edit their information. This page uses only server-side python code whith no javascript.

2. _adminDashboard_ was created to keep the administrative tasks separate from the rest. This way it should be easier to add new features in the future or maintain the code without impacting the main app.
At first I created the admin-dashboard.html and the index.js file with the javascript code for adding, editing and deleting companies. Then I realized that I should probably abstract the code in order to avoid repetition (teams and employees Models will need the same interaction with the database) and to make the app easily scalable. The solution I implemented was to call a generic function and pass parameters related to the different section of the Admin Dashboard (Company, Team and Employee). I used class names in the html and template literals in javascript in order to achieve this.
The index.js file can now manage future Django Models by simply adding an array with the Model's fields and calling the function.
The solution worked well, so I extended it to handle the vacation requests too (even if they actually are part of another app).

3. _myDesk_ is the main app of the project and is essentially a dashboard (index.html) where employees see their vacation status and can send a new request and managers can process them.
For Employees it shows how many vacation days has been already used and how many are left. It was challenging to find the right way to calculate days between dates and to implement a verification process to avoid sending bad vacation requests. The request should not start in the past, the end date must be after the start date (or at least the same day) and finally it should not overlap with other requests already sent by the user. It took some time to research the internet for a good solution but I believe I found the right one.
For Managers there is a different dashboard where they see the requests and can act on them.

## Final thoughts

I tried to implement all the topics of the course and I am very happy with the result. However it would be even better if I could have implemented React. Unfortunately the CDN integration is deprecated and I didn't want to risk that, at the time you review my code, the app doesn't work because of that.
Thank you for making this course available for everyone. I enjoyed it very much and will surely follow another one in the future.
Greetings from Berlin, Germany. Angelo.
