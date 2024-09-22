import tkinter as tk
from tkinter import messagebox
import json
import os.path
from pymongo import MongoClient


# Determine the Downloads folder path
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
file_path = os.path.join(downloads_folder, "questions.json")

# Load questions from JSON file
with open(file_path, 'r') as file:
    data = json.load(file)


exam_name = data['exam_name']
num_questions = data['num_questions']
questions = data['questions']

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['exam_db']
collection = db['results']


class ExamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiple Choice Exam")
        self.current_question = 0
        self.score = 0
        self.answers = [None] * num_questions
        self.exam_taker = ""
        self.time_left = 30  # Customize the timer duration here (in seconds)

        self.landing_page()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def landing_page(self):
        self.clear_window()
        tk.Label(self.root, text=exam_name, font=("Helvetica", 16)).pack(pady=20)
        tk.Label(self.root, text=f"Number of Questions: {num_questions}", font=("Helvetica", 12)).pack(pady=10)
        tk.Label(self.root, text="Enter your name:", font=("Helvetica", 12)).pack(pady=10)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=10)
        tk.Button(self.root, text="Start Exam", command=self.start_exam).pack(pady=20)

    def start_exam(self):
        self.exam_taker = self.name_entry.get()
        if not self.exam_taker:
            messagebox.showwarning("Warning", "Please enter your name")
            return
        self.clear_window()
        self.question_label = tk.Label(self.root, text="", wraplength=400)
        self.question_label.pack(pady=20)

        self.var = tk.StringVar()
        self.options = [tk.Radiobutton(self.root, text="", variable=self.var, value=i) for i in range(4)]
        for option in self.options:
            option.pack(anchor='w')

        self.prev_button = tk.Button(self.root, text="Previous", command=self.prev_question)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.next_button = tk.Button(self.root, text="Next", command=self.next_question)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.timer_label = tk.Label(self.root, text=f"Time left: {self.time_left} seconds")
        self.timer_label.pack(pady=10)

        self.load_question()
        self.update_timer()

    def load_question(self):
        question = questions[self.current_question]
        self.question_label.config(text=question['question'])
        self.var.set(self.answers[self.current_question] if self.answers[self.current_question] is not None else "")
        for i, option in enumerate(question['options']):
            self.options[i].config(text=option)

    def next_question(self):
        selected_option = self.var.get()
        if selected_option == "":
            messagebox.showwarning("Warning", "Please select an option")
            return

        self.answers[self.current_question] = selected_option
        if selected_option == questions[self.current_question]['answer']:
            self.score += 1

        self.current_question += 1
        if self.current_question < len(questions):
            self.load_question()
        else:
            self.submit_results()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.load_question()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time left: {self.time_left} seconds")
            self.root.after(1000, self.update_timer)
        else:
            self.submit_results()

    def submit_results(self):
        result = {
            "exam_name": exam_name,
            "exam_taker": self.exam_taker,
            "score": self.score,
            "answers": self.answers
        }
        collection.insert_one(result)
        messagebox.showinfo("Results", "End of Exam")
        messagebox.showinfo("Results", f"Your score: {self.score}/{len(questions)}")
        self.root.quit()

    def on_closing(self):
        self.save_progress()
        self.root.destroy()

    def save_progress(self):
        result = {
            "exam_name": exam_name,
            "exam_taker": self.exam_taker,
            "score": self.score,
            "answers": self.answers
        }
        collection.insert_one(result)
        print("Progress saved!")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExamApp(root)
    root.mainloop()
