// Show and hide forms based on user's choice
function showTextInput() {
  document.getElementById('textForm').style.display = 'block';
  document.getElementById('imageForm').style.display = 'none';
  document.querySelector('.options').style.display = 'none';
  document.getElementById('textResult').innerText = '';
  document.getElementById('imageResult').innerText = '';
}

function showImageUpload() {
  document.getElementById('textForm').style.display = 'none';
  document.getElementById('imageForm').style.display = 'block';
  document.querySelector('.options').style.display = 'none';
  document.getElementById('textResult').innerText = '';
  document.getElementById('imageResult').innerText = '';
}


// Show loading indicator
function showLoading() {
  document.getElementById('loading').style.display = 'block';
}

// Hide loading indicator
function hideLoading() {
  document.getElementById('loading').style.display = 'none';
}

// Submit text for fact-checking
function submitText() {
  const text = document.getElementById('textInput').value;
  if (!text.trim()) {
    alert("Please enter a claim or URL.");
    return;
  }

  const submitBtn = document.querySelector('#textForm button');
  submitBtn.disabled = true;
  showLoading();

  fetch('/fact-check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  .then(response => response.json())
  .then(data => {
    hideLoading();
    submitBtn.disabled = false;
    document.getElementById('textResult').textContent = data.result;
  })
  .catch(error => {
    hideLoading();
    submitBtn.disabled = false;
    document.getElementById('textResult').textContent = 'Error: ' + error;
  });
}

function submitImage() {
  const imageFile = document.getElementById('imageInput').files[0];
  if (!imageFile) {
    alert("Please upload an image.");
    return;
  }

  const submitBtn = document.querySelector('#imageForm button');
  submitBtn.disabled = true;
  showLoading();

  const formData = new FormData();
  formData.append("image", imageFile);

  fetch('/analyze-image', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    hideLoading();
    submitBtn.disabled = false;
    document.getElementById('imageResult').textContent = data.result;
  })
  .catch(error => {
    hideLoading();
    submitBtn.disabled = false;
    document.getElementById('imageResult').textContent = 'Error: ' + error;
  });
}

function scrollToResult(id) {
  document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}

// then call inside .then() after setting the result:
scrollToResult('textResult');
// or
scrollToResult('imageResult');
