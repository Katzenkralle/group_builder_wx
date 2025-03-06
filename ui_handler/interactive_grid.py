import wx

from group_creator import GroupCalculator as group_creator
from .constants import HIGHLIGHT_COLOR, BACKGROUND_COLOR

class InteractiveGrid(wx.grid.Grid):
    """
    Constructs a grid, from the base :class:`wx.grid.Grid`, that allows the user to interact with the data 
    and that is specifically designed to display the group composition.
    The grid is read-only by default, but the user can edit the alias of the members by clicking on the cell.
    The user can change the displayed group by clicking on the group name cell, the current selection will be highlighted.

    The following events are bound:
        - :const:`wx.grid.EVT_GRID_LABEL_LEFT_CLICK`, :const:`wx.grid.EVT_GRID_CELL_LEFT_DCLICK` -> Stops the propagation of the event.
        - :const:`wx.grid.EVT_GRID_CELL_LEFT_CLICK` -> :meth:`on_grid_interaction`
        - :const:`wx.grid.EVT_GRID_CELL_CHANGED` -> :meth:`on_grid_value_change`
    """
    

    def __init__(self, parent, id = None, pos = None, size = None, style = None):
        """
        Construct discribed grid with the given parent widget and default values.

        :param parent: The parent window for this handler.
        :type parent: wx.Window
        :param id: The identifier for the grid - Defaul None.
        :type id: int | None
        :param pos: The position of the grid - Default None.
        :type pos: wx.Point | None
        :param size: The size of the grid - Default None.
        :type size: wx.Size | None
        :param style: The style of the grid - Default None.
        :type style: int | None
        """
        super().__init__(parent, id, pos, size, style)
        # Grid general
        self.CreateGrid( 0, 3 )
        self.EnableGridLines( True )
        self.EnableDragGridSize( False )
        self.SetMargins( 0, 0 )

        self.EnableEditing(True)
        self.SetSelectionMode(wx.grid.Grid.GridSelectNone)
        self.SetCellHighlightPenWidth(0)
        self.SetCellHighlightROPenWidth(0)

        # Columns
        self.SetColSize( 0, 160 )
        self.SetColSize( 1, 160 )
        self.SetColSize( 2, 400 )
        self.EnableGridLines( True )
        self.EnableDragColMove( False )
        self.EnableDragColSize( True )
        self.SetColLabelValue( 0, u"Gruppen")
        self.SetColLabelValue( 1, u"Mitglieder")
        self.SetColLabelValue( 2, u"Alias")
        self.SetColLabelSize( 40 )
        self.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.EnableDragRowSize( False )
        self.SetRowLabelSize( 1 )
        self.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_BOTTOM )

        # Cell Defaults
        self.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_TOP )
        self.DisableDragRowSize()
        self.DisableDragColSize()

        # Interactivity
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_grid_interaction)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, lambda e: e.StopPropagation())
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, lambda e: e.StopPropagation())
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_grid_value_change)

    
    def on_grid_interaction(self, event):
        """
        Depending on the position of the click, the method will change the displayed group, 
        allow the user to edit the alias of a member or ignore the event.
        If the event is ignored, it will be propagated.

        :param event: The event that triggered the interaction.
        :type event: wx.grid.GridEvent

        :return: None
        """
        # Get location of the cell
        row = event.GetRow()
        match event.GetCol():
            case 0:
                cell_value = self.GetCellValue(row, 0)
                if not cell_value:
                    event.StopPropagation()
                    return
                for i in range(self.GetNumberRows()):
                    self.SetCellBackgroundColour(i, 0, BACKGROUND_COLOR)
                self.SetCellBackgroundColour(row, 0, HIGHLIGHT_COLOR)
                self.render_groupmembers(group_creator().get_current_group()[cell_value])

                event.StopPropagation()
                self.Refresh()
                return
            case 2:
                self.SetGridCursor(row, 2)
                try:
                    self.EnableCellEditControl(True)
                    event.StopPropagation()
                    return
                except wx._core.wxAssertionError:
                    pass
            case _:
                pass
        event.Skip()
        return
    
    def on_grid_value_change(self, event):
        """
        Update the alias of a member in the group_creator object when the user changes the value of a cell
        that is in the alias column and currently used in the group.

        :param event: The event that triggered the value change.
        :type event: wx.grid.GridEvent

        :return: None
        """
        row = event.GetRow()
        col = event.GetCol()
        member = self.GetCellValue(row, 1)
        if col == 2 and member:
            group_creator().alias[int(member)] = self.GetCellValue(row, 2)
        event.Skip()
        return
    
    def render_groupmembers(self, group):
        """
        Renders the members of the group in the grid.
        IDs are displayed in the second column and the alias in the third column.
        It will clear the grid before rendering the new group to clear old data/states.

        :param group: The group to render.
        :type group: dict{str: list[int]}

        :return: None
        """
        counter = 0
        while True:
            cell_value = self.GetCellValue(counter, 1)
            if not cell_value:
                break
            self.SetCellValue(counter, 1, "")
            counter += 1
        last_i = 0
        for i, member in enumerate(group):
            self.SetCellValue(i, 1, str(member))
            self.SetCellValue(i, 2, str(group_creator().alias.get(member, "")))
            self.SetCellEditor(i, 2, wx.grid.GridCellTextEditor())
            self.SetReadOnly(i, 2, False)
            last_i = i
        for i in range(last_i+1, self.GetNumberRows()):
            self.SetCellValue(i, 1, "")
            self.SetCellValue(i, 2, "")
            self.SetReadOnly(i, 2, True)

    def rerender_groups(self, groups):
        """
        Renders the selectable groupnames in the first column and triggers :meth:`render_groupmembers`.
        Also highlights the first group in the list if its name is not empty.

        :param groups: The groups to render.
        :type groups: dict{str: list[int]}

        :return: None
        """
        try:
            self.DeleteRows(0, self.GetNumberRows())
        except wx._core.wxAssertionError:
            pass
        n_rows = max([group_creator().n_members, len(groups)])
        self.AppendRows(n_rows)
        for i in range(n_rows):
            self.SetReadOnly(i, 0, True)
            self.SetReadOnly(i, 1, True)
            self.SetReadOnly(i, 2, True)
        # First, set the groups
        for i, group in enumerate(groups):
            self.SetCellValue(i, 0, group)
        
        if "" not in groups:
            # this is the case when the alias editing is active
            self.SetCellBackgroundColour(0, 0, HIGHLIGHT_COLOR)
        self.render_groupmembers(groups[list(groups.keys())[0]])

        self.Refresh()
