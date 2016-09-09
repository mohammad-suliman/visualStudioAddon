#add-on for visual studio

this add-on aims to resolve some issues with visual studio, and to enhance the user experience while using NVDA.

##downloading the add-on
you can download the add-on using 
[this link](https://www.dropbox.com/s/eizkvddpnitmoyx/visualStudio-1.0dev.nvda-addon?dl=1)
and then install it as any other add-on

##supported versions
the add-on has been tested with visual studio 2013 express and 2015 community and enterprise editions. however, it is expected to work with all editions from 2010 to 2015.
if you have encountered any problem with getting the add-on to work with any edition of VS 2010 to 2015, please let me know. 
also, if you have verified that the fixes by the add-on work with a version of VS which hasn't been tested so far, I'll be happy to hear from you, and update this doc accordingly.

##issues which have been fixed so far
*	Improvements to intelliSense.
*	fixes for accessibility of the debug windows.
*	status bar is now reported when using  standard NVDA key stroke (NVDA + end)
*	break points are reported via speech and beeps
*	enhancements to the files / tools windows switcher in visual studio 2015
*	fixes to the file / tools windows switcher  in older versions of visual studio
*	quick info tool tips are now supported. the shortcut for invoking this tool tip is ctrl + k and then ctrl + i
*	basic support for parameter info, use ctrl + shift + space to invoke this tool tip
*	error list navigation improvements:
	*	errors list now works with NVDA's commands for navigating tables: control + alt + left / right arrow. 
	*	it is possible to directly access each column with control + alt + number, where number is the number of the column you wish to access. for example: to access the first column use control + alt + 1.
*	NVDA now reports the current line when navigating the code with the debugger. (stepping in / over / out) with the corresponding keyboard commands.
*	fixes for the menus: 
	*	keyboard shortcuts are now reported for each menu item if available 
	*	availability of submenus is reported
*	tool box tool window improvements and fixes
*	in windows forms designer, moving UI elements / resizing them with the keyboard is now reported
*	using ctrl + f6 / ctrl + shift + f6 to switch between opened code editors is now reported

The add-on is still under development, so expect more fixes and enhancements.

##Fixes in more detail

*	fixes to intelliSense: unnecessary announcements when using intelliSense were removed to improve productivity. 
additionally, positional info of the suggested intelliSense items is not reported by default. EG "int 1 of 9" is now reported as "int". you can control whether to have this info from visual studio settings dialog under NVDA preferences menu.
NVDA's behavior with intelliSense is now as the following:
the focus of NVDA is usually placed in the editor, and the navigator object is the intelliSense menu item. so, you can review the last reported intelliSense item with review commands, (numpad keys on the desktop), and in the same time to type as usual in the editor and to get feedback.
*	fixes to debugging windows: NVDA now reads the content of the watch, locals,, autos and call stack windows.

##controlling the behavior of the add-on
the add-on includes a GUI dialog under NVDA preferences menu to control some settings within the add-on
settings you can control:
*	reporting breakpoints with speech: you can choose whether breakpoints should be reported with speech.
*	 beeping on breakpoints: you can choose whether NVDA should make a beep when the caret reaches a line with breakpoint.
*	reporting intelliSense position info: you can choose whether position info of the code completion items should be reported by NVDA.

##important notes

*	I forgot to add support for express versions of visual studio, so, the add-on should work with those versions of VS now... let me know if this doesn't happen for some reason.
*	I need your feedback to know which parts of the UI need further improvements, as well as feedback for the features which were already implemented.
You can reach me at: 
mohmad.s93@gmail.com
Please feel free to let me know your thoughts.
