document.addEventListener('DOMContentLoaded', function() {
// Fetch questions and display them
fetch('/questions')
.then(response => response.json())
.then(questions => {
const container = document.getElementById('quiz-container');
questions.forEach((question, index) => {
container.innerHTML += `
<div class="question">
<p>${index + 1}. ${question.question}</p>
<form>
<input type="radio" name="question${index}" value="A"> ${question.option_a}<br>
<input type="radio" name="question${index}" value="B"> ${question.option_b}<br>
<input type="radio" name="question${index}" value="C"> ${question.option_c}<br>
<input type="radio" name="question${index}" value="D"> ${question.option_d}<br>
</form>
</div>
`;
});
});
});