const requestFields = ['start_date', 'end_date', 'request_id'];

document.addEventListener('DOMContentLoaded', function () {
  setSectionButtons('request', requestFields);
  setDecisionForms();
});

function setSectionButtons(section, fields) {
  const editButtons = document.querySelectorAll(`.edit-${section}-btn`);
  editButtons.forEach((button, index) => {
    button.addEventListener('click', () => editRecord(index, section, fields));
  });

  const deleteForms = document.querySelectorAll(`.delete-${section}-form`);
  deleteForms.forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      deleteRecord(form, section);
    });
  });
}

function editRecord(index, section, fields) {
  const editViews = document.querySelectorAll(`.edit-${section}-view`);
  const editButtons = document.querySelectorAll(`.edit-${section}-btn`);
  const editForms = document.querySelectorAll(`.edit-${section}-form`);

  editViews[index].style.display = 'block';
  editButtons[index].style.display = 'none';

  editForms[index].onsubmit = () => {
    const fieldValues = {};
    fields.forEach((field) => {
      fieldValues[field] = document.querySelectorAll(`.edit-${field}`)[
        index
      ].value;
    });

    fetch(`/edit-${section}`, {
      method: 'POST',
      body: JSON.stringify(fieldValues),
    })
      .then((response) => response.json())
      .then(() => {
        editViews[index].style.display = 'none';
        editButtons[index].style.display = 'block';
        window.location.reload();
      });

    return false;
  };
}

function deleteRecord(form, section) {
  const fieldsValue = {};
  fieldsValue[`${section}_id`] = form.querySelector(
    `.delete-${section}_id`
  ).value;

  fetch(`/delete-${section}`, {
    method: 'POST',
    body: JSON.stringify(fieldsValue),
  }).then(() => {
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
      })
        .then((response) => response.json())
        .then(() => {
          window.location.reload();
        });
    });
  });
}
