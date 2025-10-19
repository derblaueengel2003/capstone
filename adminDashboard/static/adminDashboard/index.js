const companyFields = ['company_name', 'company_id'];
const teamFields = ['team_name', 'team_id'];
const employeeFields = [
  'team',
  'role',
  'employment_date',
  'vacation_days',
  'employee_id',
];
const requestFields = ['start_date', 'end_date', 'request_id'];

document.addEventListener('DOMContentLoaded', function () {
  console.log('Dom Loaded');
  setSectionButtons('company', companyFields, '/admin-dashboard');
  setSectionButtons('team', teamFields, '/admin-dashboard');
  setSectionButtons('employee', employeeFields, '/admin-dashboard');
  setSectionButtons('request', requestFields, '');
  setDecisionForms();
});

function setSectionButtons(section, fields, sectionPath) {
  //EDIT BUTTON
  const edit_buttons = document.querySelectorAll(`.edit-${section}-btn`);
  edit_buttons.forEach((button, index) => {
    button.addEventListener(`click`, () =>
      editRecord(index, section, fields, sectionPath)
    );
  });
  //DELETE BUTTON
  const delete_forms = document.querySelectorAll(`.delete-${section}-form`);
  delete_forms.forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();

      if (section === 'team') {
        const confirmed = window.confirm(
          'Are you sure you want to delete this team? This will remove the team from all assigned employees.'
        );
        if (!confirmed) {
          return;
        }
      }

      deleteRecord(form, section, sectionPath);
    });
  });
}

//EDIT
function editRecord(index, section, fields, sectionPath) {
  console.log(index, section, fields, sectionPath);
  document.querySelectorAll(`.edit-${section}-view`)[index].style.display =
    'block';
  document.querySelectorAll(`.edit-${section}-btn`)[index].style.display =
    'none';

  document.querySelectorAll(`.edit-${section}-form`)[index].onsubmit = () => {
    const fieldValues = {};
    fields.forEach((field) => {
      fieldValues[`${field}`] = document.querySelectorAll(`.edit-${field}`)[
        index
      ].value;
    });

    fetch(`${sectionPath}/edit-${section}`, {
      method: 'POST',
      body: JSON.stringify(fieldValues),
    })
      .then((response) => response.json())
      .then((result) => {
        document.querySelectorAll(`.edit-${section}-view`)[
          index
        ].style.display = 'none';
        document.querySelectorAll(`.edit-${section}-btn`)[index].style.display =
          'block';

        window.location.reload();
      });
    return false;
  };
}

//DELETE
function deleteRecord(form, section, sectionPath) {
  const fieldsValue = {};
  fieldsValue[`${section}_id`] = form.querySelector(
    `.delete-${section}_id`
  ).value;

  console.log(fieldsValue);

  fetch(`${sectionPath}/delete-${section}`, {
    method: 'POST',
    body: JSON.stringify(fieldsValue),
  }).then((response) => {
    window.location.reload();
  });
}

function setDecisionForms() {
  const decisionForms = document.querySelectorAll('.decision-request-form');

  decisionForms.forEach((form) => {
    const buttons = form.querySelectorAll('.decision-btn');
    const decisionInput = form.querySelector('.decision-action');
    const messageInput = form.querySelector('.decision-message');

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        decisionInput.value = button.dataset.decision;
      });
    });

    form.addEventListener('submit', (event) => {
      event.preventDefault();

      const payload = {
        request_id: form.querySelector('.decision-request_id').value,
        decision: decisionInput.value,
        manager_message: messageInput.value,
      };

      fetch('/update-request-status', {
        method: 'POST',
        body: JSON.stringify(payload),
      }).then((response) => {
        window.location.reload();
      });
    });
  });
}
