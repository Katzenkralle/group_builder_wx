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
## Class NumInput
###########################################################################

class NumInput ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, _(u"Wähle die Gruppenkonstilation aus:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )

        gSizer1.Add( self.m_staticText7, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_staticText81 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText81.Wrap( -1 )

        gSizer1.Add( self.m_staticText81, 0, wx.ALL, 5 )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Anzahl Gruppen:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )

        gSizer1.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        combo_groupsChoices = []
        self.combo_groups = wx.ComboBox( self, wx.ID_ANY, _(u"2"), wx.DefaultPosition, wx.DefaultSize, combo_groupsChoices, 0 )
        gSizer1.Add( self.combo_groups, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"Zu verteilende Mitglieder:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )

        gSizer1.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        combo_membersChoices = []
        self.combo_members = wx.ComboBox( self, wx.ID_ANY, _(u"10"), wx.DefaultPosition, wx.DefaultSize, combo_membersChoices, 0 )
        gSizer1.Add( self.combo_members, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )


        bSizer3.Add( gSizer1, 1, 0, 5 )


        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )

    def __del__( self ):
        pass


