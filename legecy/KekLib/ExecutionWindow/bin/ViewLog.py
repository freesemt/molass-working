""" View Log """
# $Id: ViewLog.py,v 1.2 2004/04/12 04:38:58 prof Exp $
from OurTkinter     import Tk, Dialog, ScrolledText
import OurMessageBox    as MessageBox

import gettext
_ = gettext.gettext

class ViewLog( Dialog ):
  """ Display log messages of a program """

  def __init__(self, parent, log):
    """ Create and display window. Log is CumulativeLogger. """
    self.log = log
    tkSimpleDialog.Dialog.__init__(self, parent, _('Log Entries'))

  def body(self, master):
    """ Create dialog body """
    master.pack_configure(fill=Tk.BOTH, expand=1)
    t = ScrolledText(master, width=60, height=37)
    t.insert(Tk.END, self.log.getText())
    t.configure(state=Tk.DISABLED)
    t.see(Tk.END)
    t.pack(fill=Tk.BOTH)

  def buttonbox(self):
    """ Create custom buttons """
    w = Tk.Button(self, text=_('Close'), width=10, command=self.ok, default=Tk.ACTIVE)
    w.pack(side=Tk.RIGHT)
    self.bind("<Return>", self.ok)
    self.bind("<Escape>", self.cancel)

if __name__ == '__main__':
  #
  # Create log entries
  #
  import CumulativeLogger
  import logging
  logging.basicConfig()
  l = logging.getLogger()
  l.setLevel(logging.INFO)
  cl = CumulativeLogger.CumulativeLogger()
  for i in range(100):
    l.info('log entry %i' % i)
  #
  # Create GUI
  #
  root = Tk.Tk()
  ViewLog(root, cl)
