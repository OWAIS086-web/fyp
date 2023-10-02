import tkinter
from datetime import datetime
from difflib import SequenceMatcher
from tkinter import *
import pyperclip
import wikipedia
import webbrowser, re, ModuleFile, SearchMod
from idlelib.colorizer import ColorDelegator
from idlelib.percolator import Percolator

import tk as tk
from customtkinter import *
from tkinter import messagebox, ttk, filedialog
from hashlib import md5


all_wd = ModuleFile.words

theme_get = "dark"
lang_get = "python"
fg_get = "white"
bg_get = "#1e1f22"
tc_get = "cyan"
font = "Consolas"
fontsize = 15


class Document:
    def __init__(self, tkFrame, TextWidget, FileDir=""):
        self.file_dir = FileDir
        self.file_name = "Scratch" if not FileDir else os.path.basename(FileDir)
        self.textbox = TextWidget
        self.status = md5(self.textbox.get(1.0, "end").encode("utf-8"))


class SMPadWidget(Text):
    def __init__(self, *args, **kwargs):
        self.callback = kwargs.pop("autocomplete", None)
        super().__init__(*args, **kwargs)
        self.bind("<Any-KeyRelease>", self._autocomplete)

    def _handle_tab(self, event):
        tag_ranges = self.tag_ranges("autocomplete")
        if tag_ranges:
            self.mark_set("insert", tag_ranges[1])
            self.tag_remove("sel", "1.0", "end")
            self.tag_remove("autocomplete", "1.0", "end")
            return "break"

    def _autocomplete(self, event):
        if event.char and self.callback:
            word = self.get("insert-1c wordstart", "insert-1c wordend")
            matches = self.callback(word)
            if matches:
                remainder = matches[0][len(word) :]
                insert = self.index("insert")
                self.insert(insert, remainder, ("sel", "autocomplete"))
                self.mark_set("insert", insert)


class Editor:
    def __init__(self, master):
        self.master = master
        self.master.set_appearance_mode(theme_get)
        self.master.geometry("1250x700")
        self.master.iconbitmap("icon.ico")
        self.master.title("scraping PAD")
        self.frame = Frame(self.master)
        self.frame.pack()

        self.lineNumber = CTkCanvas(
            self.master, background="#212325", width=60, highlightthickness=0
        )
        self.lineNumber.pack(side=LEFT, fill=Y, pady=25)

        self.wordCount = StringVar()
        self.wordCount.set("Word Count -> 0")

        self.init_dir = os.path.join(os.path.expanduser("~"), "Desktop")

        self.tabs = {}

        self.nb = ttk.Notebook(master)
        self.nb.bind("<Button-2>", self.close_tab)
        self.nb.bind("<B1-Motion>", self.move_tab)
        self.nb.pack(expand=10, fill="both")
        self.nb.enable_traversal()
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#1d1d1d", borderwidth=0.4)
        style.configure("TNotebook.Tab", background="black", foreground="white")
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#1d1d1d")],
            foreground=[("selected", "light blue")],
        )
        style.configure("Red.TNotebook.Tab", foreground="red")
        self.master.protocol("WM_DELETE_WINDOW", self.exit)

        menubar = Menu(self.master)

        filemenu = Menu(
            menubar, tearoff=0, background="#2c2f33", foreground="light blue"
        )

        filemenu.add_command(label="New", command=self.new_file_mo)
        filemenu.add_command(
            label="Open", command=self.open_file, accelerator="Ctrl + O"
        )
        filemenu.add_command(label="Open from Directory", command=self.open_in_dir)
        filemenu.add_command(
            label="Save", command=self.save_file, accelerator="Ctrl + S"
        )
        filemenu.add_command(
            label="Save As...", command=self.save_as, accelerator="Ctrl + S"
        )
        filemenu.add_command(
            label="Close Tab", command=self.close_tab, accelerator="Ctrl + W"
        )
        filemenu.add_command(label="Summary", command=self.summary)
        filemenu.add_command(label="Exit", command=self.exit, accelerator="Alt + F4")

        toolsmenu = Menu(
            menubar, tearoff=0, background="#2c2f33", foreground="light blue"
        )

        toolsmenu_txt = Menu(
            toolsmenu, tearoff=0, background="#2c2f33", foreground="light blue"
        )
        toolsmenu_txt.add_command(label="Plagiarism Check", command=self.plagiarism_checker)
        toolsmenu.add_cascade(label="Text Editing", menu=toolsmenu_txt)



        editmenu = Menu(
            menubar, tearoff=0, background="#2c2f33", foreground="light blue"
        )
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_command(label="Redo", command=self.cmd_redo)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.cut, accelerator="Ctrl + X")
        editmenu.add_command(label="Copy", command=self.copy, accelerator="Ctrl + C")
        editmenu.add_command(label="Paste", command=self.paste, accelerator="Ctrl + V")
        editmenu.add_command(label="Delete", command=self.delete, accelerator="Del")
        editmenu.add_command(
            label="Select All", command=self.select_all, accelerator="Ctrl + A"
        )
        editmenu.add_separator()
        editmenu.add_command(
            label="Convert Selection to UPPERCASE", command=self.to_Upper
        )
        editmenu.add_command(
            label="Convert Selection to lowercase", command=self.to_Lower
        )
        editmenu.add_separator()
        editmenu.add_command(label="Date & Time", accelerator="F5", command=self.time)
        editmenu.add_command(label="Duplicate Line", command=self.duplicate_line)
        editmenu.add_command(label="Goto Line", command=self.goto)
        editmenu.add_separator()
        editmenu.add_command(label="Find & Replace", command=self.find_replace)
        editmenu.add_separator()

        windowmenu = Menu(
            menubar, tearoff=0, background="#2c2f33", foreground="light blue"
        )
        transparency = Menu(
            windowmenu, tearoff=False, background="#2c2f33", foreground="light blue"
        )
        windowmenu.add_command(label="Always On Top", command=self.alwaysontop)

        transparency.add_command(label="5%", command=self.Transparent5)
        transparency.add_command(label="10%", command=self.Transparent10)
        transparency.add_command(label="20%", command=self.Transparent20)
        transparency.add_command(label="25%", command=self.Transparent25)
        transparency.add_command(label="30%", command=self.Transparent30)
        transparency.add_command(label="40%", command=self.Transparent40)
        transparency.add_command(label="50%", command=self.Transparent50)
        transparency.add_command(label="75%", command=self.Transparent75)
        transparency.add_command(label="Reset", command=self.resetTransparent)
        windowmenu.add_cascade(label="Transparency", menu=transparency)



        self.word_wrap = BooleanVar()
        editmenu.add_checkbutton(
            label="Word Wrap",
            onvalue=True,
            offvalue=False,
            variable=self.word_wrap,
            command=self.wrap,
        )

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Tools", menu=toolsmenu)
        menubar.add_cascade(label="Window", menu=windowmenu)
        self.master.config(menu=menubar)

        self.right_click_menu = Menu(
            self.master, tearoff=0, foreground="light blue", background="#2c2f33"
        )
        self.searchmenu = Menu(
            self.right_click_menu,
            tearoff=0,
            foreground="light blue",
            background="#2c2f33",
        )
        self.speakmenu = Menu(
            self.right_click_menu,
            tearoff=0,
            foreground="light blue",
            background="#3c3f41",
        )
        self.encodemenu = Menu(
            self.right_click_menu,
            tearoff=0,
            foreground="light blue",
            background="#2c2f33",
        )
        self.highlightmenu = Menu(
            self.right_click_menu,
            tearoff=0,
            foreground="light blue",
            background="#2c2f33",
        )

        self.calc_menu = Menu(
            self.right_click_menu,
            tearoff=0,
            foreground="light blue",
            background="#2c2f33",
        )

        self.right_click_menu.add_command(
            label="Cut                                     ",
            command=self.cut,
            accelerator="Ctrl + X",
        )
        self.right_click_menu.add_command(
            label="Copy", command=self.copy, accelerator="Ctrl + C"
        )
        self.right_click_menu.add_command(
            label="Paste", command=self.paste, accelerator="Ctrl + V"
        )
        self.right_click_menu.add_command(
            label="Delete", command=self.delete, accelerator="Del"
        )
        self.right_click_menu.add_command(
            label="Select All", command=self.select_all, accelerator="Ctrl + A"
        )
        self.right_click_menu.add_separator()

        self.calc_menu.add_command(label="Calculate", command=self.calculate)
        self.calc_menu.add_command(label="Calculate and Enter the Result", command=self.calc_enter_res)

        self.speakmenu.add_command(label="Full File       ", command=self.full_speak)
        self.speakmenu.add_command(label="Selection", command=self.right_speak)

        self.right_click_menu.add_cascade(label="Read Aloud", menu=self.speakmenu)

        self.right_click_menu.add_cascade(label="Calculate", menu=self.calc_menu)

        self.right_click_menu.add_command(label="Refractor", command=self.refractoring)
        self.right_click_menu.add_separator()
        self.searchmenu.add_command(label="SM-Pedia", command=self.wiki)

        self.searchmenu.add_command(label="SM-scrape", command=self.SMscrape)
        self.searchmenu.add_command(label="StackOverflow", command=self.search_stack)
        self.searchmenu.add_command(label="youtube", command=self.yt_search)
        self.searchmenu.add_command(label="Github", command=self.search_github)
        self.searchmenu.add_command(label="google", command=self.search_google)
        # self.searchmenu.add_command(label="AI", command=self.chat_gpt_search)
        self.searchmenu.add_command(label="bing", command=self.bing)
        self.encodemenu.add_command(label="Encode", command=self.encypt)
        self.encodemenu.add_command(label="Decode", command=self.decode)
        self.highlightmenu.add_command(label="Highlight", command=self.highlight_note)
        self.highlightmenu.add_command(
            label="Remove Highlight", command=self.clear_highlight
        )

        self.right_click_menu.add_cascade(label="Highlighting", menu=self.highlightmenu)
        self.right_click_menu.add_cascade(label="Search In", menu=self.searchmenu)
        self.right_click_menu.add_cascade(label="Encryption", menu=self.encodemenu)

        self.tab_right_click_menu = Menu(self.master, tearoff=0)
        self.tab_right_click_menu.add_command(label="New Tab", command=self.new_file)
        self.tab_right_click_menu.add_command(label="Close Tab", command=self.close_tab)
        self.nb.bind("<Button-3>", self.right_click_tab)

        first_tab = ttk.Frame(self.nb)
        self.tabs[first_tab] = Document(first_tab, self.create_text_widget(first_tab))
        self.nb.add(first_tab, text="Scratch")

    def get_matches(self, word):
        wordd = self.tabs[self.get_tab()].textbox.get("1.0", "end-1c").split()
        words = all_wd + list(wordd)
        matches = [x for x in words if x.startswith(word)]
        return matches

    def create_text_widget(self, frame):
        textbox = SMPadWidget(
            frame,
            autocomplete=self.get_matches,
            relief="sunken",
            borderwidth=0,
            wrap="none",
            background=bg_get,
            foreground=fg_get,
            insertbackground=tc_get,
            font=(font, fontsize),
        )
        yscrollbar = CTkScrollbar(frame, command=textbox.yview)
        yscrollbar.pack(side="right", fill="y")

        def auto_indent(event):
            text_ai = event.widget
            line = text_ai.get("insert linestart", "insert")
            match = re.match(r"^(\s+)", line)
            whitespace = match.group(0) if match else ""
            text_ai.insert("insert", f"\n{whitespace}")
            return "break"

        def tab_pressed(event: Event) -> str:
            self.tabs[self.get_tab()].textbox.insert("insert", " " * 4)
            return "break"

        textbox.bind("<Return>", auto_indent)
        textbox.bind("<Tab>", tab_pressed)

        xscrollbar = CTkScrollbar(
            frame, command=textbox.xview, orientation="horizontal"
        )
        xscrollbar.pack(side="bottom", fill="x")
        textbox.config(yscrollcommand=yscrollbar.set, undo=True, autoseparators=True)
        textbox.config(xscrollcommand=xscrollbar.set)

        textbox.bind("<Control-s>", self.save_file)
        textbox.bind("<Control-s>", self.save_file)
        textbox.bind("<Control-o>", self.open_file)
        textbox.bind("<Control-O>", self.open_file)
        textbox.bind("<Control-n>", self.new_file)
        textbox.bind("<Control-N>", self.new_file)
        textbox.bind("<Control-w>", self.close_tab)
        textbox.bind("<Control-W>", self.close_tab)
        textbox.bind("<Button-3>", self.right_click)
        textbox.bind("<Control-F>", self.finder)
        textbox.bind_all("<Return>", self.redraw)
        textbox.bind_all("<BackSpace>", self.redraw)
        textbox.bind_all("<KeyPress>", self.redraw)
        textbox.bind_all("<KeyRelease>", self.redraw)
        textbox.bind_all("<Key>", self.redraw)
        textbox.bind_all("<Button-4>", self.redraw)
        textbox.bind_all("<Button-5>", self.redraw)
        textbox.bind_all("<Configure>", self.redraw)
        textbox.bind_all("<Motion>", self.redraw)
        textbox.bind("<Control-f>", self.finder)

        cdg = ColorDelegator()
        cdg.tagdefs["COMMENT"] = {"foreground": "grey", "background": bg_get}
        cdg.tagdefs["KEYWORD"] = {"foreground": "orange", "background": bg_get}
        cdg.tagdefs["BUILTIN"] = {"foreground": "gold", "background": bg_get}
        cdg.tagdefs["STRING"] = {"foreground": "#95e7ad", "background": bg_get}
        cdg.tagdefs["DEFINITION"] = {"foreground": "#bb6733", "background": bg_get}
        cdg.tagdefs["BRACKETS"] = {"foreground": "#007F7F", "background": bg_get}
        Percolator(textbox).insertfilter(cdg)

        textbox.pack(fill="both", expand=True)
        return textbox

    def open_file(self, *args):
        ModuleFile.open_file(self, self, Document=Document)

    def save_as(self):
        ModuleFile.save_as(self)

    def goto(self):
        ModuleFile.goto(self)

    def save_file(self, *args):
        ModuleFile.save_file(self, self)

    def open_in_dir(self):
        ModuleFile.open_in_dir(self)

    def copy(self):
        try:
            sel = self.tabs[self.get_tab()].textbox.get(SEL_FIRST, SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        except TclError:
            pass

    def delete(self):
        try:
            self.tabs[self.get_tab()].textbox.delete(SEL_FIRST, SEL_LAST)
        except TclError:
            pass

    def cut(self):
        try:
            sel = self.tabs[self.get_tab()].textbox.get(SEL_FIRST, SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.tabs[self.get_tab()].textbox.delete(SEL_FIRST, SEL_LAST)
        except TclError:
            pass

    def finder(self, e):
        finde = CTkToplevel()
        finde.title("Find")
        textfindedd = CTkEntry(
            finde,
            width=200,
            text_color="light blue",
            text_font=("Arial", 12),
            height=32,
        )
        textfindedd.pack()
        textfindedd.focus_set()
        finde.attributes("-topmost", 1)

        def finded(v):
            ModuleFile.find(self, textfindedd)

        textfindedd.bind("<KeyPress>", finded)
        textfindedd.bind("KeyRelease", finded)
        textfindedd.bind("<FocusIn>", finded)
        textfindedd.bind("<MouseWheel>", finded)

    def encypt(self):
        ModuleFile.encypt(self.tabs[self.get_tab()].textbox)

    def clear_highlight(self):
        st_ind = self.tabs[self.get_tab()].textbox.index("sel.first")
        end_ind = self.tabs[self.get_tab()].textbox.index("sel.last")
        self.tabs[self.get_tab()].textbox.tag_remove("start", st_ind, end_ind)



    def decode(self):
        ModuleFile.decode(self.tabs[self.get_tab()].textbox)

    def redraw(self, event=NONE):
        self.update_count(event)
        self.lineNumber.delete("all")
        self.objectIds = []
        si = self.tabs[self.get_tab()].textbox.index("@0,0")
        while True:
            dline = self.tabs[self.get_tab()].textbox.dlineinfo(si)
            if dline is None:
                break
            y = dline[1]
            liNum = str(si).split(".")[0]
            self.lineNumber.create_text(
                2, y, anchor="nw", text=liNum, fill="#d3d3d3", font=("Consolas", 12)
            )
            si = self.tabs[self.get_tab()].textbox.index(f"{si}+1line")

    def update_count(self, event):
        count = self.tabs[self.get_tab()].textbox.get("1.0", END)
        self.wordCount.set(f"Word Count -> {len(count) - 1}")


    def wrap(self):
        if self.word_wrap.get():
            for index in self.tabs:
                self.tabs[index].textbox.config(wrap="word")
        else:
            for index in self.tabs:
                self.tabs[index].textbox.config(wrap="none")

    def find_replace(self):
        ModuleFile.find_replace(self)

    def to_Upper(self):
        ModuleFile.to_Upper(self)

    def to_Lower(self):
        ModuleFile.to_Lower(self)

    def refractoring(self):
        ModuleFile.refractor(self.tabs[self.get_tab()].textbox)

    def highlight_note(self):
        ModuleFile.highlightText(self.tabs[self.get_tab()].textbox)

    def summary(self):
        ModuleFile.Summary(self.tabs[self.get_tab()].textbox)

    def new_filed(self, *args, filename):
        new_tab = ttk.Frame(self.nb)
        self.tabs[new_tab] = Document(new_tab, self.create_text_widget(new_tab))
        self.tabs[new_tab].textbox.config(
            wrap="word" if self.word_wrap.get() else "none"
        )
        self.nb.add(new_tab, text=filename)
        self.nb.select(new_tab)

    def paste(self):
        try:
            self.tabs[self.get_tab()].textbox.insert(
                INSERT, self.master.clipboard_get()
            )
        except TclError:
            pass

    def new_file(self, e):
        file_ui = CTkToplevel()
        file_ui.title("New"), file_ui.geometry("250x150")
        CTkLabel(file_ui, text="Filename:").pack()

        file_name = CTkEntry(file_ui, width=200, text_color="light blue")
        file_name.pack(pady=5)

        type_selection = CTkComboBox(master=file_ui,
                                     values=["Python File", "C++ File", "HTML File", "File"])

        type_selection.set("File")
        type_selection.pack(pady=15)

        def apply(e):
            type_val = type_selection.get()
            filename = file_name.get()

            if type_val == "Python File":
                filename = filename + ".py"
                self.new_filed(filename = filename)
            elif type_val == "C++ File":
                filename = filename + ".cpp"
                self.new_filed(filename=filename)
            elif type_val == "File":
                filename = filename
                self.new_filed(filename=filename)
            elif type_val == "HTML":
                filename = filename + ".html"
                self.new_filed(filename=filename)
            file_ui.destroy()

        CTkButton(file_ui, text="Create", command=apply).pack(side=BOTTOM)

        file_ui.bind("<Return>", apply)

    def new_file_mo(self):
        ModuleFile.new_file(self)

    def duplicate_line(self):
        line = self.tabs[self.get_tab()].textbox.index("insert")
        line_start = line + " linestart"
        line_end = line + " lineend"
        line_contents = self.tabs[self.get_tab()].textbox.get(line_start, line_end)
        line_contents = "\n" + line_contents
        self.tabs[self.get_tab()].textbox.insert(line, line_contents)

    def Transparent25(self):
        self.master.attributes("-alpha", 0.75)

    def Transparent20(self):
        self.master.attributes("-alpha", 0.8)

    def Transparent5(self):
        self.master.attributes("-alpha", 0.95)

    def Transparent10(self):
        self.master.attributes("-alpha", 0.9)

    def Transparent30(self):
        self.master.attributes("-alpha", 0.7)

    def Transparent40(self):
        self.master.attributes("-alpha", 0.6)

    def Transparent50(self):
        self.master.attributes("-alpha", 0.5)

    def calculate(self):
        ModuleFile.calculate(self)

    def calc_enter_res(self):
        ModuleFile.calc_enter_res(self)

    def Transparent60(self):
        self.master.attributes("-alpha", 0.4)

    def Transparent75(self):
        self.master.attributes("-alpha", 0.25)

    def resetTransparent(self):
        self.master.attributes("-alpha", 1)

    def search_stack(self):
        SearchMod.search_stack(self.tabs[self.get_tab()].textbox)

    def yt_search(self):
        SearchMod.yt_search(self.tabs[self.get_tab()].textbox)

    def search_github(self):
        SearchMod.search_github(self.tabs[self.get_tab()].textbox)
    def bing(self):
        SearchMod.bing(self.tabs[self.get_tab()].textbox)



    def search_google(self):
        SearchMod.search_google(self.tabs[self.get_tab()].textbox)



    def right_speak(self):
        notepad_selection = self.tabs[self.get_tab()].textbox.selection_get()
        ModuleFile.rightSpeak(notepad_selection)

    def full_speak(self):
        full_note = self.tabs[self.get_tab()].textbox.get(0.0, END)
        ModuleFile.rightSpeak(full_note)

    def select_all(self, *args):
        curr_tab = self.get_tab()
        self.tabs[curr_tab].textbox.tag_add(SEL, "1.0", END)
        self.tabs[curr_tab].textbox.mark_set(INSERT, END)
        self.tabs[curr_tab].textbox.see(INSERT)

    def time(self):
        d = datetime.now()
        self.tabs[self.get_tab()].textbox.insert("end", d)

    def undo(self):
        self.tabs[self.get_tab()].textbox.edit_undo()

    def wiki(self):
        ModuleFile.wiki(self.tabs[self.get_tab()].textbox)

    def AI(self):
         ModuleFile.AI(self.tabs[self.get_tab()].textbox)

    def SMscrape(self):
        ModuleFile.SMscrape(self.tabs[self.get_tab()].textbox)

    def cmd_redo(self):
        self.tabs[self.get_tab()].textbox.edit_redo()

    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)


    def close_tab(self, event=None):
        if event is None or event.type == str(2):
            selected_tab = self.get_tab()
        else:
            try:
                index = event.widget.index("@%d,%d" % (event.x, event.y))
                selected_tab = self.nb._nametowidget(self.nb.tabs()[index])
            except TclError:
                return
        if self.save_changes():
            self.nb.forget(selected_tab)
            self.tabs.pop(selected_tab)
        if self.nb.index("end") == 0:
            self.master.destroy()

    def exit(self):
        if self.save_changes():
            self.master.destroy()
        else:
            return

    def alwaysontop(self):
        self.master.attributes("-topmost", 1)



    def save_changes(self):
        curr_tab = self.get_tab()
        file_dir = self.tabs[curr_tab].file_dir
        if (
            md5(self.tabs[curr_tab].textbox.get(1.0, "end").encode("utf-8")).digest()
            != self.tabs[curr_tab].status.digest()
        ):
            m = messagebox.askyesnocancel(
                "scraping PAD",
                "Hold up, mann! Do you want to save your masterpiece "
                + ("Scratch" if not file_dir else file_dir)
                + " before close the scraping PAD ?",
            )
            if m is None:
                return False
            elif m is True:
                self.save_file()
            else:
                pass
        return True

    def get_tab(self):
        return self.nb._nametowidget(self.nb.select())

    def move_tab(self, event):
        if self.nb.index("end") > 1:
            y = self.get_tab().winfo_y() - 5
            try:
                self.nb.insert(
                    event.widget.index("@%d,%d" % (event.x, y)), self.nb.select()
                )
            except TclError:
                return

            def open_file(self, *args):
                file_dir = (tkinter
                            .filedialog
                            .askopenfilename(initialdir=self.init_dir, title="Select file", ))
                if file_dir:
                    try:
                        file = open(file_dir)
                        new_tab = ttk.Frame(self.nb, borderwidth=0)
                        self.tabs[new_tab] = Document(new_tab, self.create_text_widget(new_tab), file_dir)
                        self.nb.add(new_tab, text=os.path.basename(file_dir))
                        self.nb.select(new_tab)
                        self.tabs[new_tab].textbox.insert('end', file.read())
                        self.tabs[new_tab].status = md5(self.tabs[new_tab].textbox.get(1.0, 'end').encode('utf-8'))
                    except FileNotFoundError:
                        return

# This is the function which open file form diorectory
    def plagiarism_checker(self):
        filename = filedialog.askopenfilename(
            title="Select any Text File to check for Plagiarism",
            filetypes=[("Text Files", ".txt"), ("Python Files", ".py")
        ])

# the open process is end now the check or compaire process is start


        from tkinter import END
        get_cur_note_data = self.tabs[self.get_tab()].textbox.get(0.0, END)

        txt_file = open(filename, "r+")
        txt_file = txt_file.read()

        ab = SequenceMatcher(None, txt_file,get_cur_note_data)
        ab = ab.ratio()

        result = int(ab*100)
        result = str(result) + "%"

        messagebox.showinfo("Plagiarism Ratio", result)

#the process of plagrism is complete and the hole function end after check and give report in massage box


# this is the process of splash screen we load and png file which is show in start of over program
#we set the screen size time and geometry

splash_root = Tk()
splash_image = PhotoImage(file="splash.png")
splash_root.overrideredirect(True)

window_height = 350
window_width = 700

screen_width = splash_root.winfo_screenwidth()
screen_height = splash_root.winfo_screenheight()

x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))

splash_root.geometry(
    "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)
)

splash_label = Label(splash_root, image=splash_image)
splash_label.pack()

# the process of splash screen end


def main():
    splash_root.destroy()
    root = CTk()
    app = Editor(root)
    root.mainloop()


if __name__ == "__main__":
    splash_root.after(1000, main)

splash_root.mainloop()
