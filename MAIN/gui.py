import sys
import tkinter as tk
from tkinter import scrolledtext
from maintest import process  # Import the process function from maintest.py


def submit_input(event=None):  # Add event parameter for Enter key binding
    input_text = input_entry.get()
    if input_text.lower() == "quit":
        root.quit()
        return

    try:
        # Append input to the chat history
        scrolled_text.insert(tk.END, f"You: {input_text}\n")

        # Redirect process output to GUI
        class RedirectOutput:
            def __init__(self, widget):
                self.widget = widget

            def write(self, string):
                self.widget.insert(tk.END, string)

            def flush(self):
                pass  # No-op for compatibility

        sys.stdout = RedirectOutput(scrolled_text)
        sys.stderr = RedirectOutput(scrolled_text)

        # Call the process function and capture output
        process(input_text)
    except Exception as e:
        scrolled_text.insert(tk.END, f"Error: {e}\n")

    finally:
        input_entry.delete(0, tk.END)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Add a separator for readability
    scrolled_text.insert(tk.END, "\n")
    scrolled_text.yview(tk.END)  # Auto-scroll to the latest entry


# Create GUI window
root = tk.Tk()
root.title("Family Relationship Manager")

# ScrolledText for displaying results (chat history)
scrolled_text = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD)
scrolled_text.pack(pady=10)

# Input label and entry
input_frame = tk.Frame(root)  # Frame to hold input and submit button
input_frame.pack(pady=5)

input_entry = tk.Entry(input_frame, width=50)
input_entry.pack(side=tk.LEFT, padx=5)

# Submit button
submit_button = tk.Button(input_frame, text="Submit", command=submit_input)
submit_button.pack(side=tk.RIGHT)

# Bind Enter key to submit input
input_entry.bind("<Return>", submit_input)

# Quit button
quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack(pady=5)

root.mainloop()
