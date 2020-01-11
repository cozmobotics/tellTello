# tello demo by Ryze Robotics, modified by Martin Piehslinger


# todo:
# don't print watch immediately but write it to an array and print it later 

# done:
# scripting feature 
# commands are not interpreted immediately but inserted into the commands array 
# timer task .... keepalive and regular status updates 
# recvBasic: interpretation of answer 
# watch feature
# debug feature
# sleep command (via timer task, don't use python's sleep command - so the user can interact while sleeping) 

import threading 
import socket
import sys
import time
from pythonping import ping
import msvcrt					# works for windows only. Linux users, import getch instead (not tested)
import time 
import argparse

#-----------------------------------------------------------------------------------
def help ():
	'''print help message. +++ variaous topics +++ information like battery, temperature '''
	
	print ("tellTello.py")
	print ("************")
	print ("")
	print ("A console-based frontend to the SDK of the Ryze Tello Quadrocopter")
	print ("")
	print ("Input methods: string- or key-based. ")
	print ("The program starts with string-based input. Use the command \"key\" to switch to key-based input. ")
	print ("Use the ESC key to switch back to string-basedinput. ")
	print ("")
	print ("String-based inputs: All SDK commands such as \"takeoff\" or \"speed 80\" plus the following: ")
	print ("key     ... enter key mode")
	print ("help    ... this help")
	print ("watch a b c d ... select which values to extrace from state string, like \"watch bat baro agx\". \"watch\" will reset to non-interpreted state.")
	print ("watchperiod n ... every n seconds, a satete frame will be printed. n=-1 turns off the state strings. ")
	print ("script file   ... opens file which contains commands to execute ")
	print ("state n ... output n lines of status strings")
	print ("dist  n ... set the distance for move commands (to be given in key mode, such as \"w\", which will make Tello go up n centimeters)")
	print ("ang   n ... set the angle for rotate commands (to be given in key mode, such as \"a\", which will make Tello turn left n degrees)")
	print ("end     ... end tellTello")
	print ("")
	print ("key-based command input:")
	print ("F1 or ? ... this help")
	print ("F2 ... print one status string (equals \"state 1\")")
	print ("c  ... command (send the string \"command\" to Tello)")
	print ("t  ... takeoff")
	print ("l  ... land")
	print ("w or 8 ... go up dist centimeters      (see \"dist\" command)")
	print ("a or 4 ... turn left (ccw) ang degrees (see \"ang\"  command)")
	print ("s or 2 ... go down dist centimeters    (see \"dist\" command)")
	print ("d or 6 ... turn right (cw) ang degrees (see \"ang\"  command)")
	print ("up     ... go forward dist centimeters (see \"dist\" command)")
	print ("left   ... go left dist centimeters    (see \"dist\" command)")
	print ("down   ... go backward dist centimeters(see \"dist\" command)")
	print ("right  ... go right dist centimeters   (see \"dist\" command)")
	print ("h or 5 ... stop current movement and hover")
	print ("p  ... \"PANIC!\" = stop motors immediately")
	print ("-  ... reduce \"dist\" by half         (see \"dist\" command)")
	print ("+  ... double \"dist\"                 (see \"dist\" command)")
	print ("/  ... reduce \"ang\" by half          (see \"ang\" command)")
	print ("*  ... double \"ang\"                  (see \"ang\" command)")
	print ("ESC... return to string-based input")
	print ("")

#-----------------------------------------------------------------------------------
def debug (Level, Message, end = '\n'):
	''' print message, depending upon debug-level which is chosen by teh user '''
	global DebugLevel
	
	if (Level <= DebugLevel):
		print (Message, end = end)
#-----------------------------------------------------------------------------------
def recvBasic():
	''' receive responds to commands (such as "ok") '''
	global TimeSent
	global TelloReady
	global Running
	global DataDecoded
	global SockBasic
	
	debug (3, "Tello recvBasic task started")
	count = 0
	while Running: 
		RecvError = False
		# data = "---"
		# data = data.encode(encoding="utf-8")
		DataDecoded = ''
		try:
			data, server = SockBasic.recvfrom(1518)
		except Exception as e:
			RecvError = True
			if (str(e) == 'timed out'):
				debug (5, ".", end = "") # python2 users, please remove this line
				pass
			else:
				debug (1, '\n------------------- Exception: ' + str(e) + '\n')
				break
		if (not RecvError):
			# Time = (time.time() - TimeSent)
			try:
				DataDecoded = data.decode(encoding="utf-8")
			except Exception as e:
				debug (1, str(e))
			debug(2, DataDecoded)
			TelloReady = True


	debug (3, "recvBasic ended")
#-----------------------------------------------------------------------------------
def recvBasicDummy():
	''' for offline testing '''
	global Running
	global TelloReady
	
	debug (3, "recvBasic started")
	
	while (Running):
		time.sleep (1)
		TelloReady = True
	debug (3, "recvBasic ended")
#-----------------------------------------------------------------------------------
def recvState():
	''' receive the Tello's state, print it as is or call interpreteState ''' 
	global Running
	global StateDecoded
	global SockState
	global NumFrames
	global WhichWatch 
	
	debug (4, "Tello recvState task started")
	count = 0
	while Running: 
		RecvError = False
		try:
			data, server = SockState.recvfrom(1518)  
		except Exception as e:
			RecvError = True
			if (str(e) == 'timed out'):
				debug (3, ":", end = "") # python2 users, please remove this line
				pass
			else:
				debug (1, '\n------------------- Exception: ' + str(e) + '\n')
				break
		if (not RecvError):
			StateDecoded = data.decode(encoding="utf-8")
			if (NumFrames > 0):
				if (len(WhichWatch)>0): 
					interpreteState (StateDecoded)
				else:
					print(StateDecoded)
				NumFrames = NumFrames - 1


	debug (4, "recvState ended")

#-----------------------------------------------------------------------------------
def recvStateDummy():
	''' for offline testing '''
	global Running
	global StateDecoded
	global NumFrames
	
	debug (3, "recvState started")
	
	while (Running):
		StateDecoded = "mid:-1;x:0;y:0;z:0;mpry:0,0,0;pitch:-1;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:51;temph:54;tof:10;h:0;bat:88;baro:38.28;time:0;agx:-13.00;agy:-5.00;agz:-998.00;"
		if (NumFrames > 0):
			if (len(WhichWatch)>0): 
				interpreteState (StateDecoded)
			else:
				print (StateDecoded)
			NumFrames = NumFrames - 1

		time.sleep (1)
		
	debug (3, "recvState ended")
#-----------------------------------------------------------------------------------
def interpreteState (StateString):
	''' split the state string into keyword/value pairs and print selected values in csv format '''
	global StateDict
	global Command
	global WhichWatch
	global OldWhichWatch
	global LastCommand


	StateSplitted = StateString.split(';')
	while (StateSplitted):
		Pair = StateSplitted.pop(0)
		if (':' in Pair):
			PairSplitted = Pair.split (':')
			keyword = PairSplitted[0]
			value = PairSplitted[1]
			debug (6, "keyword = " + keyword + " value= " + value)
			StateDict[keyword] = value
			
	if (OldWhichWatch != WhichWatch):		# new watch set, we'll write a header for the CVS
		OutString = "watch;time;"
		for Key in WhichWatch:
			OutString = OutString + Key + ';'
		OutString = OutString + "LastCommand" + ';'
		print (OutString)
		OldWhichWatch = WhichWatch
	
	OutString = "watch;" + str(time.time()) + ';'
	for Key in WhichWatch:
		try:
			Value = StateDict[Key]
		except Exception:
			Value = 'error'
		OutString = OutString.replace ('.',',') # +++ add an arg to decide whether or not to replace
		OutString = OutString + Value + ';'
	OutString = OutString + LastCommand + ';'
	print (OutString)
		
	
#--------------------------------------------------------------------------
def timerFunc():
	''' schedule keepalive and watch '''
	global Running
	global Commands
	global TimeKeepalive
	global NumFrames
	global TimeState
	global WatchPeriod
	global SleepTime
	
	debug (3, "Timer task started")
	Time = time.time()
	TimeKeepalive = Time + 10
	
	while (Running):
		Time = time.time()
		
		if ((Time > TimeState) and (WatchPeriod > 0)):
			NumFrames = 1
			TimeState = Time + WatchPeriod
	
		if ((SleepTime > 0) and (Time > SleepTime)):
			SleepTime = -1
			debug (4, str(Time) + ", time to wake up")
	
		if (Time > TimeKeepalive):
			sendCommand ("wifi?")	# +++ make it dependent of SDK version
	
	debug (3, "Timer task ended")
#--------------------------------------------------------------------------
def scriptRead (FileName, WhereToAdd): 
	''' read a script from a file and add the commands to an existing list of Commands. Filename = file to read, WhereToInsert = i for insert, a for append '''
	global Commands
	
	try:
		FileHandle = open (FileName, "r")
	except Exception as e:
		debug (1, str(e))
		debug (1, "Errro: unable to load " + FileName)
		return (False)
		
	if (FileHandle):
		debug (2, "Reading script" + FileName)
		NewCommands = FileHandle.readlines()
		FileHandle.close()
		if (WhereToAdd == 'i'):
			Commands = NewCommands + Commands
		elif (WhereToAdd == 'a'):
			Commands = Commands + NewCommands
		elif (WhereToAdd == 'r'):
			Commands = NewCommands
		else:
			debug (2, "Parameter WhereToAdd=" + WhereToAdd + " in function scriptRead not recognized, must be r, i or a")
			return (False)
		return (True)
		
	else:
		return (False)

#-----------------------------------------------------------------------------------
def waitForConnection (IpAddress):
	''' send pings to IpAddress until ping is successful. No timeout, will wait forever. '''
	Count = 0
	Connected = False
	while (not Connected):
		Count = Count + 1
		PingError = False
		try:
			PingResult = (ping(IpAddress,timeout=1,count=1))
		except Exception as e:
			debug (1, str(e))
			PingError = True
			
		if (not PingError):
			if ((PingResult.success())):
				Connected = True
			
		if (not Connected):
			debug (2, 'waiting for connection ' + str (Count) + ' ...')
			time.sleep (1)


#--------------------------------------------------------------
def sendCommand(msg):
	''' send a command to Tello. Wind up the keep alive time '''
	global TelloReady
	global SockBasic
	global tello_address
	global TimeKeepalive
	global args
	global Offline
	global tello_address
	global LastCommand
	
	LastCommand = msg
	debug (2, msg, end='')
	TelloReady = False
	msg = msg.encode(encoding="utf-8") 
	if (not Offline):
		sent = SockBasic.sendto(msg, tello_address)
	else:
		sent = len(msg)
	TimeKeepalive = time.time() + 10
	debug (3, ': ' + str(sent) + ' bytes sent')

#-----------------------------------------------------------------------------------

'''global variables'''
Running = True
DataDecoded = ""
TelloState = ""
StateDecoded = ""
NumFrames = 0
IpAddress = '192.168.10.1'
host = ''
InputModeString = True
Dist = 40
Angle = 90
SockBasic = None
SockState = None
TelloReady = True
NumFrames = 0
Commands = []
TimeKeepalive = time.time() + 10
TimeState = 0
Offline = True
StateDict = {"mid":"-1","x":"0","y":"0","z":"0","mpry":"0,0,0","pitch":"0","roll":"0","yaw":"0","vgx":"0","vgy":"0","vgz":"0","templ":"53","temph":"55","tof":"10","h":"0","bat":"72","baro":"-70.56","time":"0","agx":"-2.00","agy":"-10.00","agz":"-999.00"}
WhichWatch = []
OldWhichWatch = []
WatchPeriod = -1
DebugLevel = 3
tello_address = ('', 0)
LastCommand = ""
SleepTime = -1


#--------------------------------------------------------------
def main():
	''' the main program of tellTello '''
	global Running
	global InputModeString
	global Dist
	global Angle
	global SockBasic
	global SockState
	global TelloReady
	global NumFrames
	global Commands
	global Offline
	global WhichWatch
	global WatchPeriod
	global DebugLevel
	global tello_address
	global SleepTime

	parser = argparse.ArgumentParser(description = "tellTello - a console program for the Ryze Robotics Tello quadrocopter", epilog="enter \"help\" command for more information")
	parser.add_argument("--ip", type=str, default='192.168.10.1', help="ip address, default=192.168.10.1")
	parser.add_argument("-s", "--script", type=str, default="", help="script to execute")
	parser.add_argument("-w", "--watch", type=str, default='', help="list of watch expressions like \"mid x y z\"")
	parser.add_argument("-o", "--offline", type=str, default='No', help="test this program without being connected to a Tello")
	parser.add_argument("-d", "--debug", type=int, default='1', help="debug level ... 0=no debug messages, higher number for more messages")
	args = parser.parse_args()
	
	DebugLevel = args.debug

	if (args.offline == 'No'):
		Offline = False
	
	IpAddress = args.ip
	tello_address = (IpAddress, 8889)

	debug (1, "waiting for " + IpAddress)
	if (not Offline):
	
		waitForConnection (IpAddress)
		
		# --- basic communication --------------
		# Create a UDP socket
		portBasic = 8889
		locaddrBasic = (host,portBasic) 
		SockBasic = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		SockBasic.settimeout (1)
		SockBasic.bind(locaddrBasic)

		#recvThreadBasic create
		recvThreadBasic = threading.Thread(target=recvBasic)
		recvThreadBasic.start()

		# ------- retrieving state --------------------
		# Create a UDP socket
		portState = 8890
		locaddrState = (host,portState) 
		SockState = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		SockState.settimeout (1)
		SockState.bind(('0.0.0.0', portState))

		#recvThreadState create
		recvThreadState = threading.Thread(target=recvState)
		recvThreadState.start()
	else:
		#recvThreadBasic create
		recvThreadBasic = threading.Thread(target=recvBasicDummy)
		recvThreadBasic.start()
		#recvThreadState create
		recvThreadState = threading.Thread(target=recvStateDummy)
		recvThreadState.start()
		
	timerTask = threading.Thread(target=timerFunc)
	timerTask.start()

	TimeSend = 0
	TelloReady = True



	print ('\r\n\r\nTello Python3 Demo.\r\n')

	debug (1, 'Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed? battery?')
	debug (1, 'state n ... print status string n times \r\n')
	debug (1, 'end -- quit demo.\r\n')

	msg = ''
	Commands = ['command','sdk?']
	if (args.script != ""):
		if (not scriptRead (args.script, 'a')):
			sys.exit()
			
	InputModeString = True

	while Running: 
		
			if (TelloReady and InputModeString and (len(Commands) == 0) and (len(msg) == 0)):		# +++: only prompt for msg when we do not have a command in the list, but fetch the command only if no key input has arrived
				msg = input(">");

			
			if (not InputModeString): 		# keys have higher priority than Commands 
				if (msvcrt.kbhit()):
					Char1 = msvcrt.getch()
					# print (Char1[0])
					Char2 = ''
					if (msvcrt.kbhit()):			# second character when an arrow key, a function key ... is pressed
						Char2 = msvcrt.getch()
					
					if   (chr(Char1[0]) == 'c'):
						msg = 'command'
					elif (chr(Char1[0]) == 't'):
						msg = 'takeoff'
					elif (chr(Char1[0]) == 'l'):
						msg = 'land'
					elif (chr(Char1[0]) == '8'):
						msg = 'up ' + str (Dist)
					elif (chr(Char1[0]) == '2'):
						msg = 'down ' + str (Dist)
					elif (chr(Char1[0]) == '4'):
						msg = 'ccw ' + str (Angle)
					elif (chr(Char1[0]) == '6'):
						msg = 'cw ' + str (Angle)
					elif (chr(Char1[0]) == '5'):
						msg = 'stop'
					elif (chr(Char1[0]) == 'w'):
						msg = 'up ' + str (Dist)
					elif (chr(Char1[0]) == 's'):
						msg = 'down ' + str (Dist)
					elif (chr(Char1[0]) == 'a'):
						msg = 'ccw ' + str (Angle)
					elif (chr(Char1[0]) == 'd'):
						msg = 'cw ' + str (Angle)
					elif (chr(Char1[0]) == 'h'):		# halt. (not 's' because s is already used for down) ... send immediately (don't wait for TelloReady)
						sendCommand ('stop')
						msg = ''
					elif (chr(Char1[0]) == 'p'):		# the PANIC! button ... send immediately (don't wait for TelloReady)
						sendCommand ('emergency')
						msg = ''
					elif (chr(Char1[0]) == '-'):
						if (Dist >= 40):
							Dist = Dist / 2
							msg = "dist " + str(Dist)
					elif (chr(Char1[0]) == '+'):
						if (Dist <= 250):
							Dist = Dist * 2
							msg = "dist " + str(Dist)
					elif (chr(Char1[0]) == '/'):
						if (Angle >= 30):
							Angle = Angle / 2
							msg = "ang " + str(Angle)
					elif (chr(Char1[0]) == '*'):
						if (Angle <= 1800):
							Angle = Angle * 2
							msg = "ang " + str(Angle)
					elif (chr(Char1[0]) == '?'):
						help()
						msg = ''
					elif (Char1[0] == 27):
						msg = ''
						InputModeString = True
						debug (2, "key mode ended")
					elif (Char1[0] == 224):
						if   (Char2[0] == 72):		# up arrow
							msg = 'forward ' + str (Dist)
						elif (Char2[0] == 80):		# down arrow
							msg = 'back ' + str (Dist)
						elif (Char2[0] == 75):		# left arrow
							msg = 'left ' + str (Dist)
						elif (Char2[0] == 77):		# right arrow
							msg = 'right ' + str (Dist)
					elif (Char1[0] == 0):
						if   (Char2[0] == 59):		# F1
							help()
							msg = ''
						elif (Char2[0] == 60):		# F2
							msg = "state 1"

					debug (4, "---" + msg)
					

			# remove comments
			Hash = msg.find("#")
			if (Hash != -1):
				msg = msg[0:Hash]


			if (len (msg) > 0):
				Splitted = msg.split()
				keyword = Splitted[0]
				
				if    (keyword == 'end'):
					debug (1, 'ending tellTello')
					Running = False
					msg = ''
				elif (keyword in ['help', 'h', '?', 'e']):
					help()
					msg = ''
				elif (keyword == 'state'):
					if (len(Splitted) > 1):
						NumFrames = int(Splitted[1])
					else:
						debug (1, "please specify teh nuber of state frames to be pronted")
					msg = ''
				elif (keyword == 'dist'):
					Dist = int(Splitted[1])
					msg = ''
				elif (keyword == 'ang'):
					Angle = int(Splitted[1])
					msg = ''
				elif (keyword == 'key'):
					InputModeString = False
					debug (2, "Use keys to control Tello - t,l,w/a/s/d, cursor keys, ESC to end key mode")
					msg = ''
				elif (keyword == 'watch'):
					Watches = msg.split()
					Watches.pop(0)
					WhichWatch = Watches
					msg = ''
				elif (keyword == 'watchperiod'):
					try:
						WatchPeriod = float(Splitted[1])
					except Exception:
						WatchPeriod =  -1
					debug (3, "wach period = " + str (WatchPeriod))
					msg = ''
				elif (keyword == 'sleep'):
					try:
						SleepTimeDiff = float(Splitted[1])
					except Exception:
						SleepTime =  -1
						debug (1, "error in sleep statement")
					debug (3, "sleeping = " + str (SleepTimeDiff))
					SleepTime = SleepTimeDiff + time.time()
					debug (5, "will wake up at " + str(SleepTime))
					msg = ''
				elif (keyword =='debug'):
					if (len(Splitted) > 1):
						DebugLevel = int(Splitted[1])
				elif (keyword =='script'):
					if (len(Splitted) > 1):
						if (not scriptRead (Splitted[1], 'i')):
							debug (1, "unable to load " + Splitted[1])
					else:
						debug (1, "error: no filename given")
					msg = ''
				else:
					# Send data
					if (TelloReady):
						sendCommand (msg)
						msg = ''
			
			else:				# no message, let's see if we have a command in the list 
				if ((len(Commands) > 0) and (SleepTime < 0)):
					msg = Commands.pop(0)
					msg = msg.replace ('\n', ''); # trim newline-character at end of line, otherwise the command is not recognized 
					debug (2, msg)
			# except KeyboardInterrupt:
				# Running = False
				# print ('\n ctrl-break \n')
				# break
			

	TimeShutdown = 3
	debug (2, "Will shut down in " + str(TimeShutdown) + " seconds")
	time.sleep (TimeShutdown) # give recvBasic task some time to end 
	if (args.offline == 'No'):
		SockBasic.close()  
		SockState.close()
	debug (2, "Thank you for using tellTello")

#--------------------------------------------------------------------------

if __name__ == '__main__':
	main() 

