# appModule for visual studio
#author: mohammad suliman (mohmad.s93@gmail.com)

import appModuleHandler
from NVDAObjects.UIA import UIA, WpfTextView, Toast
from NVDAObjects.behaviors import RowWithoutCellObjects, RowWithFakeNavigation
from NVDAObjects.IAccessible import IAccessible, ContentGenericClient
from NVDAObjects import NVDAObjectTextInfo
import textInfos
import controlTypes
import UIAHandler
import api
import winUser
import ui
import tones
import mouseHandler
from logHandler import log
import eventHandler
import scriptHandler
from globalCommands import SCRCAT_FOCUS
import re
import time
import speech

# some user configuration vars to control how the add-on behaves
announceIntelliSensePosInfo = False
beepOnBreakpoints = True
announceBreakpoints = True
#reportIntelliSenseDescription = True

# global vars

#whether last focused object was an intelliSense item
intelliSenseLastFocused = False

#last focused intelliSense object
lastFocusedIntelliSenseItem = None

#whether the caret has moved to a different line in the code editor 
caretMovedToDifferentLine = False

# global functions
def _isCompletionPopupShowing():
	obj = api.getForegroundObject()
	try:
		if obj.firstChild.firstChild.firstChild.next.next.role == controlTypes.ROLE_POPUPMENU:
			return True
	except Exception as e:
		pass
	# try some rescy option 
	try:
		obj1 = obj .firstChild
		obj2 = obj1.firstChild
		if obj1.role == controlTypes.ROLE_WINDOW and obj1.name == ''\
		and obj2.role == controlTypes.ROLE_WINDOW and obj2.name == '':
			return True
	except Exception as e:
		pass
	return False

def _shouldIgnoreEditorAncestorFocusEvents():
	global intelliSenseLastFocused
	return intelliSenseLastFocused == True

def _getCurIntelliSenseDescription():
	obj = api.getForegroundObject()
	try:
		obj = obj.firstChild.firstChild.firstChild
		if obj.role == controlTypes.ROLE_STATICTEXT:
			return obj
	except Exception as e:
		pass
	return None


class AppModule(appModuleHandler.AppModule):

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_TAB and isinstance(obj, UIA) and obj.UIAElement.currentClassName == "TabItem":
			clsList.insert(0, editorTabItem)
		elif obj.role == controlTypes.ROLE_TABCONTROL and isinstance(obj, UIA) and obj.UIAElement.currentClassName == "DocumentGroup":
			clsList.insert(0, editorTabControl)
		elif isinstance(obj, UIA) and obj.UIAElement.currentClassName == "IntellisenseMenuItem" and obj.role == controlTypes.ROLE_MENUITEM:
			clsList.insert(0, intelliSenseMenuItem)
		elif isinstance(obj, UIA) and obj.UIAElement.currentClassName == "MenuItem" and obj.role == controlTypes.ROLE_MENUITEM:
			clsList.insert(0, VSMenuItem)
		elif obj.name == 'Treegrid Accessibility' and obj.role == controlTypes.ROLE_WINDOW:
			clsList.insert(0, VarsTreeView)
		elif obj.name is None and obj.windowClassName == 'TREEGRID' and obj.role == controlTypes.ROLE_PANE:
			clsList.insert(0, BadVarView)
		elif isinstance(obj, UIA) and obj.UIAElement.currentClassName == "TextMarker" and obj.role == controlTypes.ROLE_UNKNOWN and obj.name.startswith("Breakpoint"):
			clsList.insert(0, VSBreakpoint)
		elif obj.name == "Text Editor" and obj.role == controlTypes.ROLE_EDITABLETEXT:
			clsList.insert(0, VSTextEditor)
		elif obj.role == controlTypes.ROLE_DATAITEM and isinstance(obj, UIA) and obj.UIAElement.currentClassName == "ListViewItem":
			clsList.insert(0, ErrorsListItem)
		elif obj.name == "Quick Info Tool Tip" and obj.role == controlTypes.ROLE_TOOLTIP:
			clsList.insert(0, QuickInfoToolTip)
		elif obj.name == "Signature Help" and obj.role == controlTypes.ROLE_UNKNOWN and isinstance(obj, UIA) and obj.UIAElement.currentClassName == "WpfSignatureHelp":
			clsList.insert(0, ParameterInfo)

	def event_NVDAObject_init(self, obj):
		if obj.name == "Active Files" and obj.role in (controlTypes.ROLE_DIALOG, controlTypes.ROLE_LIST):
			#this object reports the descktop object as its container, this causes 2 issues 
			#redundent announcement of the foreground object 
			#and losing the real foreground object which makes reporting the status bar script not reliable			
			obj.role = controlTypes.ROLE_LIST
			if obj.container.name == "Desktop":
				obj.container = api.getForegroundObject()
			#description here also is redundant, so, remove it
			obj.description = ""
		elif obj.name == "Active Tool Windows" and obj.role  == controlTypes.ROLE_LIST:
			#do the same for tool windows List
			obj.description = ""


	def event_gainFocus(self, obj, nextHandler):
		global intelliSenseLastFocused
		global lastFocusedIntelliSenseItem
		if obj.name == "Text Editor" and obj.role == controlTypes.ROLE_EDITABLETEXT:
			# in many cases, the editor fire focus events when intelliSense menu is opened, which leads to a lengthy announcements after reporting the current intelliSense item
			#so, allow the focus to return to the editor if that happens, but don't report the focus event, and set the navigator object to be last reported intelliSense item to allow the user to review
			if _isCompletionPopupShowing():
				api.setNavigatorObject(lastFocusedIntelliSenseItem)
				intelliSenseLastFocused = True
				return 
		intelliSenseLastFocused = False
		lastFocusedIntelliSenseItem = None
		nextHandler()

	def event_appModule_loseFocus(self):
		global intelliSenseLastFocused
		global lastFocusedIntelliSenseItem
		lastFocusedIntelliSenseItem		= None
		intelliSenseLastFocused = False

#almost copied from NVDA core with minor modifications
	def script_reportStatusLine(self, gesture):
		#it seems that the status bar is the last child of the forground object
		#so, get it from there
		obj = api.getForegroundObject().lastChild
		found=False
		if obj and obj.role == controlTypes.ROLE_STATUSBAR:
			text = api.getStatusBarText(obj)
			api.setNavigatorObject(obj)
			found=True
		else:
			info=api.getForegroundObject().flatReviewPosition
			if info:
				info.expand(textInfos.UNIT_STORY)
				info.collapse(True)
				info.expand(textInfos.UNIT_LINE)
				text=info.text
				info.collapse()
				api.setReviewPosition(info)
				found=True
		if not found:
			# Translators: Reported when there is no status line for the current program or window.
			ui.message(_("No status line found"))
			return
		if scriptHandler.getLastScriptRepeatCount()==0:
			ui.message(text)
		else:
			speech.speakSpelling(text)
	# Translators: Input help mode message for report status line text command.
	script_reportStatusLine.__doc__ = _("Reads the current application status bar and moves the navigator to it. If pressed twice, spells the information")
	script_reportStatusLine.category=SCRCAT_FOCUS

	def script_reportParameterInfo(self, gesture):
		# get the parameter info object
		try:
			obj = api.getForegroundObject().firstChild.firstChild
		except:
			return
		if obj.role == controlTypes.ROLE_TOOLTIP:
			# emulate an alert event for this object
			eventHandler.queueEvent("alert", obj)

	# def script_reportIntelliSensDesc(self, gesture):
		# gesture.send()
		# obj = _getCurIntelliSenseDescription()
		# if not obj:
			# return 
		# ui.message(obj.name)

#this method is only for debugging, final release won't include it
	def script_checkIfPopupCompletion(self, gesture):
		if _isCompletionPopupShowing():
			ui.message("available")
		else:
			ui.message("not available")

	__gestures = {
		"kb:Alt+c": "checkIfPopupCompletion",
		"kb:NVDA+End": "reportStatusLine",
		"kb:control+shift+space": "reportParameterInfo",
		# "kb:control+i": "reportIntelliSensDesc"
	}

class editorTabItem(UIA):
	"""
	one of the editor focus ancestors, we ignore focus entered events in some cases 
	see _shouldIgnoreEditorAncestorFocusEvents for more info
	"""

	def event_focusEntered(self):
		if _shouldIgnoreEditorAncestorFocusEvents():
			return
		return super(editorTabItem, self).event_focusEntered()

class editorTabControl(UIA):
	"""one of the editor focus ancestors, we ignore focus entered events in some cases 
	see _shouldIgnoreEditorAncestorFocusEvents for more info
	"""

	def event_focusEntered(self):
		if _shouldIgnoreEditorAncestorFocusEvents():
			return
		return super(editorTabControl, self).event_focusEntered()


cutPositionalInfo = re.compile(" \d+ of \d+$")
itemIndexExp = re.compile("^ \d+")
groupCountExp = re.compile("\d+$")

class intelliSenseMenuItem(UIA):

	def _get_states(self):
		states = set()
		#only fetch the states witch are likely to change
		e=self.UIACachedStatesElement
		try:
			hasKeyboardFocus=e.cachedHasKeyboardFocus
		except COMError:
			hasKeyboardFocus=False
		if hasKeyboardFocus:
			states.add(controlTypes.STATE_FOCUSED)
		# Don't fetch the role unless we must, but never fetch it more than once.
		role=None
		if e.getCachedPropertyValue(UIAHandler.UIA_IsSelectionItemPatternAvailablePropertyId):
			role=self.role
			states.add(controlTypes.STATE_CHECKABLE if role==controlTypes.ROLE_RADIOBUTTON else controlTypes.STATE_SELECTABLE)
			if e.getCachedPropertyValue(UIAHandler.UIA_SelectionItemIsSelectedPropertyId):
				states.add(controlTypes.STATE_CHECKED if role==controlTypes.ROLE_RADIOBUTTON else controlTypes.STATE_SELECTED)
		# those states won't change for this UI element, so add them to the states set
		states.add(controlTypes.STATE_FOCUSABLE)
		states.add(controlTypes.STATE_READONLY)
		return states

	def event_gainFocus(self):
		global intelliSenseLastFocused
		global lastFocusedIntelliSenseItem
		intelliSenseLastFocused = True
		lastFocusedIntelliSenseItem = self
		# self.description = _getCurIntelliSenseDescription()
		self.description = None
		super(intelliSenseMenuItem, self).event_gainFocus()

	def _get_name(self):
		# by default, the name of the intelliSense menu item includes the position info
		#so, remove it
		oldName = super(intelliSenseMenuItem, self).name
		newName = re.sub(cutPositionalInfo, "", oldName)
		return newName

	def _get_positionInfo(self):
		"""gets the position info of the intelliSense menu item based on the original name
		the user can turn that off by setting to false the appropriate flag
		"""
		if announceIntelliSensePosInfo == False:
			return {}
		oldName = super(intelliSenseMenuItem, self).name
		info={}
		if  cutPositionalInfo.search(oldName) is None:
			return {}
		positionalInfoStr = cutPositionalInfo.search(oldName).group()
		itemIndex = int(itemIndexExp.search(positionalInfoStr).group())
		if itemIndex>0:
			info['indexInGroup']=itemIndex
		groupCount = int(groupCountExp.search(positionalInfoStr).group())
		if groupCount>0:
			info['similarItemsInGroup'] = groupCount
		return info


#the parent view of the variables view in the locals / autos/ watch windows
class VarsTreeView(IAccessible):
	"""the parent view of the variables view in the locals / autos/ watch windows"""

	role = controlTypes.ROLE_TREEVIEW
	name = ''

	def event_focusEntered(self):
		speech.speakObject(self,reason=controlTypes.REASON_FOCUSENTERED)

# a regular expression for removing level info from the name
cutLevelInfo = re.compile(" @ tree depth \d+$")
#a regular expression for getting the level
getLevel = re.compile("\d+$")
class BadVarView(ContentGenericClient):
	"""the view that showes the variable info (name, value, type) in the locals / autos / watch windows"""

	role = controlTypes.ROLE_TREEVIEWITEM
	TextInfo=NVDAObjectTextInfo

	def _getMatchingParentChildren(self):
		parentChildren = self.parent.children
		matchingChildren = []
		for index, child in enumerate(parentChildren):
			if controlTypes.STATE_SELECTED in child.states or controlTypes.STATE_FOCUSED in child.states and not child.name.startswith("[Column"):
				matchingChildren.append(parentChildren[index + 1])
				matchingChildren.append(parentChildren[index + 2])
				if self._isCallStackWindow():
					break
				matchingChildren.append(parentChildren[index + 3])
				break
		return matchingChildren

	def _isCallStackWindow(self):
		try:
			return self.parent.parent.parent.parent.name == "Call Stack"
		except:
			return False

	def isDuplicateIAccessibleEvent(self,obj):
		if isinstance(obj, BadVarView):
			return self == obj
		return super(BadVarView, self).isDuplicateIAccessibleEvent(obj)

	def event_stateChange(self):
		return 

	def event_gainFocus(self):
		self.parent.firstChild = self
		super(BadVarView, self).event_gainFocus()

	def _get_name(self):
		matchingChildren = self._getMatchingParentChildren()
		if matchingChildren is None:
			return None
		if len(matchingChildren) < 2:
			return None
		res  = []
		for child in matchingChildren:
			name = child.name
			value = child.value
			#remove the level info 
			value = str(value)
			value = re.sub(cutLevelInfo, "", value)
			res.append(name + ": ")
			res.append(value)
			res.append(", ")
		#remove last coma 
		res.pop(-1)
		return "".join(res)

	def _get_states(self):
		superStates = super(BadVarView, self).states
		matchingChildren = self._getMatchingParentChildren()
		if matchingChildren is None:
			return superStates
		if len(matchingChildren) == 0:
			return superStates
		states = matchingChildren[0]._get_states() | superStates
		if self.name.startswith("Name: None"):
			#if this happens, then the view has no meaningful info
			states.add(controlTypes.STATE_UNAVAILABLE)
		return states

	def _isEqual(self, other):
		if not isinstance(other, BadVarView):
			return False
		return self is other

	def _get_positionInfo(self):
		# only calculate the level 
		#index in group,  similar items in group are not easy to calculate, and it won't be efficien
		matchingChildStr = self._getMatchingParentChildren().pop(0).value
		matchingChildStr = str(matchingChildStr)
		if re.search(getLevel, matchingChildStr) is None:
			return {}
		levelStr = re.search(getLevel, matchingChildStr).group()
		if not levelStr.isdigit():
			return {}
		level = int(levelStr)
		if level <= 0:
			return {}
		info = {}
		info["level"] = level
		return info

	def script_moveRight(self, gesture):
		if controlTypes.STATE_COLLAPSED in self.states:
			ui.message(_("expanded"))
		gesture.send()
		return

	def script_moveLeft(self, gesture):
		if controlTypes.STATE_EXPANDED in self.states:
			ui.message(_("collapsed"))
		gesture.send()
		return

	__gestures = {
		"kb:leftArrow": "moveLeft",
		"kb:rightArrow": "moveRight"
	}


class VSMenuItem(UIA):
	""" a class for ordinary menu items in visual studio"""

	def _get_states(self):
		states = super(VSMenuItem, self)._get_states()
		# visual studio exposes the menu item which has a sub menu as collapsed
		#remove this state and add HASPOP state to fix NVDA behavior
		if controlTypes.STATE_COLLAPSED in states:
			states.remove(controlTypes.STATE_COLLAPSED)
			states.add(controlTypes.STATE_HASPOPUP)
		#this state is redundant in this context
		states.discard(controlTypes.STATE_CHECKABLE)
		return states

getLineText = re.compile("Ln \d+")
getLineNum = re.compile("\d+$")

def _getCurLineNumber():
	"""gets current line number which has the caret in the editor based on status bar text"""
	obj = api.getForegroundObject().lastChild
	text = None
	if obj and obj.role == controlTypes.ROLE_STATUSBAR:
		text = api.getStatusBarText(obj)
	if not text:
		return 0
	lineText = re.search(getLineText, text)
	if not lineText:
		return 0
	lineText = lineText.group()
	lineNum = re.search(getLineNum, lineText)
	if not lineNum:
		return 0
	lineNum = int(lineNum.group())
	if lineNum <= 0:
		return 0
	return lineNum

getBreakpointState = re.compile("Enabled|Disabled")

class VSBreakpoint(UIA):
	"""a class for break point control to allow us to detect and report break points once the caret reaches a line with break point""" 

	def event_nameChange(self):
		global caretMovedToDifferentLine
		# return if we already announced the break point for the current line 
		if not caretMovedToDifferentLine:
			return
		caretMovedToDifferentLine = False
		currentLineNum = _getCurLineNumber()
		BPLineNum = self._getLineNumber()
		if currentLineNum == 0 or BPLineNum == 0 \
		or currentLineNum != BPLineNum:
			return
		global announceBreakpoints, beepOnbreakPoints
		if beepOnBreakpoints:
			tones.beep(1000, 50)
		if not announceBreakpoints:
			return
		global getBreakpointState
		message = _("breakpoint")
		state = re.search(getBreakpointState, self.name)
		if  state:
			message += ", " 
			message += state.group()
		ui.message(message)

	def _getLineNumber(self):
		"""gets the line number of the breakpoint """
		try:
			ret=self.UIAElement.currentAutomationID
		except Exception as e:
			return 0
		lineNum = re.search(getLineNum, ret)
		if not lineNum:
			return 0
		lineNum = int(lineNum.group())
		if lineNum <= 0:
			return 0
		return lineNum

class VSTextEditor(WpfTextView):
	"""a class for VS text editor  
	currently, we need this class to try to tell whether the caret has moved to a different line 
	this helps us to not make several announcements of the same breakpoint when moving the caret left and rite on the same line
	"""

	description = ""

	def script_caret_moveByLine(self, gesture):
		global caretMovedToDifferentLine
		caretMovedToDifferentLine = True
		super(VSTextEditor, self).script_caret_moveByLine(gesture)

splitError= re.compile("(Severity:.*)(Code:.*)(Description:.*)(Project:.*)(File:.*)(Line:.*)")
splitErrorNoCodeCol = re.compile("(Severity:.*)(Description:.*)(Project:.*)(File:.*)(Line:.*)")
splitErrorNoFileCol = re.compile("(Severity:.*)(Code:.*)(Description:.*)(Project:.*)(Line:.*)")
splitErrorNoLineCol = re.compile("(Severity:.*)(Code:.*)(Description:.*)(Project:.*)(File:.*)")
class ErrorsListItem(RowWithoutCellObjects, RowWithFakeNavigation, UIA):
	""" a class for list item of the errors list
	the goal is to enable the user to navigate each row with NVDA's commands for navigating tables (ctrl+alt+right/left arrow). in addition, it is possible to move directly to a column with ctrl + alt + number, when the number is the column number we wish to move to
	"""

	def _getColumnContent(self, column):
		text = self._getColumnContentAndHeader(column)
		# extract the content
		text = text.split(":", 1)[1]
		#remove spaces if there are any
		text = text.strip()
		return text

	def _getColumnHeader(self, column):
		text = self._getColumnContentAndHeader(column)
		# extract the header
		text = text.split(":", 2)[0]
		#remove spaces if there are any
		text = text.strip()
		return text

	def _getColumnContentAndHeader(self, column):
		global splitError, splitErrorNoCodeCol, splitErrorNoFileCol, splitErrorNoLineCol
		if column < 1 or column > 6:
			return ""
		try:
			return re.search(splitError, self.name).group(column)
		except:
			pass
		try:
			return re.search(splitErrorNoCodeCol, self.name).group(column)
		except:
			pass
		try:
			return re.search(splitErrorNoFileCol, self.name).group(column)
		except:
			pass
		try:
			return re.search(splitErrorNoLineCol, self.name).group(column)
		except:
			pass
		return ""

	def _getColumnLocation(self,column):
		if column < 1 or column > 6:
			return None
		child = None
		try:
			child = UIA._get_children(self)[column - 1].firstChild
		except Exception as e:
			log.debug(e)
		if not child:
			return None
		return child.location

	def _get_childCount(self):
		return 6

	def initOverlayClass(self):
		for i in xrange(10):
			self.bindGesture("kb:control+alt+" + str(i), "moveToColumn")

	def script_moveToColumn(self, gesture):
		keyName = gesture.displayName
		# extract the number from the key name
		columnNum = re.search("\d+$", keyName).group()
		columnNum = int(columnNum)
		if columnNum > 6 or columnNum == 0:
			#currently, up to 6 columns is supported,  hopefuly this is the max number of columns that could be in this view
			return
		self._moveToColumnNumber(columnNum)


class QuickInfoToolTip(Toast):
	""" a class for the quick info tool tip view  """

	def _get_name(self):
		return "Quick Info"

	def _get_description(self):
		# this view has a long description, don't think the user wants to hear it every tiem he invokes the quick info
		return ""

class ParameterInfo (Toast):
	role = controlTypes.ROLE_TOOLTIP

	def _get_description(self):
		return ""

