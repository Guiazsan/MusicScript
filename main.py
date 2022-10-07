import pygame.midi
import time
import re
import string
from datetime import datetime
from multiprocessing import Process

dictNotes = ["c","cs","d","ds","e","f","fs","g","gs","a","as","b"]
BEATNOTE = 4
COMPASSTIME = 4
BPM = 140

INSTRUMENTS = []
SESSIONS = []

class Instrument():
    name : str
    midiNumber : int
    pitch : int
    channel : int

class SessionInstrument():
    instrument : Instrument
    notes : []
    player : pygame.midi.Output

class Note():    
    startTime : time
    duration : float
    pitch : int
    multi : bool
    played : bool

class Session():
    name : str
    sessionInstruments : []
    
def readNotes(strNotes : str, octave : int) -> []:
    resultNotes = []
    # Faço divisão complexa de string, mantendo itens dentro dos parenteses
    notes = re.split(r',\s*(?![^()]*\))', strNotes)
    for strNote in notes:
        notePlus = []
        note = ""
        if "+" in strNote:
            plusSplit = strNote.split("+")
            for i in range(len(plusSplit)):
                if i == 0:
                    note = plusSplit[i]
                else:
                    notePlus.append(plusSplit[i])
            strNote = plusSplit[0]

        noteTone = ""
        noteTime = ""
        endTime = False
        for n in strNote:
            if n.isdigit() and not endTime:
                noteTime += n
            else:
                endTime = True
                noteTone += n

        noteTime = (BEATNOTE / int(noteTime)) * (60/BPM)

        for times in notePlus:
            noteTime = noteTime + ((BEATNOTE / int(times)) * (60/BPM))
        
        tones = noteTone.replace("(", "").replace(")", "").split(",")

        for tone in tones:
            newOctave = re.findall(r'\d+', tone)
            newNote = Note()
            newNote.startTime = None
            newNote.pitch = dictNotes.index(re.sub(r'[^a-zA-Z]', '', tone)) + (8 * (int(newOctave[0]) if len(newOctave) > 0 else octave))
            newNote.played = False
            newNote.multi = "(" in noteTone
            newNote.duration = noteTime
            resultNotes.append(newNote)

    return resultNotes

def playNotes(sessionInstruments : []):
    finished = False
    actualNotes = []    

    for sessionInstrument in sessionInstruments:
        actualNotes.append(0)

    while not finished:
        
        for sessionInstrument in sessionInstruments:
            player = sessionInstrument.player
            player.set_instrument(int(sessionInstrument.instrument.midiNumber), channel=channel)
            notes : sessionInstrument.notes = [i for i in sessionInstrument.notes if not i.played]
            for note in notes:
            # if len(notes) > 0:
            #     note = notes[0]
                if note.startTime == None:
                    note.startTime = datetime.now()
                    player.note_on(note.pitch, 127)
                else:
                    duration = datetime.now() - note.startTime
                    if (duration.total_seconds() >= note.duration):
                        player.note_off(note.pitch, 127)
                        note.played = True
                
                if not note.multi



# def playNotes(strNotes : str, midiNumber : int, octave : int = 0):
#     # Faço divisão complexa de string, mantendo itens dentro dos parenteses
#     notes = re.split(r',\s*(?![^()]*\))', strNotes)

#     player = pygame.midi.Output(0)
#     player.set_instrument(midiNumber)

#     for strNote in notes:

#         notePlus = []
#         note = ""
#         if "+" in strNote:
#             plusSplit = strNote.split("+")
#             for i in range(len(plusSplit)):
#                 if i == 0:
#                     note = plusSplit[i]
#                 else:
#                     notePlus.append(plusSplit[i])
#             strNote = plusSplit[0]

#         noteTone = ""
#         noteTime = ""
#         endTime = False
#         for n in strNote:
#             if n.isdigit() and not endTime:
#                 noteTime += n
#             else:
#                 endTime = True
#                 noteTone += n

#         noteTime = (BEATNOTE / int(noteTime)) * (60/BPM)

#         for times in notePlus:
#             noteTime = noteTime + ((BEATNOTE / int(times)) * (60/BPM))
        
#         tones = noteTone.replace("(", "").replace(")", "").split(",")

#         for tone in tones:
#             newOctave = re.findall(r'\d+', tone)
#             player.note_on(dictNotes.index(re.sub(r'[^a-zA-Z]', '', tone)) + (8 * (int(newOctave[0]) if len(newOctave) > 0 else octave)), 127)

#         time.sleep(noteTime)

#         for tone in tones:
#             newOctave = re.findall(r'\d+', tone)
#             player.note_off(dictNotes.index(re.sub(r'[^a-zA-Z]', '', tone)) + (8 * (int(newOctave[0]) if len(newOctave) > 0 else octave)), 127)
    
#     del player

pygame.midi.init()
player = pygame.midi.Output(0)
channel = 0

inMustache = False
actualInstrument = None
actualSession = None

f = open("teste.ms", "r")
lines = f.readlines()
for line in lines:
    if ("{" in line):
        inMustache = True
        if ("instrument" in line):
            actualInstrument = Instrument()
            actualInstrument.name = line[line.find("instrument")+len("instrument"):line.rfind("{")].strip()
        if ("session" in line):
            actualSession = Session()
            actualSession.name = line[line.find("session")+len("session"):line.rfind("{")].strip()
            actualSession.notes = []
            actualSession.sessionInstruments = []
    
    if actualInstrument != None:
        if "midiNumber" in line:
            actualInstrument.midiNumber = line.split("=")[1].strip()
        if "pitch" in line:
            actualInstrument.pitch = int(line.split("=")[1].strip())

    if (actualSession != None) and ("(" in line) and (")" in line):
        notesLine = line[line.find("(")+1:line.rfind(")")]
        instrument = [i for i in INSTRUMENTS if i.name == line[:line.find("(")].strip()]
        instrument = instrument[0]

        sessionInstrument = SessionInstrument()
        sessionInstrument.instrument = instrument
        sessionInstrument.notes = readNotes(notesLine, instrument.pitch)
        sessionInstrument.player = player
        channel += 1
        sessionInstrument.instrument.channel = channel
        # sessionInstrument.player.set_instrument(int(sessionInstrument.instrument.midiNumber), channel=channel)

        actualSession.sessionInstruments.append(sessionInstrument)

    if "}" in line:
        inMustache = False
        if actualInstrument != None:
            INSTRUMENTS.append(actualInstrument)
            actualInstrument = None

        if actualSession != None:
            SESSIONS.append(actualSession)
            actualSession = None
    else :
        if (not inMustache) and (line.strip().replace("\n", "") != ""):
            session : Session = [i for i in SESSIONS if i.name == line.strip()]
            if len(session) == 1:
                playNotes(session[0].sessionInstruments)

            if ("(" in line) and (")" in line):
                notesLine = line[line.find("(")+1:line.rfind(")")]
                instrument = [i for i in INSTRUMENTS if i.name == line[:line.find("(")]]
                instrument = instrument[0]
                playNotes(notesLine, int(instrument.midiNumber), int(instrument.pitch))
                readNotes(notesLine, instrument)

pygame.midi.quit()