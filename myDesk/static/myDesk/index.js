//Fields and Labels must have the same index!
const companyFields = ['company_name', 'vacation_days', 'company_id']
const companyLabels = ['Company name', 'Vacation days', 'Company id']

document.addEventListener('DOMContentLoaded', function () {
  console.log('Dom Loaded');
    setSectionButtons('company', companyFields, companyLabels)
});

function setSectionButtons(section, fields, labels) {
//EDIT BUTTON
    const edit_buttons = document.querySelectorAll(`.edit-${section}-btn`);
edit_buttons.forEach((button, index) => {
  button.addEventListener(`click`, () => editRecord(index, section, fields, labels));
});
//DELETE BUTTON
const delete_buttons = document.querySelectorAll(`.delete-${section}-btn`);
delete_buttons.forEach((button, index) => {
  button.addEventListener('click', () => deleteRecord(index, section))
})
}

//EDIT
function editRecord(index, section, fields, labels) {
  document.querySelectorAll(`.edit-${section}-view`)[index].style.display =
    'block';
  document.querySelectorAll(`.edit-${section}-btn`)[index].style.display =
    'none';   
    
    document.querySelectorAll(`.edit-${section}-form`)[index].onsubmit = (e) => {
        e.preventDefault();
        const fieldValues = {}
        fields.forEach((field) => {
            fieldValues[`${field}`] = document.querySelectorAll(`.edit-${field}`)[index].value
        })

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
        
        //Display result elements except for ID
        for (const [key, value] of Object.entries(result)) {
            if (key != "id") {
                labelIndex = fields.findIndex((i)=> i == key)
                document.querySelectorAll(`div.${key}, div.edit-${key}`)[index].textContent = `${labels[labelIndex]}: ` + value;
            } 
        }
        });
    return false;
    };
}

//DELETE
function deleteRecord(index, section) {
    // const company_id = document.querySelectorAll(`.delete-${section}_id`)[index];
    // console.log(company_id)
    document.querySelectorAll(`.delete-${section}-form`)[index].onsubmit = (e) => {
      e.preventDefault();
      const fieldsValue = {}
      fieldsValue[`${section}_id`] = document.querySelectorAll(
        `.delete-${section}_id`
      )[index].value;
      
      console.log(fieldsValue)

      fetch(`/delete-${section}`, {
        method: 'POST',
        body: JSON.stringify(fieldsValue),
      })
        .then((response) => response.json())
        .then((result) => {
            document.querySelectorAll(`.${section}`)[index].style.display = 'none';
        });
    };
}

