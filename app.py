import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from tkcalendar import DateEntry
import threading
import time
import queue
from tkinter import font as tkfont

class TodoApp:
    # function for initializing the application
    def __init__(self, root):
        self.root = root
        self.root.title("To-do Manager")
        self.root.geometry("800x600")
        
        self.dark_bg = "#1E1E1E"
        self.dark_secondary = "#252526"
        self.dark_accent = "#333333"
        self.text_color = "#D4D4D4"
        self.accent_blue = "#007ACC"
        self.accent_green = "#6A9955"
        self.accent_red = "#F44747"
        
        self.root.configure(bg=self.dark_bg)
        
        self.configure_styles()
        
        self.init_database()
        
        self.reminder_queue = queue.Queue()
        
        self.create_widgets()
        
        self.load_tasks()
        
        self.stop_thread = False
        self.reminder_thread = threading.Thread(target=self.reminder_checker)
        self.reminder_thread.daemon = True
        self.reminder_thread.start()
        
        self.process_reminder_queue()

    # function for defining and setting the styles for the application 
    def configure_styles(self):
        style = ttk.Style()
        
        style.configure("Treeview",
                         background=self.dark_accent,
                         foreground=self.text_color,
                         rowheight=25,
                         fieldbackground=self.dark_accent)
        
        style.configure("Treeview.Heading",
                         background=self.dark_secondary,
                         foreground=self.text_color,
                         relief="flat")
        
        style.map("Treeview.Heading",
                   background=[('active', self.dark_accent)])
        
        style.map("Treeview",
                   background=[('selected', self.accent_blue)],
                   foreground=[('selected', 'white')])
        
        style.configure("TButton",
                         background=self.dark_accent,
                         foreground=self.text_color,
                         borderwidth=1,
                         focusthickness=3,
                         focuscolor=self.accent_blue)
        
        style.map("TButton",
                   background=[('active', self.accent_blue)],
                   relief=[('pressed', 'sunken')])
        
        style.configure("TFrame", background=self.dark_bg)
        style.configure("TLabel", background=self.dark_bg, foreground=self.text_color)
        style.configure("TEntry", fieldbackground=self.dark_accent, foreground=self.text_color)
        
        style.configure("my.DateEntry", 
                        fieldbackground=self.dark_accent,
                        background=self.dark_accent,
                        foreground=self.text_color,
                        arrowcolor=self.text_color)

    # function for initializing the database
    def init_database(self):
        try:
            self.conn = sqlite3.connect("to-do.db")
            self.cursor = self.conn.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    deadline TEXT,
                    status TEXT DEFAULT 'Pending',
                    reminder INTEGER DEFAULT 0
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")
    
    # function for creating the widgets for the application
    def create_widgets(self):
        self.title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=10)
        self.button_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="To-do Manager", 
                               font=self.title_font, bg=self.dark_bg, fg=self.accent_blue)
        title_label.pack(pady=(0, 20))
        
        input_frame = tk.Frame(main_frame, bg=self.dark_secondary, bd=1, relief=tk.GROOVE, padx=15, pady=15)
        input_frame.pack(fill="x", pady=10)
        
        title_row = tk.Frame(input_frame, bg=self.dark_secondary)
        title_row.pack(fill="x", pady=5)
        
        tk.Label(title_row, text="Title:", bg=self.dark_secondary, fg=self.text_color, 
            font=self.label_font, width=10).pack(side="left", anchor="w")
        
        self.title_entry = tk.Entry(title_row, width=40, bg=self.dark_accent, fg=self.text_color, 
                                   insertbackground=self.text_color, relief=tk.FLAT, bd=5)
        self.title_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        desc_row = tk.Frame(input_frame, bg=self.dark_secondary)
        desc_row.pack(fill="x", pady=5)
        
        tk.Label(desc_row, text="Description:", bg=self.dark_secondary, fg=self.text_color, 
                font=self.label_font, width=10).pack(side="left", anchor="w")
        
        self.desc_entry = tk.Entry(desc_row, width=40, bg=self.dark_accent, fg=self.text_color, 
                                  insertbackground=self.text_color, relief=tk.FLAT, bd=5)
        self.desc_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        date_status_row = tk.Frame(input_frame, bg=self.dark_secondary)
        date_status_row.pack(fill="x", pady=5)
        
        date_frame = tk.Frame(date_status_row, bg=self.dark_secondary)
        date_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(date_frame, text="Deadline:", bg=self.dark_secondary, fg=self.text_color, 
                font=self.label_font, width=10).pack(side="left", anchor="w")
        
        calendar_frame = tk.Frame(date_frame, bg=self.dark_secondary)
        calendar_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.deadline_entry = DateEntry(calendar_frame, width=12, 
                                      background=self.dark_accent,
                                      foreground=self.text_color, 
                                      borderwidth=0,
                                      highlightthickness=1,
                                      highlightbackground=self.dark_accent,
                                      highlightcolor=self.accent_blue,
                                      date_pattern='yyyy-mm-dd',
                                      selectmode='day',
                                      state="readonly")
        self.deadline_entry.pack(side="left", fill="x")
        
        status_frame = tk.Frame(date_status_row, bg=self.dark_secondary)
        status_frame.pack(side="right", padx=10)
        
        tk.Label(status_frame, text="Status:", bg=self.dark_secondary, fg=self.text_color, 
                font=self.label_font, width="10").pack(side="left", padx=5)
        
        self.status_var = tk.StringVar(value="Pending")
        self.status_combo = ttk.Combobox(status_frame, textvariable=self.status_var, width=10, 
                                        values=["Pending", "In Progress", "Completed"], 
                                        state="readonly")
        self.status_combo.pack(side="left")
        
        reminder_frame = tk.Frame(input_frame, bg=self.dark_secondary)
        reminder_frame.pack(fill="x", pady=5)
        
        self.reminder_var = tk.BooleanVar(value=False)
        self.reminder_check = tk.Checkbutton(reminder_frame, text="Set reminder", 
                                           variable=self.reminder_var,
                                           bg=self.dark_secondary, fg=self.text_color,
                                           selectcolor=self.dark_accent,
                                           activebackground=self.dark_secondary,
                                           activeforeground=self.text_color)
        self.reminder_check.pack(side="left", padx=(80, 0))
        
        button_frame = tk.Frame(input_frame, bg=self.dark_secondary)
        button_frame.pack(fill="x", pady=(15, 5))
        
        self.add_button = tk.Button(button_frame, text="Add Task", command=self.add_task,
                                  bg=self.accent_blue, fg="white", width=10, font=self.button_font,
                                  activebackground=self.accent_blue, activeforeground="white",
                                  relief=tk.FLAT, bd=0, padx=10, pady=5)
        self.add_button.pack(side="left", padx=5)
        
        self.update_button = tk.Button(button_frame, text="Update", command=self.update_task,
                                     bg=self.dark_accent, fg=self.text_color, width=10, font=self.button_font,
                                     activebackground=self.accent_blue, activeforeground="white",
                                     relief=tk.FLAT, bd=0, padx=10, pady=5, state="disabled")
        self.update_button.pack(side="left", padx=5)
        
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_task,
                                     bg=self.dark_accent, fg=self.text_color, width=10, font=self.button_font,
                                     activebackground=self.accent_red, activeforeground="white",
                                     relief=tk.FLAT, bd=0, padx=10, pady=5, state="disabled")
        self.delete_button.pack(side="left", padx=5)
        
        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_entries,
                                    bg=self.dark_accent, fg=self.text_color, width=10, font=self.button_font,
                                    activebackground=self.dark_secondary, activeforeground=self.text_color,
                                    relief=tk.FLAT, bd=0, padx=10, pady=5)
        self.clear_button.pack(side="left", padx=5)
        
        list_frame = tk.Frame(main_frame, bg=self.dark_bg, bd=0, relief=tk.GROOVE)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        list_label = tk.Label(list_frame, text="Your Tasks", font=self.label_font, 
                             bg=self.dark_bg, fg=self.text_color)
        list_label.pack(anchor="w", pady=(0, 5))
        
        tree_frame = tk.Frame(list_frame, bg=self.accent_blue, bd=1)
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Title", "Description", "Deadline", "Status", "Reminder")
        self.task_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")
        
        for col in columns:
            self.task_tree.heading(col, text=col)
            if col == "ID":
                self.task_tree.column(col, width=40, anchor="center")
            elif col == "Title":
                self.task_tree.column(col, width=150, anchor="w")
            elif col == "Description":
                self.task_tree.column(col, width=250, anchor="w")
            elif col == "Deadline":
                self.task_tree.column(col, width=100, anchor="center")
            elif col == "Status":
                self.task_tree.column(col, width=100, anchor="center")
            elif col == "Reminder":
                self.task_tree.column(col, width=80, anchor="center")
        
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.task_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        self.task_tree.pack(side="left", fill="both", expand=True)
        
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.task_tree.bind("<Double-1>", self.on_task_double_click)
        
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.dark_secondary, fg=self.text_color,
                                   activebackground=self.accent_blue, activeforeground='white')
        self.context_menu.add_command(label="Mark as Completed", command=lambda: self.change_status("Completed"))
        self.context_menu.add_command(label="Mark as In Progress", command=lambda: self.change_status("In Progress"))
        self.context_menu.add_command(label="Mark as Pending", command=lambda: self.change_status("Pending"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Reminder", command=self.toggle_reminder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit Task", command=self.edit_selected_task)
        self.context_menu.add_command(label="Delete Task", command=self.delete_task)
        
        self.task_tree.bind("<Button-3>", self.show_context_menu)
        
        self.status_text = tk.StringVar()
        self.status_text.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_text, bd=1, relief=tk.SUNKEN, 
                             bg=self.dark_secondary, fg=self.text_color, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.selected_task_id = None
    
    # function for loading the tasks from the database
    def load_tasks(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        try:
            self.cursor.execute("SELECT id, title, description, deadline, status, reminder FROM tasks")
            tasks = self.cursor.fetchall()
            
            for task in tasks:
                task_list = list(task)
                task_list[5] = "Yes" if task[5] == 1 else "No"
                
                if task[4] == "Completed":
                    tag = "completed"
                elif task[4] == "In Progress":
                    tag = "inprogress"
                else:
                    tag = "pending"
                    
                today = datetime.date.today().strftime("%Y-%m-%d")
                if task[3] == today and task[4] != "Completed":
                    tag = "duetoday"
                elif task[3] < today and task[4] != "Completed":
                    tag = "overdue"
                
                self.task_tree.insert("", "end", values=task_list, tags=(tag,))
            
            self.task_tree.tag_configure("completed", foreground=self.accent_green)
            self.task_tree.tag_configure("inprogress", foreground="#FFA500")
            self.task_tree.tag_configure("pending", foreground=self.text_color)
            self.task_tree.tag_configure("duetoday", foreground="#FFFF00")
            self.task_tree.tag_configure("overdue", foreground=self.accent_red)
            
            self.status_text.set(f"Loaded {len(tasks)} tasks")
            
            self.check_due_tasks()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading tasks: {e}")
    
    # function for adding a task to the database
    def add_task(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        deadline = self.deadline_entry.get()
        status = self.status_var.get()
        reminder = 1 if self.reminder_var.get() else 0
        
        if not title:
            messagebox.showwarning("Input Error", "Title cannot be empty")
            return
        
        try:
            self.cursor.execute(
                "INSERT INTO tasks (title, description, deadline, status, reminder) VALUES (?, ?, ?, ?, ?)",
                (title, description, deadline, status, reminder)
            )
            self.conn.commit()
            
            self.clear_entries()
            self.load_tasks()
            
            self.status_text.set("Task added successfully")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding task: {e}")

    # function for updating a task in the database  
    def update_task(self):
        if not self.selected_task_id:
            return
        
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        deadline = self.deadline_entry.get()
        status = self.status_var.get()
        reminder = 1 if self.reminder_var.get() else 0
        
        if not title:
            messagebox.showwarning("Input Error", "Title cannot be empty")
            return
        
        try:
            self.cursor.execute(
                "UPDATE tasks SET title = ?, description = ?, deadline = ?, status = ?, reminder = ? WHERE id = ?",
                (title, description, deadline, status, reminder, self.selected_task_id)
            )
            self.conn.commit()
            
            self.clear_entries()
            self.load_tasks()
            
            self.status_text.set("Task updated successfully")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating task: {e}")

    # function for deleting a task from the database 
    def delete_task(self):
        if not self.selected_task_id:
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this task?")
        if not confirm:
            return
        
        try:
            self.cursor.execute("DELETE FROM tasks WHERE id = ?", (self.selected_task_id,))
            self.conn.commit()
            
            self.clear_entries()
            self.load_tasks()
            
            self.status_text.set("Task deleted successfully")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error deleting task: {e}")
    
    # function for selecting a task from the list of tasks
    def on_task_select(self, event):
        selected_items = self.task_tree.selection()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.task_tree.item(item, "values")
        
        self.update_button.config(state="normal")
        self.delete_button.config(state="normal")
        
        self.update_button.config(bg=self.accent_blue)
        self.delete_button.config(bg=self.accent_red)
        
        self.selected_task_id = values[0]
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, values[1])
        
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, values[2])
        
        try:
            year, month, day = map(int, values[3].split('-'))
            self.deadline_entry.set_date(datetime.date(year, month, day))
        except (ValueError, IndexError):
            self.deadline_entry.set_date(datetime.date.today())
        
        self.status_var.set(values[4])
        
        self.reminder_var.set(values[5] == "Yes")

    # function for double clicking on a task

    def on_task_double_click(self, event):
        self.edit_selected_task()

    # function for editing a selected task    

    def edit_selected_task(self):
        if not self.task_tree.selection():
            return
            
        self.title_entry.focus_set()
        self.status_text.set("Edit task and click Update when done")
    
    # function for clearing the entries in the input fields

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.deadline_entry.set_date(datetime.date.today())
        self.status_var.set("Pending")
        self.reminder_var.set(False)
        
        self.update_button.config(state="disabled", bg=self.dark_accent)
        self.delete_button.config(state="disabled", bg=self.dark_accent)
        
        self.selected_task_id = None
        
        for item in self.task_tree.selection():
            self.task_tree.selection_remove(item)
    
    # function for showing the context menu
    def show_context_menu(self, event):
        item = self.task_tree.identify_row(event.y)
        if item:
            self.task_tree.selection_set(item)
            self.on_task_select(None)
            self.context_menu.post(event.x_root, event.y_root)
    
    # function for changing the status of a task
    def change_status(self, status):
        if not self.selected_task_id:
            return
        
        try:
            self.cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, self.selected_task_id))
            self.conn.commit()
            
            self.status_var.set(status)
            
            self.load_tasks()
            
            self.status_text.set(f"Task marked as {status}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating task status: {e}")
    
    # function for toggling the reminder of a task
    def toggle_reminder(self):
        if not self.selected_task_id:
            return
            
        try:
            self.cursor.execute("SELECT reminder FROM tasks WHERE id = ?", (self.selected_task_id,))
            current = self.cursor.fetchone()[0]
            
            new_reminder = 0 if current == 1 else 1
            
            self.cursor.execute("UPDATE tasks SET reminder = ? WHERE id = ?", (new_reminder, self.selected_task_id))
            self.conn.commit()
            
            self.reminder_var.set(new_reminder == 1)
            
            self.load_tasks()
            
            status = "enabled" if new_reminder == 1 else "disabled"
            self.status_text.set(f"Reminder {status}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error toggling reminder: {e}")
    
    # function for checking the due tasks
    def check_due_tasks(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        try:
            self.cursor.execute("SELECT title FROM tasks WHERE deadline = ? AND status != 'Completed'", (today,))
            due_tasks = self.cursor.fetchall()
            
            if due_tasks:
                tasks_str = "\n".join([f"• {task[0]}" for task in due_tasks])
                messagebox.showinfo("Tasks Due Today", f"You have {len(due_tasks)} tasks due today:\n\n{tasks_str}")
        except sqlite3.Error as e:
            print(f"Error checking due tasks: {e}")
    
    # function for processing the reminder queue
    def process_reminder_queue(self):
        try:
            while not self.reminder_queue.empty():
                task_title = self.reminder_queue.get_nowait()
                self.show_reminder(task_title)
        except queue.Empty:
            pass
        
        self.root.after(1000, self.process_reminder_queue)
    
    # function for checking the reminders
    def reminder_checker(self):
        while not self.stop_thread:
            try:
                with sqlite3.connect("to-do.db") as conn:
                    cursor = conn.cursor()
                    
                    today = datetime.date.today().strftime("%Y-%m-%d")
                    cursor.execute(
                        "SELECT id, title FROM tasks WHERE reminder = 1 AND status != 'Completed' AND deadline = ?",
                        (today,)
                    )
                    tasks = cursor.fetchall()
                    
                    for task in tasks:
                        self.reminder_queue.put(task[1])
            except Exception as e:
                print(f"Error in reminder checker: {e}")
                
            for _ in range(360):
                if self.stop_thread:
                    break
                time.sleep(10)
    
    # function for showing the reminder
    def show_reminder(self, task_title):
        reminder_win = tk.Toplevel(self.root)
        reminder_win.title("Task Reminder")
        reminder_win.configure(bg=self.dark_secondary)
        reminder_win.geometry("350x200")
        reminder_win.resizable(False, False)
        reminder_win.lift()
        reminder_win.focus_force()
        
        reminder_win.attributes("-topmost", True)
        
        reminder_frame = tk.Frame(reminder_win, bg=self.dark_secondary, bd=2, relief=tk.GROOVE,
                                padx=20, pady=20)
        reminder_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(reminder_frame, text="⏰ Reminder", font=self.title_font,
                             bg=self.dark_secondary, fg=self.accent_blue)
        title_label.pack(pady=(0, 10))
        
        task_text = f"Task due today:\n\n{task_title}"
        task_label = tk.Label(reminder_frame, text=task_text, wraplength=300,
                            bg=self.dark_secondary, fg=self.text_color, justify="center")
        task_label.pack(pady=10)
        
        close_btn = tk.Button(reminder_frame, text="Dismiss", command=reminder_win.destroy,
                            bg=self.accent_blue, fg="white", relief=tk.FLAT, bd=0,
                            activebackground=self.dark_accent, activeforeground="white",
                            padx=20, pady=5)
        close_btn.pack(pady=10)

    # the main script for running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()