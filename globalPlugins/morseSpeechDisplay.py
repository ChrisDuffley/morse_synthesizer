import wx
import gui
import gui.guiHelper
import addonHandler
import globalPluginHandler
from scriptHandler import script
from logHandler import log
from gettext import gettext as _
import wx.adv

addonHandler.initTranslation()

MORSE_CODE_DICT = {
	'A': '.-',     'Ä': '.-.-',  'B': '-...',  'C': '-.-.',  'D': '-..',
	'E': '.',      'É': '..-..', 'F': '..-.',  'G': '--.',   'H': '....',
	'I': '..',     'J': '.---',  'K': '-.-',   'L': '.-..',  'M': '--',
	'N': '-.',     'O': '---',   'Ö': '---.',  'P': '.--.',  'Q': '--.-',
	'R': '.-.',    'S': '...',   'ß': '...--..','T': '-',    'U': '..-',
	'Ü': '..--',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
	'Z': '--..',
	'0': '-----',  '1': '.----', '2': '..---', '3': '...--', '4': '....-',
	'5': '.....',  '6': '-....', '7': '--...', '8': '---..', '9': '----.',
	'.': '.-.-.-', ',': '--..--', ':': '---...', '?': '..--..', "'": '.----.',
	'-': '-....-', '/': '-..-.',  '(': '-.--.',  ')': '-.--.-', '"': '.-..-.',
	'=': '-...-',  '+': '.-.-.',  '@': '.--.-.', '!': '-.-.--', '&': '.-...',
	';': '-.-.-.', '_': '..--.-', '$': '...-..-', '¿': '..-.-', '¡': '--...-',
	' ': '',
	'á': '.--.-',  'à': '.--.-', 'ä': '.-.-',  'å': '.--.-', 'ç': '-.-..',
	'é': '..-..',  'è': '.-..-', 'ð': '..--.', 'ñ': '--.--', 'ö': '---.',
	'ø': '---.',   'ś': '...-...', 'š': '----', 'ü': '..--', 'þ': '.--..',
	'ß': '...--..', '¿': '..-.-', '¡': '--...-'
}
for c in list(MORSE_CODE_DICT):
	if len(c) == 1 and c.isalpha() and c.isupper():
		lower = c.lower()
		if lower not in MORSE_CODE_DICT:
			MORSE_CODE_DICT[lower] = MORSE_CODE_DICT[c]

def textToMorse(text):
	morseWords = []
	for word in text.split(' '):
		morseChars = []
		for char in word:
			code = MORSE_CODE_DICT.get(char, '?')
			morseChars.append(code)
		if morseChars:
			morseWords.append(' '.join(morseChars))
	return '   '.join(morseWords)

class MorseSpeechDisplayDialog(wx.Dialog):
	def __init__(self, morseText, originalText, parent=None):
		super().__init__(
				parent, title=_("Clipboard Morsecode"),
				style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
		)
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		
		# Clipboard Text
		sHelper.addItem(wx.StaticText(self, label=_("Clipboard Text:")))
		self.origTextCtrl = wx.TextCtrl(
				self, value=originalText, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
		)
		self.origTextCtrl.SetMinSize((500, 80))
		sHelper.addItem(self.origTextCtrl, flag=wx.EXPAND)
		
		# Morsecode
		sHelper.addItem(wx.StaticText(self, label=_("Morsecode:")))
		self.textCtrl = wx.TextCtrl(
				self, value=morseText, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
		)
		self.textCtrl.SetMinSize((500, 120))
		sHelper.addItem(self.textCtrl, flag=wx.EXPAND, proportion=1)
		
		# Buttons
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		copyBtn = bHelper.addButton(self, label=_("Morsecode in Zwischenablage kopieren"))
		copyBtn.Bind(wx.EVT_BUTTON, self.onCopy)
		bHelper.sizer.AddStretchSpacer()
		closeBtn = bHelper.addButton(self, wx.ID_OK, _("Schließen"))
		sHelper.addItem(bHelper)
		
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL, proportion=1)
		self.SetSizer(mainSizer)
		mainSizer.Fit(self)
		self.CentreOnScreen()

	def onCopy(self, evt):
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(wx.TextDataObject(self.textCtrl.GetValue()))
			wx.TheClipboard.Close()
			wx.adv.NotificationMessage(_("Morsecode kopiert"), _("Der Morsecode wurde in die Zwischenablage kopiert.")).Show(timeout=wx.adv.NotificationMessage.Timeout_Auto)
		else:
			wx.MessageBox(_("Konnte die Zwischenablage nicht öffnen."), _("Fehler"), wx.ICON_ERROR)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	@script(
			description=_("Zeigt den aktuellen Text der Zwischenablage als Morsecode an."),
			gestures=["kb(desktop):NVDA+shift+n", "kb(laptop):NVDA+windows+n"],
			category="Morse Synthesizer"
	)
	def script_showClipboardAsMorse(self, gesture):
		def show():
			clipboardText = ""
			if wx.TheClipboard.Open():
				if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
					data = wx.TextDataObject()
					wx.TheClipboard.GetData(data)
					clipboardText = data.GetText()
				wx.TheClipboard.Close()
			clipboardText = clipboardText.strip()
			if not clipboardText:
				clipboardText = _("Kein Text in der Zwischenablage gefunden. Bitte kopiere erst Text in die Zwischenablage.")
				morseText = ""
			else:
				morseText = textToMorse(clipboardText)
			dlg = MorseSpeechDisplayDialog(morseText, clipboardText, gui.mainFrame)
			dlg.ShowModal()
			dlg.Destroy()
		wx.CallAfter(show)