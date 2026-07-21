import tkinter as tk
from tkinter import filedialog, simpledialog, colorchooser, ttk

# ---------------- MAIN WINDOW ----------------
window = tk.Tk()
window.title("My Notepad")
window.geometry("1000x700")

dark_mode = False
current_files = {}

# ---------------- STATUS BAR ----------------
status_bar = tk.Label(window, text="Line 1, Column 1", anchor="w")
status_bar.pack(side="bottom", fill="x")

# ---------------- NOTEBOOK ----------------
notebook = ttk.Notebook(window)
notebook.pack(expand=True, fill="both")


# ---------------- GET CURRENT TEXT AREA ----------------
def get_text_area():
    current_tab = notebook.select()
    frame = notebook.nametowidget(current_tab)
    return frame.winfo_children()[1]


# ---------------- STATUS UPDATE ----------------
def update_status(event=None):
    try:
        text = get_text_area()
        row, col = text.index(tk.INSERT).split(".")
        status_bar.config(text=f"Line {row}, Column {col}")
    except:
        pass


# ---------------- LINE NUMBERS ----------------
def update_line_numbers(text_area, line_numbers):
    line_numbers.config(state="normal")
    line_numbers.delete(1.0, tk.END)

    lines = text_area.get("1.0", tk.END).count("\n")
    for i in range(1, lines + 1):
        line_numbers.insert(tk.END, f"{i}\n")

    line_numbers.config(state="disabled")


# ---------------- CREATE TAB ----------------
def create_tab(title="Untitled"):
    frame = tk.Frame(notebook)

    line_numbers = tk.Text(
        frame,
        width=4,
        padx=5,
        takefocus=0,
        border=0,
        bg="lightgray",
        state="disabled"
    )
    line_numbers.pack(side="left", fill="y")

    text_area = tk.Text(
        frame,
        font=("Arial", 14),
        wrap="word",
        undo=True
    )
    text_area.pack(expand=True, fill="both", side="left")

    notebook.add(frame, text=title)
    notebook.select(frame)

    current_files[text_area] = None

    text_area.bind(
        "<KeyRelease>",
        lambda e: update_line_numbers(text_area, line_numbers)
    )

    text_area.bind("<KeyRelease>", update_status)
    text_area.bind("<ButtonRelease>", update_status)

    update_line_numbers(text_area, line_numbers)

    return text_area


# Create first tab
create_tab()


# ---------------- FILE FUNCTIONS ----------------
def new_file():
    create_tab()


def open_file():
    file = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt")]
    )

    if file:
        text = create_tab(file.split("/")[-1])

        with open(file, "r") as f:
            text.insert(tk.END, f.read())

        current_files[text] = file


def save_as():
    text = get_text_area()

    file = filedialog.asksaveasfilename(
        defaultextension=".txt"
    )

    if file:
        with open(file, "w") as f:
            f.write(text.get("1.0", tk.END))

        current_files[text] = file
        notebook.tab(notebook.select(), text=file.split("/")[-1])


def save_file():
    text = get_text_area()
    file = current_files[text]

    if file is None:
        save_as()
    else:
        with open(file, "w") as f:
            f.write(text.get("1.0", tk.END))


# ---------------- EDIT FUNCTIONS ----------------
def undo():
    get_text_area().edit_undo()


def redo():
    get_text_area().edit_redo()


def make_bold():
    get_text_area().config(font=("Arial", 14, "bold"))


def make_italic():
    get_text_area().config(font=("Arial", 14, "italic"))


def change_font_size():
    size = simpledialog.askinteger(
        "Font Size",
        "Enter font size:"
    )

    if size:
        get_text_area().config(font=("Arial", size))


def change_text_color():
    color = colorchooser.askcolor()[1]

    if color:
        get_text_area().config(fg=color)


def toggle_dark_mode():
    global dark_mode

    text = get_text_area()

    if dark_mode:
        text.config(bg="white", fg="black")
        dark_mode = False
    else:
        text.config(bg="#1e1e1e", fg="white")
        dark_mode = True


# ---------------- SEARCH ----------------
def search_text():
    text = get_text_area()
    text.tag_remove("highlight", "1.0", tk.END)

    word = simpledialog.askstring(
        "Search",
        "Enter word:"
    )

    if word:
        start = "1.0"

        while True:
            start = text.search(word, start, stopindex=tk.END)

            if not start:
                break

            end = f"{start}+{len(word)}c"
            text.tag_add("highlight", start, end)
            start = end

        text.tag_config("highlight", background="yellow")


# ---------------- WORD COUNT ----------------
def word_count():
    text = get_text_area()
    words = text.get("1.0", tk.END).split()

    status_bar.config(
        text=f"Word Count: {len(words)}"
    )


# ---------------- AUTO SAVE ----------------
def auto_save():
    for text, file in current_files.items():
        if file:
            with open(file, "w") as f:
                f.write(text.get("1.0", tk.END))

    window.after(5000, auto_save)


# ---------------- MENU ----------------
menu_bar = tk.Menu(window)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.destroy)

# Edit menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Undo", command=undo)
edit_menu.add_command(label="Redo", command=redo)
edit_menu.add_separator()
edit_menu.add_command(label="Bold", command=make_bold)
edit_menu.add_command(label="Italic", command=make_italic)
edit_menu.add_command(label="Font Size", command=change_font_size)
edit_menu.add_command(label="Text Color", command=change_text_color)
edit_menu.add_command(label="Dark Mode", command=toggle_dark_mode)

# Tools menu
tools_menu = tk.Menu(menu_bar, tearoff=0)
tools_menu.add_command(label="Search", command=search_text)
tools_menu.add_command(label="Word Count", command=word_count)

menu_bar.add_cascade(label="File", menu=file_menu)
menu_bar.add_cascade(label="Edit", menu=edit_menu)
menu_bar.add_cascade(label="Tools", menu=tools_menu)

window.config(menu=menu_bar)

# Start auto-save
auto_save()

# Run app
window.mainloop()