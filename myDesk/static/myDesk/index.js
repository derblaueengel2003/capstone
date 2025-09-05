const companyFields = ['company_name', 'company_id']
const teamFields = ['team_name', 'team_id']
const employeeFields = [
  'user',
  'team',
  'role',
  'employement_date',
  'vacation_days',
  'employee_id',
];

function setSectionButtons(section, fields) {
//EDIT BUTTON
const edit_buttons = document.querySelectorAll(`.edit-${section}-btn`);
edit_buttons.forEach((button, index) => {
  button.addEventListener(`click`, () => editRecord(index, section, fields));
});
//DELETE BUTTON
const delete_buttons = document.querySelectorAll(`.delete-${section}-btn`);
delete_buttons.forEach((button, index) => {
  button.addEventListener('click', () => deleteRecord(index, section))
})
}

document.addEventListener('DOMContentLoaded', function () {
  console.log('Dom Loaded');
    setSectionButtons('company', companyFields);
    setSectionButtons('team', teamFields);
    setSectionButtons('employee', employeeFields);
});


//EDIT
function editRecord(index, section, fields) {
    console.log(index, section, fields)
  document.querySelectorAll(`.edit-${section}-view`)[index].style.display =
    'block';
  document.querySelectorAll(`.edit-${section}-btn`)[index].style.display =
    'none';   
    
    document.querySelectorAll(`.edit-${section}-form`)[index].onsubmit = (e) => {
        // e.preventDefault();
        console.log(e)
        const fieldValues = {}
        fields.forEach((field) => {
            fieldValues[`${field}`] = document.querySelectorAll(`.edit-${field}`)[index].value
        })

        console.log(fieldValues)

    fetch(`/edit-${section}`, {
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
        console.log(result)
        window.location.reload()
        });
    return false;
    };
}

//DELETE
function deleteRecord(index, section) {
    document.querySelectorAll(`.delete-${section}-form`)[index].onsubmit = (e) => {
    //   e.preventDefault();
      const fieldsValue = {}
      fieldsValue[`${section}_id`] = document.querySelectorAll(
        `.delete-${section}_id`
      )[index].value;
      
      console.log(fieldsValue)

      fetch(`/delete-${section}`, {
        method: 'POST',
        body: JSON.stringify(fieldsValue),
      })
        // .then((response) => response.json())
        .then((response) => {
            document.querySelectorAll(`.${section}`)[index].style.display = 'none';
        window.location.reload();

        });
    };
}

