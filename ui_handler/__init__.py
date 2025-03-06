import wx
if 'app' not in globals():
    # Needet to allow imports from files other than main.py
    app = wx.App(False)

from .main_frame import MainFrameHandler