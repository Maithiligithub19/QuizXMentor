import pandas as pd

# Sample data for the quiz questions
data = {
"Question": [
"What is the capital of France?",
"Which planet is known as the Red Planet?",
"What is the largest mammal?",
"Which language is primarily used for Android development?",
"What is the chemical symbol for gold?",
"Who wrote 'Romeo and Juliet'?",
"What is the boiling point of water in Celsius?",
"Which is the longest river in the world?",
"What year did the Titanic sink?",
"Who is known as the father of modern physics?"
],
"Option_A": [
"London", "Venus", "Elephant", "Python", "Go", "Charles Dickens", "90", "Nile", "1912", "Isaac Newton"
],
"Option_B": [
"Paris", "Mars", "Blue Whale", "Java", "Au", "William Shakespeare", "100", "Amazon", "1905", "Galileo Galilei"
],
"Option_C": [
"Berlin", "Jupiter", "Giraffe", "JavaScript", "Ag", "Mark Twain", "110", "Yangtze", "1918", "Albert Einstein"
],
"Option_D": [
"Madrid", "Saturn", "Polar Bear", "C++", "Pt", "Jane Austen", "120", "Mississippi", "1920", "Stephen Hawking"
],
"Correct_Ans": [
"B", "B", "B", "B", "B", "B", "B", "A", "A", "C"
]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
df.to_excel("questions_template.xlsx", index=False, engine='openpyxl')