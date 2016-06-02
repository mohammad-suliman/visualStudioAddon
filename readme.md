#add-on for visual studio

this add-on aims to resolve some issues with visual studio, and to enhance the user experience while using NVDA.

issues which have been fixed so far:
*	Improvements to intelliSense.
*	fixes for accessibility of the debug windows.
*	status bar is now reported when using  standard NVDA key stroke (NVDA+end)
*	break points are reported via speach and beeps
*	 some enhancements to the files / tools windows switcher
*	quick info tool tips are now supported. the shortcut for invoking this tool tip is ctrl + k and then ctrl + i
*	basic support for parameter info, use ctrl + shift + space to invoke this tool tip
note: the tool tip is not presented in a  friendly way, more fixes are needed.
*	errors list now works with NVDA's commands for navigating tables: control + alt + left / right arrow. also, it is possible to directly access each column with control + alt + number, where number is the number of the column you wish to access. for example: to access the first column use control + alt + 1.
note: those commands might change in the near future if they founded to be problimatic.
*	NVDA now reports the current line when navigating the code with the debugger. (stepping in / over / out) with the corrisponding keyboard commands.
*	tool box tool window improvements and fixes
The add-on is still under development, so expect more fixes and enhancements.
Your feedback is very important: please let me know if you have suggestions or any thoughts that could help us further improve this add-on.

## Features
Fixes in more detail:

*	fixes to intelliSense: unnecessary announcements when using intelliSense were removed to improve productivity. 
additionally, positional info of the suggested intelliSense items were removed. EG "int 1 of 9" is now reported as "int". however you can get those announcements back by setting a flag to False in the add-on source code. 
in the future, a check box may be dedicated to toggle this option.
NVDA's behavior with intelliSense is now as the following:
the focus of NVDA is usually placed in the editor, and the navigator object is the intelliSense menu item. so, you can review the last reported intelliSense item with review commands, (numpad keys on the desktop), and in the same tiem to type as usual in the editor and to get feedback.

*	fixes to debugging windows: NVDA now reads the content of the wotch, locals, and autos windows.

#important note: 
I need your feedback to know which parts of the UI need further improvements, as well as feedback for the features which were already implemented.
You can reach me at: 
mohmad.s93@gmail.com
Please feel free to let me know your thoughts.