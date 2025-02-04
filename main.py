import wx

def start_app():
    """
    Initializes and starts the main application frame.
    This function imports the MainFrameHandler from the ui_handler module,
    creates an instance of MainFrameHandler, shows the frame, and starts
    the application's main loop.

    *Note: the app object is a global variable that is defined in the main module. If executed as main.*
    
    :return: None
    """
    from ui_handler import MainFrameHandler
    frame = MainFrameHandler(None)
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    app = wx.App(False)
    start_app()
