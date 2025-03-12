# -*- coding: utf-8 -*-
""" The GUI Window to visualize progress in calculations """
# $Id: ActionWindow.py,v 1.10 2004/04/09 03:53:26 prof Exp $
import sys
if sys.version_info > (3,):
    import queue as Queue
else:
    import Queue

import time
import re
from OurTkinter         import Tk, Dialog, ScrolledText, tk_set_icon_portable
import OurMessageBox    as     MessageBox

import ProgressBarView
import ThreadsConnector
import logging
import gettext
_ = gettext.gettext

class ActionWindow( Dialog ):

  def __init__( self, parent, title, text, geometry, progressbarlabel=1, on_stop=None ):
    """ Create dialog, remember interface objects """
    # Postpone parent's init bacause it starts modal dialog immediately
    self.aw_parent  = parent
    self.aw_title   = title
    self.aw_text    = text
    self.aw_geometry    = geometry
    self.progressbarlabel = progressbarlabel
    self.log        = logging.getLogger(self.__class__.__name__)
    self.on_stop    = on_stop
    self.msg_start  = None

  def setConnector(self, conn):
    """ Remember a thread connector """
    self.conn = conn

  def setProgressBar(self, progress):
    """ Remember a progress bar controller """
    self.progress_ctrl = progress

  def go(self):
    """ Create and start dialog """
    print( 'go' )
    Dialog.__init__(self, self.aw_parent, self.aw_title)

  def wait_window(self, wnd):
    """ Customize appearence of window, setup periodic call and call parent's wait_window """
    self.fixWindowLayout()
    self.aw_alarm = self.after(100, self.periodicCheckForMessages)
    Dialog.wait_window(self, wnd)
  
  def destroy(self):
    """ Terminate periodic process and call parent's destroy """
    self.after_cancel(self.aw_alarm)
    # self.grab_release()
    Dialog.destroy(self)

  def periodicCheckForMessages(self):
    """ Check if there are new messages and dispatch them """
    try:
      while 1:
        (code, item) = self.conn.get_message()
        # print( code, item )
        if code == ThreadsConnector.MESSAGE_LOG:
          self.onLogMessage(item)
        elif code == ThreadsConnector.MESSAGE_PROGRESS:
          self.onProgress()
        elif code in (ThreadsConnector.MESSAGE_EXIT_CANCEL, ThreadsConnector.MESSAGE_EXIT_ERROR, ThreadsConnector.MESSAGE_EXIT_OK):
          self.onCalculationsExitMessage(item)
        else:
          self.log.error('Unknown ActionWindow message: %s, %s' % (code, item))
    except Queue.Empty:
      pass
    self.aw_alarm = self.after(100, self.periodicCheckForMessages)

  def onLogMessage(self, text):
    """ Display log message """
    # print( 'text=', text )
    is_error_msg = text.lower().find( 'error' ) >= 0

    w = self.logwnd
    w.configure(state=Tk.NORMAL )

    if is_error_msg:
        # reduce the index by one, e.g., 13.0 ==> 12.0
        self.msg_start = re.sub( r'(\d+).', lambda m: '%d.' % ( int( m.group(1) ) - 1 ), w.index( Tk.END ) )

    w.insert(Tk.END, text)

    if is_error_msg:
        self.msg_end = w.index( Tk.END )
        print( 'tag_add ERROR', self.msg_start, self.msg_end )
        w.tag_add( 'ERROR_MSG', self.msg_start, self.msg_end )

    w.insert(Tk.END, "\n")

    # print( 'msg_start, msg_end=', self.msg_start, self.msg_end )
    if self.msg_start is not None:
        # この ActionWindow の造りにより、
        # tag の終端が更新されるため、毎回再設定する。
        try:
            f, t = w.tag_ranges( 'ERROR_MSG' )
            w.tag_remove( 'ERROR_MSG', f, t )
            w.tag_add( 'ERROR_MSG', self.msg_start, self.msg_end )
        except Exception as exc:
            # without this catch, it seems to die.
            from ExceptionTracebacker import ExceptionTracebacker
            etb = ExceptionTracebacker()
            # ValueError: too many values to unpack (expected 2)
            print(etb.last_lines())

    # print( w.tag_ranges( 'ERROR_MSG' ) )

    w.see(Tk.END)
    w.configure(state=Tk.DISABLED)

  def onCalculationsExitMessage(self, text):
    """ Visualize that calculations are finished """
    self.status_label.configure(text=text)
    self.progress_bar.updateProgress(100,100)
    self.button_cancel.configure(state=Tk.DISABLED)
    # Cancel ボタンは無意味になるので、表示しない。
    self.button_cancel.pack_forget()
    # pack_forget() していた OK ボタンを表示する。
    self.button_ok.pack(side=Tk.LEFT, padx=5, pady=5)
    self.button_ok.configure(state=Tk.NORMAL)
    self.bind('<Escape>', self.cancel)

  def onProgress(self):
    """ Visualize progress of calculations """
    (cur, limit) = self.progress_ctrl.get()
    self.progress_bar.updateProgress(cur, limit)

  def body(self, master):
    """ Pack body of window """
    self.geometry( self.aw_geometry )
    self.packText(master)
    self.packProgressBar(master)
    self.packStatusText(master)
    self.packLogWindow(master)
    tk_set_icon_portable( self, 'synthesizer' )

  def packText(self, master):
    """ Pack text message """
    Tk.Label(master, text=self.aw_text, anchor=Tk.NW, justify=Tk.LEFT).pack(fill=Tk.X)

  def packProgressBar(self, master):
    """ Pack progress bar """
    self.progress_bar = ProgressBarView.ProgressBarView(master, doLabel=self.progressbarlabel )
    self.progress_bar.pack(fill=Tk.X)

  def packLogWindow(self, master):
    """ Pack log window """
    # self.logwnd = ScrolledText(master, width=60, height=12, state=Tk.DISABLED, font=( 'GulimChe', 10 ) )
    self.logwnd = ScrolledText(master, width=60, height=12, state=Tk.DISABLED )
    # print( 'logwnd font=', self.logwnd.cget( 'font' ) )
    self.logwnd.pack(fill=Tk.BOTH, expand=1)
    self.logwnd.tag_configure("ERROR_MSG", foreground='red' )
    self.msg_start = None
    self.msg_end = None

  def packStatusText(self, master):
    """ Pack a status text """
    self.status_label = Tk.Label(master, text=_('Task is in progress'), anchor=Tk.NW, justify=Tk.LEFT)
    self.status_label.pack(fill=Tk.X)

  def buttonbox(self):
    """ Pack buttons """
    Dialog.buttonbox(self)
    # Get buttons by accessing children of last packed frame
    (self.button_ok, self.button_cancel) = self.pack_slaves()[-1].pack_slaves()
    self.button_ok.configure(state=Tk.DISABLED)
    # disable 状態で表示が残っても混乱要因になるので、表示しない。
    self.button_ok.pack_forget()
    self.bind('<Escape>', lambda e: 'break')

  def fixWindowLayout(self):
    """ Make window content resizable, set minimal sizes of window to avoid disappearing of GUI elements """
    # [0] is a wrapping frame for the window body
    self.pack_slaves()[0].pack_configure(fill=Tk.BOTH, expand=1)
    self.update_idletasks()
    reqheight = self.winfo_reqheight()
    reqwidth  = self.button_ok.winfo_reqwidth() + self.button_cancel.winfo_reqwidth()
    self.minsize(reqwidth + 10, reqheight + 10)

  def ok(self, event=None):
    """ Handle 'ok' button. Can be called only after end of calculations """
    if not(self.conn.isRunning()):
      Dialog.ok(self)
      if self.on_stop:
        self.on_stop()

  def cancel(self, event=None):
    """ Handle 'cancel' button and window close """
    if not(self.conn.isRunning()):
      print( 'Dialog.cancel(self)' )
      Dialog.cancel(self)
      return                                               # return
    if MessageBox.askyesno(title=_('Cancelling operation'), message=_('Cancel operation?'), parent=self):
      print( 'self.conn.cancel()' )
      self.conn.cancel()

if __name__ == '__main__':
  w = ActionWindow(None, _('Calculations'), _('Counting'))
  t = ThreadsConnector.ThreadsConnector()
  w.setConnector(t)
  w.go()

