import tkinter as tk
from tkinter import scrolledtext


class ScannerWindow:
    def __init__(self, title="Virus Scanner"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("650x420")
        self.root.configure(bg="#1e1e1e")

        self._input_var = tk.StringVar()
        self._waiting_for_input = False

        self.input_frame = tk.Frame(self.root, bg="#1e1e1e", pady=10, padx=10)
        self.input_frame.pack(fill=tk.X)

        self.prompt_label = tk.Label(
            self.input_frame, text="", fg="#ffffff", bg="#1e1e1e", font=("Segoe UI", 10, "bold")
        )
        self.prompt_label.pack(anchor="w")

        entry_row = tk.Frame(self.input_frame, bg="#1e1e1e")
        entry_row.pack(fill=tk.X, pady=(5, 0))

        self.entry = tk.Entry(entry_row, font=("Consolas", 11), bg="#2d2d2d", fg="#ffffff", insertbackground="white")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.entry.bind("<Return>", self._submit_input)  # מאפשר לשלוח גם בלחיצה על Enter

        self.submit_btn = tk.Button(
            entry_row,
            text="submit",
            command=self._submit_input,
            bg="#007acc",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            relief=tk.FLAT,
        )
        self.submit_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.output_area = scrolledtext.ScrolledText(
            self.root,
            state=tk.DISABLED,
            bg="#121212",
            fg="#e0e0e0",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            wrap=tk.WORD,
        )
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.output_area.tag_config("normal", foreground="#d4d4d4")
        self.output_area.tag_config("warning", foreground="#ff4d4d", font=("Consolas", 10, "bold"))

    def _submit_input(self, event=None):
        if self._waiting_for_input:
            self._waiting_for_input = False
            self._input_var.set(self.entry.get())

    def clear_output(self):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.config(state=tk.DISABLED)
        self.root.update()

    def get_input(self, prompt_text="Enter path:"):
        self.prompt_label.config(text=prompt_text)
        self.entry.delete(0, tk.END)
        self.entry.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        self.entry.focus()

        self._waiting_for_input = True
        self.root.wait_variable(self._input_var)  
        user_value = self._input_var.get()

        self.entry.delete(0, tk.END)
        self.entry.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)
        self.prompt_label.config(text="")
        self.clear_output()

        return user_value

    def print_msg(self, text, is_warning=False):
        self.output_area.config(state=tk.NORMAL)
        if is_warning:
            self.output_area.insert(tk.END, f"⚠️ {text}\n", "warning")
        else:
            self.output_area.insert(tk.END, f"{text}\n", "normal")

        self.output_area.see(tk.END)  
        self.output_area.config(state=tk.DISABLED)
        self.root.update()  

if __name__ == "__main__":
    app = ScannerWindow("Antivirus Scanner")

    folder_path = app.get_input("Enter the directory path to scan:")

    app.print_msg(f"Scanning directory: {folder_path}")
    app.print_msg("C:\\test\\clean.txt is not virus")
    app.print_msg("VIRUS DETECTED!!! Filepath: C:\\test\\eicar.txt", is_warning=True)
    app.print_msg("Scan finished.")

    app.root.mainloop()