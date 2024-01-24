import pickle
import socket
import threading
from tkinter import * 
from tkinter.font import Font
import os

global textBox
global name
global client
global chatlog


def receive_messages(client_socket, name):
    print('i am receiving messages')

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Server closed the connection.")
                break

            received_object = pickle.loads(data)
            message = received_object['message'].decode('utf-8')
            sender = received_object['sender'].decode('utf-8')
            print(sender)
            print(message)
            if sender=='system' :
                update_chat(received_object,3)
            elif message and message != "":
                print('\n' + sender + ' : ' + message)
                update_chat(received_object,1)
        except socket.error as e:
            print(f"Error receiving message: {e}")
            break
def update_chat(msg_obj, state):
    sender = msg_obj['sender'].decode('utf-8')
    msg = msg_obj['message'].decode('utf-8')

    chatlog.config(state=NORMAL)

    if state == 0:
        # Your messages (on the right)
        formatted_msg = 'YOU: ' + msg
        chatlog.tag_configure('self', background='lightblue')
        chatlog.insert(END, formatted_msg + '\n', 'self')
    elif state == 1:
        # Messages from other clients (on the left)
        formatted_msg = sender + ': ' + msg
        chatlog.tag_configure('other', background='#ff8080')
        chatlog.insert(END, formatted_msg + '\n', 'other')
    else :
        chatlog.tag_config('system', foreground='grey', font=('Helvetica', 10), justify='center')
        formatted_msg = msg
        chatlog.insert(END,formatted_msg + '\n','system')
    chatlog.config(state=DISABLED)
    chatlog.yview(END)
    chatlog.after(0, chatlog.yview, END)

def getName():
    global name
    name = nameBox.get("1.0", END).strip()
    gui_name.destroy()

def send():
    msg = textBox.get("1.0", END)
    msg_obj = {
        'sender': name.encode('utf-8'),
        'message': msg.strip().encode('utf-8')
    }
    update_chat(msg_obj,0)
    send_object(client, msg_obj)
    textBox.delete('1.0', END)
def press(event):
    send()
def press2(event):
    getName()


def send_object(client_socket, data):
    serialized_data = pickle.dumps(data)
    client_socket.send(serialized_data)

def main():
    global textBox
    global nameBox
    global client
    global chatlog
    global name  # Declare name as a global variable
    global gui_name

    host, port = "127.0.0.1", 9001
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print("Connected to the server.")
    # name = input("What is your name? ") 
    gui_name = Tk()
    gui_name.title("Enter Your Name")
    gui_name.geometry('380x430')

    theBigFont = Font(
        family='Terminal',
        size=17,
        weight='normal'
    )
    theFont = Font(
        family='Terminal',
        size=12,
        weight='normal'
    )

    welcomeLabel = Label(gui_name, text="Welcome to my chat room", font=theBigFont)
    welcomeLabel.pack(pady=10, side='top', anchor='n')
    welcomeLabel.place(relx=0.5,rely=0.2,anchor=CENTER)

    label = Label(gui_name, text="Enter your name:", font=theBigFont)
    label.pack(pady=10, side='top', anchor='n')
    label.place(relx=0.5,rely=0.4,anchor=CENTER)
    # Centering the text box
    nameBox = Text(gui_name, bg='white', width='30', height='1')
    nameBox.pack(pady=10)
    nameBox.place(relx=0.5,rely=0.5,anchor=CENTER)
    nameBox.bind('<KeyRelease-Return>',press2)

    # Centering the button
    submit_button = Button(gui_name, text="Submit", command=getName,font=theFont)
    submit_button.pack(pady=10)
    submit_button.place(relx=0.5,rely=0.6,anchor=CENTER)

    gui_name.mainloop()

    gui = Tk()
    gui.title("Mounir's chat application")
    gui.geometry('380x430')

    chatlog = Text(gui, bg='white', width='50', height='8')
    chatlog.config(state=DISABLED)
    
    textBox = Text(gui, bg='white', width='30', height='8')
    
    sendButton = Button(gui, text='Send', width='10', height='8', command=send,font=theFont)

    chatlog.place(x=6, y=6, height=386, width=370)
    textBox.place(x=6, y=401, height=20, width=265)
    sendButton.place(x=300, y=401, height=20, width=50)
    textBox.bind('<KeyRelease-Return>',press)

    # name = "Mounir"

    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client, name), daemon=True)
    receive_thread.start()
    gui.mainloop()

if __name__ == "__main__":
    main()
