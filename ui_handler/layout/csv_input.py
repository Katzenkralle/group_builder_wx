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
## Class CsvInput
###########################################################################

class CsvInput ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        gSizer2 = wx.GridSizer( 0, 2, 0, 0 )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"Wählen eine CSV Datei aus:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )

        gSizer2.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.csv_filepicker = wx.FilePickerCtrl( self, wx.ID_ANY, u"/home/someone/test.csv", _(u"Select a CSV file"), _(u"*.csv;*.CSV"), wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
        self.csv_filepicker.SetMinSize( wx.Size( 250,-1 ) )

        gSizer2.Add( self.csv_filepicker, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Spalte der Mitglieder:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )

        gSizer2.Add( self.m_staticText5, 0, wx.ALL, 5 )

        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        members_header_csvChoices = []
        self.members_header_csv = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, members_header_csvChoices, 0 )
        self.members_header_csv.SetSelection( 0 )
        self.members_header_csv.SetMinSize( wx.Size( 250,-1 ) )

        bSizer8.Add( self.members_header_csv, 0, wx.ALL, 5 )

        members_header_csv_subChoices = []
        self.members_header_csv_sub = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, members_header_csv_subChoices, 0 )
        self.members_header_csv_sub.SetSelection( 0 )
        self.members_header_csv_sub.SetMinSize( wx.Size( 250,-1 ) )

        bSizer8.Add( self.members_header_csv_sub, 0, wx.ALL, 5 )


        gSizer2.Add( bSizer8, 1, wx.ALIGN_RIGHT|wx.EXPAND, 5 )

        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, _(u"Gewünschte Gruppenanzahl:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )

        gSizer2.Add( self.m_staticText6, 0, wx.ALL, 5 )

        combo_groupsChoices = []
        self.combo_groups = wx.ComboBox( self, wx.ID_ANY, _(u"2"), wx.DefaultPosition, wx.DefaultSize, combo_groupsChoices, 0 )
        self.combo_groups.SetMinSize( wx.Size( 250,-1 ) )

        gSizer2.Add( self.combo_groups, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


        bSizer6.Add( gSizer2, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer6 )
        self.Layout()
        bSizer6.Fit( self )

    def __del__( self ):
        pass


