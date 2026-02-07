from customtkinter import *
import socket
import threading

class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()
        self.user_name = None
       
        self.title('Підключення до чату')
        self.geometry("300x360")


        CTkLabel(self, text='Вхід в чат...',
                 font=('Times New Roman', 18), anchor='w').pack(padx=10, pady=25, fill='x')
       
        self.name_entry = CTkEntry(self, placeholder_text='Name',
                                   font=('Times New Roman', 18), height=35)
        self.name_entry.pack(padx=10, pady=15, fill='x')
        self.host_entry = CTkEntry(self, placeholder_text='Host',
                                   font=('Times New Roman', 18), height=35)
        self.host_entry.pack(padx=10, pady=15, fill='x')
        self.port_entry = CTkEntry(self, placeholder_text='Port',
                                   font=('Times New Roman', 18), height=35)
        self.port_entry.pack(padx=10, pady=15, fill='x')
        CTkButton(self, text='Вхід', font=('Times New Roman', 18), fg_color="#686868", height=35,
                  command=self.start_chat).pack(padx=10, pady=25, fill='x')
    def start_chat(self):
        self.user_name = self.name_entry.get()
        try:
            print(self.host_entry.get(), self.port_entry.get())
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.connect((
                self.host_entry.get(),
                int(self.port_entry.get())
                ))
            hello = f'TEXT@{self.user_name}@[SYSTEM]{self.user_name} доєднався до чату!\n'
            self.sock.send(hello.encode())
            self.destroy()
            win = MainWindow(self.sock, self.user_name)
            win.mainloop()
        except:
            self.host_entry.delete(0, END)
            self.port_entry.delete(0, END)


class MainWindow(CTk):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.user_name = name
        w, h = 400, 300
        self.geometry(f"{w}x{h}")
        #menu
        self.menu = CTkFrame(self, width = 200, height = h)
        self.menu.pack_propagate(False)


        self.menu.configure(width=0)
        self.menu.place(x=0, y=0)


        self.label = CTkLabel(self.menu, text='SETTINGS')
        self.entry_name = CTkEntry(self.menu, placeholder_text='name...')
        self.label_theme = CTkOptionMenu(self.menu, values=['auto', 'dark', 'light'], fg_color="#686868",
                                         command=self.change_theme, button_color= "#4E4E4E", button_hover_color="#686868")
        self.submit = CTkButton(self.menu, text='Submit', command=self.change_name, fg_color="#686868")


        self.label.pack(pady=30)
        self.entry_name.pack(pady=(15,10))
        self.label_theme.pack()
        self.submit.pack(pady=(15,10))
        #chat
        self.btn = CTkButton(self, text="☰", width=30, command=self.toggle_show_menu, fg_color="#686868")
        self.chat_text = CTkTextbox(self, state = 'disable')
        self.input_text = CTkEntry(self, placeholder_text='...')
        self.send_btn = CTkButton(self, text='ᯓ➤', width=40, height=30, command=self.send_message_, fg_color="#686868")


        self.btn.place(x=0, y=0)
        self.chat_text.place(x = 0, y = 30)
        self.input_text.place(x = 0, y = 250)
        self.send_btn.place(x = 200, y = 250)
        #var
        self.is_show_menu = False
        self.menu_width = 0
        self.speed_show_menu = 20
        #
        self.chat_text.configure(state='disable')
        threading.Thread(target=self.receive_message_, daemon=True).start()
        self.adaptive()




    def add_message(self, text):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(END, text + '\n')
        self.chat_text.configure(state='disable')




    def send_message_(self):
        message = self.input_text.get()
        if message:
            self.add_message(f'{self.user_name}: {message}')#????
            data = f'TEXT@{self.user_name}@{message}\n'
            try:
                self.sock.sendall(data.encode())
            except:
                pass
            self.input_text.delete(0, END)
    def receive_message_(self):
        buffer = ''
        while True:
            try:
                m = self.sock.recv(4096).decode()
                if not m:
                    break
                buffer += m
                while '\n' in buffer:
                    line, buffer  = buffer.split('\n', 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()




    def handle_line(self, line):
        if not line:
            return
        parts = line.split('@',2)
        if parts[0] == 'TEXT':
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f'{author}: {message}')
        else:
            self.add_message(f'>>>{line}')


    def change_name(self):
        name = self.entry_name.get()
        if name:
            self.user_name = name
            self.entry_name.delete(0, END)
        else:
            self.entry_name.insert(END, 'Ім\'я відсутнє')




    def change_theme(self, value):
        if value=='auto': set_appearance_mode('system')
        else: set_appearance_mode(value)


    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()


    def show_menu(self):
        if self.menu_width < 200:
            self.menu_width += self.speed_show_menu
            self.menu.configure(width = self.menu_width, height=self.winfo_height())
            if self.menu_width>=30:
                self.btn.configure(width=self.menu_width, text='MENU ☰')
        if self.is_show_menu:
            self.after(20, self.show_menu)


    def close_menu(self):
        if self.menu_width >= 0:
            self.menu_width -= self.speed_show_menu
            self.menu.configure(width = self.menu_width, height=self.winfo_height())
            if self.menu_width<30:
                self.btn.configure(width=self.menu_width, text='☰')
        if not self.is_show_menu:
            self.after(20, self.close_menu)


    def adaptive(self):
        k = 1
        self.screen_width = self.winfo_width() / k
        self.screen_height = self.winfo_height() / k
        self.s_btn_width = self.send_btn.winfo_width() / k
        self.s_btn_height = self.send_btn.winfo_height() / k


       #place
        self.send_btn.place(
            x=self.screen_width - self.s_btn_width - 5,
            y=self.screen_height - self.s_btn_height - 5
        )
        if self.menu_width>=0:
            self.chat_text.place(
                x = self.menu_width + 5,
                y = 30 + 5
            )
            self.input_text.place(
                x = self.menu_width + 5 ,
                y= self.screen_height - self.s_btn_height - 5
            )
        else:
            self.chat_text.place(
                x = 5,
                y = 30 + 5
            )
            self.input_text.place(
                x = 5,
                y= self.screen_height - self.s_btn_height - 5
            )


        #size
        self.send_btn.configure(
            width= self.screen_width / 10,
            height= self.screen_height / 10
        )


        self.input_text.configure(
            width= self.screen_width - self.s_btn_width - self.menu_width - 15,
            height = self.s_btn_height
        )
        self.chat_text.configure(
            width =  self.screen_width - self.menu_width - 10,
            height = self.screen_height - 30 - self.s_btn_height - 20
        )
   
        self.after(50, self.adaptive)




app = RegisterWindow()
app.mainloop()
