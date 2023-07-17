import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")

        # Create a frame to hold the category labels
        category_frame = tk.Frame(root)
        category_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Create category labels for "Task" and "Due Date"
        task_label = tk.Label(category_frame, text="Task", width=30, anchor=tk.W)
        task_label.grid(row=0, column=0, sticky=tk.W)
        due_date_label = tk.Label(category_frame, text="Due Date", width=30, anchor=tk.W)
        due_date_label.grid(row=0, column=1, sticky=tk.W)

        # Create a frame to hold the task list
        task_frame = tk.Frame(root)
        task_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a scrollbar for the task list
        scrollbar = tk.Scrollbar(task_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a listbox to display tasks
        self.task_listbox = tk.Listbox(task_frame, width=60, yscrollcommand=scrollbar.set)
        self.task_listbox.pack()

        # Attach the scrollbar to the task listbox
        scrollbar.config(command=self.task_listbox.yview)

        # Create a frame to hold the buttons
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.RIGHT, padx=10)

        # Create buttons for task operations
        create_button = tk.Button(button_frame, text="Create Task", command=self.open_create_window)
        create_button.pack(pady=5)

        edit_button = tk.Button(button_frame, text="Edit Task", command=self.open_edit_window)
        edit_button.pack(pady=5)

        delete_button = tk.Button(button_frame, text="Delete Task", command=self.delete_task)
        delete_button.pack(pady=5)

        # Connect to the database
        self.conn = sqlite3.connect(r"C:\Users\Tanya\Desktop\task_manager.db")
        self.cursor = self.conn.cursor()

        # Fetch tasks from the database and display them in the listbox
        self.fetch_tasks()

    def fetch_tasks(self):
        self.task_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM tasks")
        tasks = self.cursor.fetchall()
        for task in tasks:
            self.task_listbox.insert(tk.END, f"{task[1]:<30} {task[2]:<30}")

    def open_create_window(self):
        # Create a new window for creating a task
        create_window = tk.Toplevel(self.root)
        create_window.title("Create Task")

        # Entry for task name
        task_label = tk.Label(create_window, text="Task Name:")
        task_label.pack()
        task_entry = tk.Entry(create_window)
        task_entry.pack(pady=5)

        # Calendar for task due date
        due_date_label = tk.Label(create_window, text="Due Date:")
        due_date_label.pack()
        due_date_cal = DateEntry(create_window, date_pattern="yyyy-mm-dd")
        due_date_cal.pack(pady=5)

        # Button to save the task
        save_button = tk.Button(create_window, text="Save Task", command=lambda: self.save_task(create_window, task_entry.get(), due_date_cal.get()))
        save_button.pack(pady=10)

    def save_task(self, window, task, due_date):
        if task:
            self.cursor.execute("INSERT INTO tasks (task_name, due_date) VALUES (?, ?)", (task, due_date))
            self.conn.commit()
            self.fetch_tasks()
            window.destroy()
        else:
            messagebox.showwarning("Task Creation", "Task name cannot be empty.")

    def open_edit_window(self):
        selected_task = self.task_listbox.curselection()
        if selected_task:
            task = self.task_listbox.get(selected_task[0]).split()[0]
            current_due_date = self.cursor.execute("SELECT due_date FROM tasks WHERE task_name = ?", (task,)).fetchone()[0]

            # Create a new window for editing the task
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Task")

            # Entry for task name
            task_label = tk.Label(edit_window, text="Task Name:")
            task_label.pack()
            task_entry = tk.Entry(edit_window)
            task_entry.insert(tk.END, task)
            task_entry.pack(pady=5)

            # Calendar for task due date
            due_date_label = tk.Label(edit_window, text="Due Date:")
            due_date_label.pack()
            due_date_cal = DateEntry(edit_window, date_pattern="yyyy-mm-dd")
            due_date_cal.set_date(current_due_date)
            due_date_cal.pack(pady=5)

            # Button to save the edited task
            save_button = tk.Button(edit_window, text="Save Task", command=lambda: self.save_edited_task(edit_window, task, task_entry.get(), due_date_cal.get()))
            save_button.pack(pady=10)
        else:
            messagebox.showwarning("Task Editing", "Please select a task to edit.")

    def save_edited_task(self, window, old_task, new_task, new_due_date):
        if new_task:
            self.cursor.execute("UPDATE tasks SET task_name = ?, due_date = ? WHERE task_name = ?", (new_task, new_due_date, old_task))
            self.conn.commit()
            self.fetch_tasks()
            window.destroy()
        else:
            messagebox.showwarning("Task Editing", "Task name cannot be empty.")

    def delete_task(self):
        selected_task = self.task_listbox.curselection()
        if selected_task:
            task = self.task_listbox.get(selected_task[0]).split()[0]
            self.cursor.execute("DELETE FROM tasks WHERE task_name = ?", (task,))
            self.conn.commit()
            self.fetch_tasks()
        else:
            messagebox.showwarning("Task Deletion", "Please select a task to delete.")

    def __del__(self):
        # Close the connection when the object is destroyed
        self.cursor.close()
        self.conn.close()

root = tk.Tk()
task_manager = TaskManager(root)
root.mainloop()
