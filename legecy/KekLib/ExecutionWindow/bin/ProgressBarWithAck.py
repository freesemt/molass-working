""" Progress bar controller for a long calculations """
# $Id: ProgressBarWithAck.py,v 1.1 2004/04/07 06:21:00 prof Exp $
import ThreadsConnector

class ProgressBarWithAck:

  def __init__(self, conn):
    """ Create progress bar controller, remember connector """
    self.conn  = conn
    self.cur   = 0
    self.limit = 100

  def set(self, cur, limit):
    """ Initialize current position and maximal value """
    self.cur   = cur
    self.limit = limit
    self.notify()

  def get(self):
    """ Get current and maximal positions """
    return (self.cur, self.limit)

  def tick(self):
    """ Increment current position """
    self.cur = self.cur + 1
    self.notify()

  def notify(self):
    """ Notify GUI widget on change. Check if thread should be finished. """
    self.conn.put_message([ThreadsConnector.MESSAGE_PROGRESS, None])
    self.conn.ack()

