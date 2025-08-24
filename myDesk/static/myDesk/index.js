document.addEventListener('DOMContentLoaded', function () {
  console.log('Dom Loaded');

  const edit_company_buttons = document.querySelectorAll(`.edit-company-btn`);
  edit_company_buttons.forEach((button, index) => {
    button.addEventListener(`click`, () => edit_company(index));
  });

  const delete_company_buttons = document.querySelectorAll('.delete-company-btn');
  delete_company_buttons.forEach((button, index) => {
    button.addEventListener('click', () => delete_company(index))
  })
});

function edit_company(index) {
  document.querySelectorAll('.edit-company-view')[index].style.display = 'block';
  document.querySelectorAll('.edit-company-btn')[index].style.display = 'none';

  const company_name = document.querySelectorAll('.edit-company-name')[index];
  const vacation_days = document.querySelectorAll('.edit-vacation-days')[index];
  const company_id = document.querySelectorAll('.company-id')[index];

  document.querySelectorAll('.edit-company-form')[index].onsubmit = (e) => {
    e.preventDefault();
    fetch('/edit-company', {
      method: 'POST',
      body: JSON.stringify({
        company_name: company_name.value,
        vacation_days: vacation_days.value,
        company_id: company_id.value,
      }),
    })
      .then((response) => response.json())
      .then((result) => {
        document.querySelectorAll('.edit-company-view')[index].style.display = 'none';
        document.querySelectorAll('.edit-company-btn')[index].style.display = 'block';
       
        document.querySelectorAll('div.company-name, div.edit-company-name')[index].textContent = "Company name: "+
          result.company_name;
        document.querySelectorAll('div.vacation-days, div.edit-vacation-days')[index].textContent = "Vacation days: "+
          result.vacation_days;
      });
    return false;
  };
}

function delete_company(index) {
    const company_id = document.querySelectorAll('.delete-company-id')[index];
    console.log(company_id)
    document.querySelectorAll('.delete-company-form')[index].onsubmit = (e) => {
      e.preventDefault();
      fetch(`/delete-company`, {
        method: 'POST',
        body: JSON.stringify({
          company_id: company_id.value,
        }),
      })
        .then((response) => response.json())
        .then((result) => {
            document.querySelectorAll('.company')[index].style.display = 'none';
        });
    };
}

