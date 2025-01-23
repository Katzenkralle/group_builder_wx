import wx.grid
import layout
import wx
from group_compositor import GroupCalculator

group_creator = GroupCalculator()
app = wx.App(False)

class GuiHandler(layout.entrypoint):
    highlighte_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
    background_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

    def __init__(self, parent):
        super().__init__(parent)
        self.combo_groups_num.Set([str(i) for i in range(2, 11)])
        self.combo_groups_csv.Set([str(i) for i in range(2, 11)])
        self.combo_members.Set([str(i) for i in range(10, 101)])
        
        self.combo_groups_num.Bind(wx.EVT_TEXT, self.on_group_change)
        self.combo_groups_csv.Bind(wx.EVT_TEXT, self.on_group_change)
        self.combo_members.Bind(wx.EVT_TEXT, self.on_member_change)

        self.combo_groups_num.Bind(wx.EVT_CHAR, self.only_allow_number)
        self.combo_groups_csv.Bind(wx.EVT_CHAR, self.only_allow_number)
        self.combo_members.Bind(wx.EVT_CHAR, self.only_allow_number)

        self.notebook_modes.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_change)

        self.new_iteration_btn.Bind(wx.EVT_BUTTON, self.on_new_iteration)

        self.combo_groups_num.SetValue("4")
        self.combo_groups_csv.SetValue("4")
        self.combo_members.SetValue("12")


        self.iterations_choise.Bind(wx.EVT_CHOICE, self.on_iteration_view_change)


        self.group_grid.SetSelectionMode(wx.grid.Grid.GridSelectNone)
        self.group_grid.SetCellHighlightPenWidth(0)
        self.group_grid.SetCellHighlightROPenWidth(0)
        self.group_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_grid_interaction)
        self.group_grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, lambda e: e.StopPropagation())

    def only_allow_number(self, event):
        """
        Allows only numeric input for age and height fields.

        Args:
            event: The key event.
        """
        key_code = event.GetKeyCode()
        # Check if the key is a number, backspace, or a control key (e.g., arrow keys)
        if key_code in range(48, 58) or key_code in [wx.WXK_BACK, wx.WXK_RETURN]:
            event.Skip()  # Allow the input
        else:
            event.StopPropagation()  # Reject the input

    def on_iteration_view_change(self, event):
        group = group_creator.get_current_group(iteration=int(event.GetString()), replace_alias=False)
        self.rerender_groups(group)

    def on_page_change(self, event):
        match event.GetSelection():
            case 0:
                self.on_group_change(None, int(self.combo_groups_num.GetValue()))
            case 1:
                self.on_group_change(None, int(self.combo_groups_csv.GetValue()))
            case  _:
                print("Invalid page. This should not happen")
    
    def on_group_change(self, event = None, n_groups = None):
        inp = n_groups if n_groups else int(event.GetString())
        group_creator.n_groups = inp

    def on_member_change(self, event):
        group_creator.n_students = int(event.GetString())

    def on_grid_interaction(self, event):
        # Get location of the cell
        match event.GetCol():
            case 0:
                row = event.GetRow()
                cell_value = self.group_grid.GetCellValue(row, 0)
                if not cell_value:
                    event.StopPropagation()
                    return
                for i in range(self.group_grid.GetNumberRows()):
                    self.group_grid.SetCellBackgroundColour(i, 0, GuiHandler.background_color)
                self.group_grid.SetCellBackgroundColour(row, 0, GuiHandler.highlighte_color)

                self.render_groupmembers(group_creator.get_current_group()[cell_value])

                event.StopPropagation()

            case 2:
                pass
            case _:
                event.Skip()

        self.Refresh()
        return
    
    def render_groupmembers(self, group):
        counter = 0
        while True:
            cell_value = self.group_grid.GetCellValue(counter, 1)
            if not cell_value:
                break
            self.group_grid.SetCellValue(counter, 1, "")
            counter += 1
        for i, member in enumerate(group):
            self.group_grid.SetCellValue(i, 1, str(member))
            self.group_grid.SetCellValue(i, 2, str(group_creator.alias.get(member, "")))
        
    def rerender_groups(self, groups):
        # Update table
        try:
            self.group_grid.DeleteRows(0, self.group_grid.GetNumberRows())
        except wx._core.wxAssertionError:
            pass
        self.group_grid.AppendRows(max([group_creator.n_students, len(groups)]))
        # First, set the groups
        for i, group in enumerate(groups):
            self.group_grid.SetCellValue(i, 0, group)
        
        self.group_grid.SetCellBackgroundColour(0, 0, GuiHandler.highlighte_color)
        self.render_groupmembers(groups[list(groups.keys())[0]])

        self.Refresh()

    def on_new_iteration(self, event):
        print(group_creator.create_groups())
        new_group = group_creator.get_current_group()
        self.iterations_choise.Set(list(map(lambda x: str(x), range(group_creator.get_iteration()+1))))
        self.iterations_choise.SetSelection(group_creator.get_iteration())
        self.rerender_groups(new_group)
        
            


if __name__ == "__main__":
    frame = GuiHandler(None)
    frame.Show(True)
    app.MainLoop()