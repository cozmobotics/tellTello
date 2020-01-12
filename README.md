# tellTello.py V 1.1
# ******************

A console-based frontend to the SDK of the Ryze Tello Quadrocopter

## What it does:
* Fly Tello with text commands (like "ccw 90") or with keys (like w/a/s/d and cursor keys)
* execute commands from a text file
* watch selected variables from the status string and write them to a comma-separated list (csv-format)

## Input methods: string- or key-based.
The program starts with string-based input. Use the command "key" or "joy" to switch to key-based input.
Use the ESC key to switch back to string-based input.

### String-based inputs: All SDK commands such as "takeoff" or "speed 80" plus the following:
* help    ... this help
* key     ... enter key mode
* joy     ... enter joystick mode
* watch a b c d ... select which values to extrace from state string, like "watch bat baro agx". "watch" without parameters will reset to non-interpreted state.
* watchperiod n ... every n seconds, a state frame will be printed. n=-1 turns off the state strings.
* state n ... output n lines of status strings
* dist  n ... set the distance for move commands (to be given in key mode, such as "w", which will make Tello go up n centimeters)
* ang   n ... set the angle for rotate commands (to be given in key mode, such as "a", which will make Tello turn left n degrees)
* script file... opens file which contains commands to execute
* sleep n ... pause for n seconds (fractons of seconds are allowed)
* end     ... end tellTello

### key-based command input (key and joy modes):
* F1 or ? ... this help
* F2 ... print one status string (equals "state 1")
* c  ... command (send the string "command" to Tello)
* t  ... takeoff
* l  ... land
* p  ... "PANIC!" = stop motors immediately
* j  ... enter joystick mode
* k  ... enter key mode
* h,H,5,space ... stop current movement and hover
* ESC... return to string-based input
#### Motion keys in key mode:
* w or 8 ... go up dist centimeters      (see "dist" command)
* a or 4 ... turn left (ccw) ang degrees (see "ang"  command)
* s or 2 ... go down dist centimeters    (see "dist" command)
* d or 6 ... turn right (cw) ang degrees (see "ang"  command)
*  up     ... go forward dist centimeters (see "dist" command)
*  left   ... go left dist centimeters    (see "dist" command)
*  down   ... go backward dist centimeters(see "dist" command)
*  right  ... go right dist centimeters   (see "dist" command)
*  -  ... reduce "dist" by half         (see "dist" command)
*  +  ... double "dist"                 (see "dist" command)
*  /  ... reduce "ang" by half          (see "ang" command)
*  *  ... double "ang"                  (see "ang" command)
#### Motion keys  in joystick mode:
* w or 8 ... move simulated joystick up by 10%
* a or 4 ... move simulated joystick ccw by 10%
* s or 2 ... move simulated joystick down by 10%
* d or 6 ... move simulated joystick cw by 10%
* up     ... move simulated joystick forward by 10%
* left   ... move simulated joystick left by 10%
* down   ... move simulated joystick back by 10%
* right  ... move simulated joystick right by 10%

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


