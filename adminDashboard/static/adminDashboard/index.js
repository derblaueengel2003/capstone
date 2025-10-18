const companyFields = ['company_name', 'company_id']
const teamFields = ['team_name', 'team_id']
const employeeFields = [
  'team',
  'role',
  'employment_date',
  'vacation_days',
  'employee_id',
];
const requestFields = ['start_date', 'end_date', 'request_id']


document.addEventListener('DOMContentLoaded', function () {
  console.log('Dom Loaded');
  setSectionButtons('company', companyFields);
  setSectionButtons('team', teamFields);
  setSectionButtons('employee', employeeFields);
  setSectionButtons('request', requestFields)
});

function setSectionButtons(section, fields) {
//EDIT BUTTON
const edit_buttons = document.querySelectorAll(`.edit-${section}-btn`);
edit_buttons.forEach((button, index) => {
  button.addEventListener(`click`, () => editRecord(index, section, fields));
});
//DELETE FORM
const delete_forms = document.querySelectorAll(`.delete-${section}-form`);
delete_forms.forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    deleteRecord(form, section);
  });
});
}

//EDIT
function editRecord(index, section, fields) {
  console.log(index, section, fields)
  document.querySelectorAll(`.edit-${section}-view`)[index].style.display =
    'block';
  document.querySelectorAll(`.edit-${section}-btn`)[index].style.display =
    'none';   
    
    document.querySelectorAll(`.edit-${section}-form`)[index].onsubmit = () => {
        const fieldValues = {}
        fields.forEach((field) => {
            fieldValues[`${field}`] = document.querySelectorAll(`.edit-${field}`)[index].value
        })

    fetch(`/admin-dashboard/edit-${section}`, {
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
        
        window.location.reload()
        });
    return false;
    };
}

//DELETE
function deleteRecord(form, section) {
  const idField = form.querySelector(`.delete-${section}_id`);
  if (!idField) {
    return;
  }

  const fieldsValue = {};
  fieldsValue[`${section}_id`] = idField.value;

  fetch(`/admin-dashboard/delete-${section}`, {
    method: 'POST',
    body: JSON.stringify(fieldsValue),
  }).then(() => {
    window.location.reload();
  });
}
