import wx
import addonHandler
import config
import gui
import gui.guiHelper
import globalPluginHandler
from scriptHandler import script
from logHandler import log
from gettext import gettext as _

addonHandler.initTranslation()

class MorseSynthConfigDialog(wx.Dialog):
	def __init__(self, parent=None):
		super().__init__(parent, title=_("Morsecode-Synthesizer"), style=wx.DEFAULT_DIALOG_STYLE)
		
		# Abschnitt anlegen, falls nicht vorhanden
		if "morseSynth" not in config.conf:
			config.conf["morseSynth"] = {}
		self._settings = config.conf["morseSynth"]
		wpm = int(self._settings.get('wpm', 15))
		freq = int(self._settings.get('freq', 440))
		farnsworth = self._settings.get('farnsworth', 1.0)
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		
		# Geschwindigkeit (WPM)
		self.wpmEdit = sHelper.addLabeledControl(_("WPM:"), wx.SpinCtrl, min=5, max=60)
		self.wpmEdit.SetValue(wpm)
		
		# Tonhöhe (Hz)
		self.freqEdit = sHelper.addLabeledControl(_("Freq (Hz):"), wx.SpinCtrl, min=200, max=2000)
		self.freqEdit.SetValue(freq)
		
		# Farnsworth-Faktor
		self.farnsworthEdit = sHelper.addLabeledControl(_("Farnsworth:"), wx.SpinCtrlDouble, min=0.5, max=3.0, inc=0.1)
		self.farnsworthEdit.SetDigits(1)
		self.farnsworthEdit.SetValue(farnsworth)
		
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizer(mainSizer)
		mainSizer.Fit(self)
		self.CentreOnScreen()

	def save(self):
		try:
			self._settings['wpm'] = self.wpmEdit.GetValue()
			self._settings['freq'] = self.freqEdit.GetValue()
			self._settings['farnsworth'] = self.farnsworthEdit.GetValue()
			config.conf.save()  # Einstellungen dauerhaft speichern
		except Exception as e:
			log.error(f"Fehler beim Speichern der MorseSynth-Einstellungen: {e}")

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	@script(
			description=_("Öffnet die Einstellungen für den Morsecode-Synthesizer."),
			gestures=["kb(desktop):NVDA+shift+m","kb(laptop):NVDA+windows+m"],
			category="Morse Synthesizer" 
	)
	def script_openMorseSynthConfig(self, gesture):
		def show():
			dlg = MorseSynthConfigDialog(gui.mainFrame)
			if dlg.ShowModal() == wx.ID_OK:
				dlg.save()
			dlg.Destroy()
		wx.CallAfter(show)