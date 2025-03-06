import wx

class ForceRerender(wx.PyCommandEvent):
    """
    Custom event to force the UI to rerender.
    This event can be used to trigger a rerender of the UI components in a wxPython application.
    
    :param evtType: The type of the event.
    :type evtType: int
    :param id: The identifier of the event.
    :type id: int    
    """
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)


class RedirectText:
    """
    Redirects the output of the `sys.stdout` to a given `wx.TextCtrl`.
    """
    def __init__(self, text_ctrl):
        """
        Initializes the redirector with the given `wx.TextCtrl`.
        
        :param text_ctrl: The text control to redirect the output to.
        :type text_ctrl: wx.TextCtrl

        :return: None
        """
        self.out = text_ctrl

    def write(self, string):
        """
        Writes the given string to the `wx.TextCtrl`.
        If the string is "clear" the `wx.TextCtrl` will be cleared.

        :param string: The string to write.
        :type string: str

        :return: None
        """
        if string == "clear":
            wx.CallAfter(self.out.Clear)
            return
        if string == "\n":
            return
        wx.CallAfter(self.out.AppendText, f"{string.replace("\n", "")}\n")

    def flush(self):
        """
        Dummy methode. Required for compatibility with `sys.stdout`.
        """
        pass

