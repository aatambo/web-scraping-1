import tkinter as tk
from tkinter import filedialog, font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from collections import Counter
import bs4
import re
import requests


class TreeView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.subframe = ttk.Frame(self)
        self.subframe.grid(row=0, column=0, sticky='nsew')

        self.subframe.grid_columnconfigure(0, weight=1)
        self.subframe.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.subframe,
            show='headings',
            bootstyle='dark')
        self.tree['columns'] = (1, 2)
        self.tree.column(1, anchor=tk.CENTER)
        self.tree.column(2, anchor=tk.CENTER)

        vs = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.tree.yview)
        vs.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.tree['yscrollcommand'] = vs.set
        hs = ttk.Scrollbar(
            self,
            orient=tk.HORIZONTAL,
            command=self.tree.xview)
        hs.grid(column=0, row=1, sticky=(tk.E, tk.W))
        self.tree['xscrollcommand'] = hs.set

        self.tree.heading(1, text='Word')
        self.tree.heading(2, text='Count')

        self.tree.grid(row=0, column=0, sticky='nsew')


class ScrapeEngine(ttk.Frame):
    """makes a tkinter frame"""

    def __init__(self, *args, **kwargs):
        """initializes super class and attributes"""
        super().__init__(*args, **kwargs)
        self.inputs = {}

        self.grid_rowconfigure(4, weight=5)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text='Url(start with http or https)').grid(
            row=0, column=0, pady=15)
        self.inputs['url'] = ttk.Entry(
            self,
            width=85)
        self.inputs['url'].grid(row=1, column=0)

        self.info_label = ttk.Label(self, text='')
        self.info_label.grid(row=2, column=0, pady=5)

        self.btn = ttk.Button(
            self,
            text='Submit',
            bootstyle='light-outline',
        )
        self.btn.grid(row=3, column=0, pady=15)

    def show_info(self, txt, style):
        self.info_label['text'] = txt
        self.info_label.config(bootstyle=style)
        self.info_label.after(7000, self.hide_info)

    def hide_info(self):
        self.info_label['text'] = ''


class App(tk.Tk):
    """creates window"""

    def __init__(self, *args, **kwargs):
        """initializes super class and attributes"""
        super().__init__(*args, **kwargs)
        self.bind('<Return>', lambda event: self.scrape())

        self.style = ttk.Style()
        self.style.theme_use('cyborg')
        d_font = tk.font.nametofont('TkDefaultFont')
        d_font.configure(size=11, family='Helvetica')

        self.title('Web-Scrapping-1')
        self.geometry('720x640')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.frame = ScrapeEngine(self)
        self.frame.grid(column=0, row=0, sticky='nsew')
        self.frame.btn.config(command=lambda: self.scrape())

        self.tree = TreeView(self)
        self.tree.grid(column=0, row=1, sticky='nsew')

    def scrape(self):
        url = self.frame.inputs['url'].get()
        regex_web = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'

        if url != '':

            if re.fullmatch(regex_web, url):

                try:
                    page = requests.get(url)
                    soup = bs4.BeautifulSoup(
                        page.content, features='html.parser')
                    data = soup.find_all('body')
                    text = 'Success!'
                    self.frame.show_info(text, 'success')
                    # data cleaning
                    data1 = [el.text.strip().split() for j in data for el in j]
                    data2 = [i for i in data1 if i != '']
                    data3 = [i for j in data2 for i in j]
                    data4 = [i.lower() for i in data3]

                    data5 = []

                    for word in data4:
                        symbols = r"!@#$%^&*()_-+={[}]|\;:\"<>?/.,"

                        for i in range(len(symbols)):

                            if symbols[i] in word:
                                word = word.replace(symbols[i], ' ')

                        data5.append(word.split())

                    clean_data = [i for j in data5 for i in j]
                    clean_data.sort()

                    dicto = {}

                    for word in clean_data:

                        if word in dicto:
                            dicto[word] += 1
                        else:
                            dicto[word] = 1

                    c = Counter(dicto)
                    sorted_dict = c.most_common()

                    try:
                        for row in self.tree.tree.get_children():
                            self.tree.tree.delete(row)
                    except:
                        pass
                    finally:
                        for result in sorted_dict:
                            self.tree.tree.insert('', tk.END, values=result)

                except Exception as e:
                    text = '''
                    Check your internet connection!
                    Check if the url is correct!
                    Now try again
                    '''
                    self.frame.show_info(text, 'danger')

            else:
                text = 'Enter a valid url!'
                self.frame.show_info(text, 'danger')

        else:
            text = 'Url field can not be empty!'
            self.frame.show_info(text, 'danger')


if __name__ == "__main__":
    app = App()
    app.mainloop()
