# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1037,898 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        self.notebook_modes = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        bSizer2.Add( self.notebook_modes, 0, wx.ALL|wx.EXPAND, 5 )

        gSizer4 = wx.GridSizer( 0, 2, 0, 0 )

        self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, _(u"Zusammensetzungen:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )

        gSizer4.Add( self.m_staticText8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        iterations_choiseChoices = [ wx.EmptyString ]
        self.iterations_choise = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, iterations_choiseChoices, 0 )
        self.iterations_choise.SetSelection( 0 )
        self.iterations_choise.SetMinSize( wx.Size( 100,-1 ) )

        gSizer4.Add( self.iterations_choise, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )


        bSizer2.Add( gSizer4, 0, wx.EXPAND, 5 )

        self.grid_container = wx.BoxSizer( wx.VERTICAL )


        bSizer2.Add( self.grid_container, 1, wx.EXPAND, 5 )

        bSizer10 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        self.edit_aliases_btn = wx.Button( self, wx.ID_ANY, _(u"Alias bearbeiten"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.edit_aliases_btn, 0, wx.ALL, 5 )


        bSizer10.Add( bSizer7, 1, wx.EXPAND, 5 )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        self.reset_btn = wx.Button( self, wx.ID_ANY, _(u"Zurücksetzen "), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer11.Add( self.reset_btn, 0, wx.ALL, 5 )

        self.export_csv_btn = wx.Button( self, wx.ID_ANY, _(u"Export to CSV"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer11.Add( self.export_csv_btn, 0, wx.ALL, 5 )

        self.new_iteration_btn = wx.Button( self, wx.ID_ANY, _(u"Neu Zusammensetzen"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer11.Add( self.new_iteration_btn, 0, wx.ALL, 5 )


        bSizer10.Add( bSizer11, 0, 0, 5 )


        bSizer2.Add( bSizer10, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer2 )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


