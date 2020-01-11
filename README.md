# tellTello
A console-based frontend to the SDK of the Ryze Tello Quadrocopter
Written in Python3, runs on Windows (sorry Linux users)

Input methods: string- or key-based.
The program starts with string-based input. Use the command "key" to switch to key-based input.
Use the ESC key to switch back to string-basedinput.

## String-based inputs: 
All SDK commands such as "takeoff" or "speed 80" plus the following:
* help    ... this help
* key     ... enter key mode
* watch a b c d ... select which values to extrace from state string, like "watch bat baro agx". "watch" without parameters will reset to non-interpreted state.
* watchperiod n ... every n seconds, a state frame will be printed. n=-1 turns off the state strings.
* script file   ... opens file which contains commands to execute
* state n ... output n lines of status strings
* dist  n ... set the distance for move commands (to be given in key mode, such as "w", which will make Tello go up n centimeters)
* ang   n ... set the angle for rotate commands (to be given in key mode, such as "a", which will make Tello turn left n degrees)
* end     ... end tellTello

## key-based command input:
* F1 or ? ... this help
* F2 ... print one status string (equals "state 1")
* c  ... command (send the string "command" to Tello)
* t  ... takeoff
* l  ... land
* w or 8 ... go up dist centimeters      (see "dist" command)
* a or 4 ... turn left (ccw) ang degrees (see "ang"  command)
* s or 2 ... go down dist centimeters    (see "dist" command)
* d or 6 ... turn right (cw) ang degrees (see "ang"  command)
* up     ... go forward dist centimeters (see "dist" command)
* left   ... go left dist centimeters    (see "dist" command)
* down   ... go backward dist centimeters(see "dist" command)
* right  ... go right dist centimeters   (see "dist" command)
* h or 5 ... stop current movement and hover
* p  ... "PANIC!" = stop motors immediately
* minus sign  ... reduce "dist" by half         (see "dist" command)
* plus sign   ... double "dist"                 (see "dist" command)
* slash       ... reduce "ang" by half          (see "ang" command)
* asterisk    ... double "ang"                  (see "ang" command)
* sleep n ... pause for n seconds (fractons of seconds are allowed)
* ESC... return to string-based input


## command line:

python tellTello.py [arguments]

*   -h, --help            show this help message and exit
*   --ip IP               ip address, default=192.168.10.1
*   -s SCRIPT, --script SCRIPT
                        script to execute
*   -w WATCH, --watch WATCH
                        list of watch expressions like "mid x y z"
*   -o OFFLINE, --offline OFFLINE
                        test this program without being connected to a Tello
*   -d DEBUG, --debug DEBUG
                        debug level ... 0=no debug messages, higher number for
                        more messages

enter "help" command for more information


