import tkinter as tk
import socket
import threading
from cryptography.fernet import Fernet
from tkinter import messagebox

window = tk.Tk()
window.title("Client")
username = " "
password = " "

#initialise an encryption key
key = b'WpCqtNdnIcBrBMwknbkN49_Hq3_Pprl-8ddL2GvCRrc='
fernet = Fernet(key)


#create tkinter user interface
topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text="Name:      ").pack(side=tk.LEFT)

entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)

topFrame.pack(side=tk.TOP)


midFrame = tk.Frame(window)
lblName2 = tk.Label(midFrame, text="Password:").pack(side=tk.LEFT)

entPsw = tk.Entry(midFrame, show="*")
entPsw.pack(side=tk.LEFT)


midFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
btnConnect = tk.Button(displayFrame, text="Login", command=lambda: connect())
btnConnect.pack(side=tk.TOP)
lblLine = tk.Label(
    displayFrame, text="------------------------------------------------------------------").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="#0F110C")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7",
                 highlightbackground="#CECCCC", state="disabled")


displayFrame.pack(side=tk.TOP)


bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="#CECCCC")
tkMessage.bind(
    "<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)

#connect client to chat
def connect():
    global username, client
    if len(entName.get()) < 1:
        tk.messagebox.showerror(
            title="ERROR", message="You must enter your first name")
    elif len(entPsw.get()) < 1:
        tk.messagebox.showerror(
            title="ERROR", message="You must enter your password")
    else:
        userExists = False
        
        #authenticate user

        with open('login.txt', 'rb') as login:
            for l in login:
                l = str(l)
                x = l.split(':')
                a = x[0].replace("b'", "")
                b = x[1].replace("'", "").replace("\\n", "")

                username = entName.get()
                password = entPsw.get()

                if a == username and b == password:
                    userExists = True

        if userExists == True:
            connect_to_server(username)
        else:
            tk.messagebox.showerror(
                title="ERROR", message="This user does not exist")


# network client
client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 6969


# connect client to the server
def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode())

        entName.config(state=tk.DISABLED)
        entPsw.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR", message="Cannot connect to host: " + HOST_ADDR +
                                " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


#recieve messages from the server
def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server:
            break
        
        # display recieved messages

        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            tkDisplay.insert(tk.END, "\n\n\t" + from_server)

        tkDisplay.config(foreground="#9D6381")

        tkDisplay.see(tk.END)

    sck.close()
    window.destroy()


#send your message
def getChatMessage(msg):

    msg = msg.replace('\n', '')

    tkDisplay.config(foreground="#9D6381")
    tkDisplay.config(state=tk.NORMAL)

    if len(msg) >= 1:
        tkDisplay.insert(tk.END, "\n\n" + "You: " + msg,
                         "tag_your_message")

    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)


# forward your message to the server
def send_mssage_to_server(msg):
    client_msg = str(msg)
    client.send(fernet.encrypt(client_msg.encode()))
    if msg == "exit":
        client.close()
        window.destroy()


window.mainloop()
