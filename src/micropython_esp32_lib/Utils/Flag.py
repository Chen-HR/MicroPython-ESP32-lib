"""
# file: ./Utils/Flag.py
"""

try:
  from ..Utils import ListenerHandler
except ImportError:
  from micropython_esp32_lib.Utils import ListenerHandler

class Flag:
  pass

class BooleanFlag(Flag):
  def __init__(self):
    self.flag = False
  def activate(self) -> None:
    self.flag = True
  def deactivate(self) -> None:
    self.flag = False
  def isActivate(self) -> bool:
    return self.flag

class BooleanFlagListener(ListenerHandler.SyncListener):
  def __init__(self, flag: BooleanFlag):
    self.flag = flag
  @property
  def obj(self):
    return self.flag
  def listen(self, obj = None, *args, **kwargs) -> bool:
    return self.flag.isActivate()
