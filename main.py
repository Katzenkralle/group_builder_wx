import wx
import sys

def start_app():
    """
    Initializes and starts the main application frame.
    This function imports the :class:`ui_handler.main_frame.MainFrameHandler`, creates an instance of it
    and attaches it to the main application frame. 
    Then the application's main loop is entered.
    The App will imeediately exit with code 1 if the Python version is less than 3.12.

    *Note: the app object is a global variable that is defined in the main module. If executed as main.*

    
    :return: None
    """
    from ui_handler import MainFrameHandler
    frame = MainFrameHandler(None)
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    if sys.version_info < (3, 12):
        print("Please use Python 3.12 or newer.")
        exit(1)

    app = wx.App(False)
    start_app()
