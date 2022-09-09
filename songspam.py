# songspam.py
# a program by lucas boebel
# mess with your friends

import threading
import time
import PySimpleGUI as sg
from subprocess import Popen, PIPE

RUN = False # boolean to stop a song midrun 

scpt = '''
        on run {targetPhone, targetMessage}
            tell application "Messages"
                set targetService to 1st account whose service type = iMessage
                set targetBuddy to participant targetPhone of targetService
                send targetMessage to targetBuddy
            end tell
        end run
       '''

# myid should be something like: "iMessage;+;chat87078286092147762"
# https://stackoverflow.com/questions/44852939/send-imessage-to-group-chat
scptgc ='''
        on run {targetID, targetMessage}
            tell application "Messages"
                set targetBuddy to a reference to text chat id targetID
                send targetMessage to targetBuddy
            end tell
        end run
        '''

def run(filename, phoneNum, window):
    try:
        song = open(filename, 'r')
        phoneNum = int(phoneNum)
    except:
        print("Something went wrong. Check that the file path and phone number are correct.")
        sg.Popup('Error', 'Something went wrong. Check that the file path and phone number are correct.')
    else:
        lastmin = 0
        lastsec = 0

        try:
            for line in song:
                if RUN:
                    # formatted as ["00:00.00", "text\n"]
                    print(line.strip())
                    linelist = line.strip('\ufeff').strip('[').strip().split(']')

                    try: # catch for weird formats at end of file
                        line = linelist[1]
                    except:
                        print("End of song. (or something went wrong)")
                        break

                    # formatted as ["00", "00.00"]
                    timelist = linelist[0].split(':')
                    currmin = int(timelist[0])
                    currsec = float(timelist[1])

                    if lastmin == currmin:
                        # .069 is a correction for the time it takes to run the iMessage script
                        time.sleep(max(0, currsec - (lastsec + .069))) 

                    else:
                        time.sleep(max(0, 60 - (lastsec + .069)))

                    lastmin = currmin          
                    lastsec = currsec

                    p = Popen(['osascript', '-', str(phoneNum), line], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                    p.communicate(scpt)

                else:
                    break
        finally:
            window.write_event_value('-THREAD-', '** DONE **')  # put a message into queue for GUI
            song.close()

# same as run, but for groupchats
def rungc(filename, myid, window):
    try:
        song = open(filename, 'r')
    except:
        print("Something went wrong. Check that the file path and chat id are correct.")
        sg.Popup('Error', 'Something went wrong. Check that the file path and phone number are correct.')
    else:
        lastmin = 0
        lastsec = 0

        try:
            for line in song:
                if RUN:
                    # formatted as ["00:00.00", "text\n"]
                    print(line.strip())
                    linelist = line.strip('\ufeff').strip('[').strip().split(']')

                    try: # catch for weird formats at end of file
                        line = linelist[1]
                    except:
                        print("End of song. (or something went wrong)")
                        break

                    # formatted as ["00", "00.00"]
                    timelist = linelist[0].split(':')
                    currmin = int(timelist[0])
                    currsec = float(timelist[1])

                    if lastmin == currmin:
                        # .069 is a correction for the time it takes to run the iMessage script
                        time.sleep(max(0, currsec - (lastsec + .069))) 

                    else:
                        time.sleep(max(0, 60 - (lastsec + .069)))

                    lastmin = currmin          
                    lastsec = currsec

                    p = Popen(['osascript', '-', '"' + str(myid) + '"', line], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                    p.communicate(scptgc)

                else:
                    break
        finally:
            window.write_event_value('-THREAD-', '** DONE **')  # put a message into queue for GUI
            song.close()

# PySimpleGUI stuff
def gui():
    global RUN

    sg.theme('DarkTeal1')

    layout = [
            [sg.Text('welcome to SongSpam!', size=(40, 1), justification='center', font=("Menlo", 25))],
            [sg.Text('choose a file ending in .lrc', size=(35, 1), font=("Menlo", 15))],
            [sg.Text('your file:', size=(10, 1), justification='left', font=("Menlo", 15)),
            sg.InputText('', size=(15, 1), justification='left', font=("Menlo", 15)), sg.FileBrowse(file_types=(("Text Files", "*.lrc"),))],
            [sg.Text('enter a 10-digit phone number (e.g: 1234567890)', size=(50, 1), font=("Menlo", 15))],
            [sg.Text('your number:', size=(12, 1), justification='left', font=("Menlo", 15)),
            sg.InputText('', size=(15, 1), justification='left', font=("Menlo", 15))],
            [sg.Text('OR enter an iMessage chat ID (e.g: iMessage;+;chat831551415676550949)', size=(70, 1), font=("Menlo", 15))],
            [sg.Text('your chatID:', size=(12, 1), justification='left', font=("Menlo", 15)),
            sg.InputText('', size=(15, 1), justification='left', font=("Menlo", 15))],
            [sg.Button('Run!', bind_return_key=True), sg.Button('Stop'), sg.Button('Exit')]
            ]

    window = sg.Window('SongSpam - a program by Lucas Boebel', layout)

    while True: # event loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        elif event == 'Run!':
            print(values)
            confirm = sg.popup_yes_no('Are you sure?')
            if confirm == 'Yes':
                RUN = True
                if values[1] != '':
                    threading.Thread(target=run, args=(values[0], values[1], window,), daemon=True).start()
                elif values[2] != '':
                    threading.Thread(target=rungc, args=(values[0], values[2], window,), daemon=True).start()


        elif event == '-THREAD-':
            sg.Popup('Song finished or stopped')
            print('Got a message back from the thread: ', values[event])

        elif event == 'Stop':
            RUN = False

    window.close()

if __name__ == '__main__':
    gui()
    print('Exiting Program')