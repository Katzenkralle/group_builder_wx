import wx.grid
import layout.main_frame as main_frame
import layout.csv_input as csv_input
import layout.num_input as num_input
import wx
from wx.lib.mixins.grid import GridAutoEditMixin
import group_compositor

group_creator = group_compositor.GroupCalculator()
app = wx.App(False)

GROUPS_INITIAL_VALUE = 4
MEMBERS_INITIAL_VALUE = 12

HIGHLIGHT_COLOR = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
BACKGROUND_COLOR = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)


EVT_FORCE_RERENDER = wx.NewEventType()
EVT_FORCE_RERENDER_BINDER = wx.PyEventBinder(EVT_FORCE_RERENDER)

class ForceRerender(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)



class InpUtilsMixin:
    def on_group_composition_value_change(self, target: str, value = None):
        try:
            value = int(value)
        except ValueError:
            value = None
        match target:
            case "group":
                group_creator.n_groups = value
            case "member":
                group_creator.n_students = value
            case None:
                pass
        return
    
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

class NumInpHandler(num_input.NumInput, InpUtilsMixin):
    def __init__(self, parent):
        super().__init__(parent)
        self.combo_members.Set([str(i) for i in range(4, 30)])
        self.combo_members.Bind(wx.EVT_TEXT, self.on_change_members)
        #self.combo_members.Bind(wx.EVT_TEXT, lambda e: self.combo_groups.Set([str(i) for i in range(2, int(e.GetString())//2)]))
        self.combo_members.Bind(wx.EVT_CHAR, self.only_allow_number)
        self.combo_members.SetValue(str(MEMBERS_INITIAL_VALUE))

        
        self.combo_groups.Bind(wx.EVT_TEXT, lambda e: self.on_group_composition_value_change("group", e.GetString()))
        self.combo_groups.Bind(wx.EVT_CHAR, self.only_allow_number)
        self.combo_groups.SetValue(str(GROUPS_INITIAL_VALUE))


    def on_change_members(self, event):
        self.on_group_composition_value_change("member", event.GetString())
        self.combo_groups.Set([str(i) for i in range(2, group_creator.n_students//2)])
        self.combo_groups.SetValue(str(group_creator.n_students//4))

    def Enable(self, enable=True):
        self.combo_groups.Enable(enable)
        self.combo_members.Enable(enable)

    def on_activation(self):
        self.on_group_composition_value_change("member", int(self.combo_members.GetValue()))
        self.on_group_composition_value_change("group", int(self.combo_groups.GetValue()))

class CsvInpHandler(csv_input.CsvInput, InpUtilsMixin):
    def __init__(self, parent):
        super().__init__(parent)
        self.combo_groups.Set([str(i) for i in range(2, 11)])
        self.combo_groups.Bind(wx.EVT_TEXT, lambda e: self.on_group_composition_value_change("group", e.GetString()))
        self.combo_groups.Bind(wx.EVT_CHAR, self.only_allow_number)
        self.combo_groups.SetValue(str(GROUPS_INITIAL_VALUE))

        self.csv_filepicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_csv_fileselect)
        self.members_header_csv.Bind(wx.EVT_CHOICE, self.on_header_selection_change)
        self.members_header_csv_sub.Bind(wx.EVT_CHOICE, self.on_header_selection_change)
    
    def on_activation(self):
        group_creator.n_students = None
        self.on_group_composition_value_change("group", int(self.combo_groups.GetValue()))
        try:
            self.on_header_selection_change(None, trigger_rerender=False)
        except ValueError:
            pass
    
    def Enable(self, enable=True):
        self.combo_groups.Enable(enable)
        self.csv_filepicker.Enable(enable)
        self.members_header_csv.Enable(enable)
        self.members_header_csv_sub.Enable(enable)

    def on_header_selection_change(self, _, trigger_rerender = True):
        group_creator.select_from_csv_file([self.members_header_csv.GetStringSelection(), self.members_header_csv_sub.GetStringSelection()])
        if trigger_rerender:
            wx.PostEvent(self.GetParent(), ForceRerender(EVT_FORCE_RERENDER, self.GetId()))

    def on_csv_fileselect(self, event):
        headers = group_creator.read_csv_columns(event.GetPath())
        self.members_header_csv.Set(headers)
        self.members_header_csv.SetSelection(0)
        self.members_header_csv_sub.Set([""] + headers)
        self.members_header_csv_sub.SetSelection(0)
        # Must trigger mannually, because the event is not triggered by the SetSelection method
        self.on_header_selection_change(None, trigger_rerender=False)
        self.combo_groups.Set([str(i) for i in range(2, group_creator.n_students//2)])
        self.combo_groups.Set([str(i) for i in range(2, group_creator.n_students//2)])
        self.combo_groups.SetValue(str(group_creator.n_students//4))
        wx.PostEvent(self.GetParent(), ForceRerender(EVT_FORCE_RERENDER, self.GetId()))


class InteractiveGrid(wx.grid.Grid):
    def __init__(self, parent, id = None, pos = None, size = None, style = None):
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
        self.SetColSize( 2, 300 )
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

        # Interactivity
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_grid_interaction)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, lambda e: e.StopPropagation())
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, lambda e: e.StopPropagation())
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_grid_value_change)

    
    def on_grid_interaction(self, event):
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
                self.render_groupmembers(group_creator.get_current_group()[cell_value])

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
        row = event.GetRow()
        col = event.GetCol()
        member = self.GetCellValue(row, 1)
        if col == 2 and member:
            group_creator.alias[int(member)] = self.GetCellValue(row, 2)
        event.Skip()
        return
    
    def render_groupmembers(self, group):
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
            self.SetCellValue(i, 2, str(group_creator.alias.get(member, "")))
            self.SetCellEditor(i, 2, wx.grid.GridCellTextEditor())
            self.SetReadOnly(i, 2, False)
            last_i = i
        for i in range(last_i+1, self.GetNumberRows()):
            self.SetCellValue(i, 1, "")
            self.SetCellValue(i, 2, "")
            self.SetReadOnly(i, 2, True)

    def rerender_groups(self, groups):
        # Update table
        try:
            self.DeleteRows(0, self.GetNumberRows())
        except wx._core.wxAssertionError:
            pass
        n_rows = max([group_creator.n_students, len(groups)])
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


class MainFrameHandler(main_frame.MainFrame):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.InpNum = NumInpHandler(self.notebook_modes)
        self.InpCsv = CsvInpHandler(self.notebook_modes)
        self.notebook_modes.AddPage(self.InpNum, "Mittels Eingabe", select=True)
        self.notebook_modes.AddPage(self.InpCsv, "Mittels CSV-Datei")

        self.notebook_modes.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_change)

        self.edit_aliases_btn.Bind(wx.EVT_BUTTON, self.on_edit_aliases)
        self.new_iteration_btn.Bind(wx.EVT_BUTTON, self.on_new_iteration)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.reset_state)
        self.export_csv_btn.Bind(wx.EVT_BUTTON, self.on_export_csv)

        self.iterations_choise.Bind(wx.EVT_CHOICE, self.on_iteration_view_change)
        
        self.group_grid = InteractiveGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.grid_container.Add( self.group_grid, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.notebook_modes.Bind(EVT_FORCE_RERENDER_BINDER, self.rerender_or_create)

        self.on_new_iteration(None)

    def check_pair_repetition_warning(self):
        if int(self.iterations_choise.GetSelection()) >= group_creator.pair_repetition_brakepoinnt:
            self.pair_repetition_warning.SetLabel("Achtung: Wiederholung von Paaren")
        else:
            self.pair_repetition_warning.SetLabel("")

    def reset_state(self, _, generate_new = True):
        group_creator.reset_groups()
        group_creator.alias = {}
        if self.notebook_modes.GetSelection() == 1:
            try:
                group_creator.select_from_csv_file([self.InpCsv.members_header_csv.GetStringSelection(),
                                                     self.InpCsv.members_header_csv_sub.GetStringSelection()])
            except ValueError:
                pass
        if generate_new:
            self.on_new_iteration(None)

    def reset_view(self):
        try:
            self.group_grid.DeleteRows(0, self.group_grid.GetNumberRows())
            self.iterations_choise.Set([])
        except:
            pass

    def rerender_or_create(self, _):
        iter_choise = self.iterations_choise.GetSelection()
        if iter_choise != wx.NOT_FOUND:
            self.group_grid.rerender_groups(group_creator.get_current_group(iter_choise))
        else:
            self.on_new_iteration(None)

    def on_iteration_view_change(self, event):
        group = group_creator.get_current_group(iteration=int(event.GetString()), replace_alias=False)
        self.check_pair_repetition_warning()
        self.group_grid.rerender_groups(group)

    def on_page_change(self, event):
        self.reset_state(None, generate_new=False)
        match event.GetSelection():
            case 0:
                self.InpNum.on_activation()
            case 1:
                self.InpCsv.on_activation()
            case  _:
                print("Invalid page. This should not happen")
        #self.reset_view()
        if group_creator.n_groups and group_creator.n_students:
            self.on_new_iteration(None)
        else:
            self.reset_view()

    def on_new_iteration(self, _):
        try:
            print(group_creator.create_groups())
        except ValueError:
            if self.notebook_modes.GetSelection() == 0:
                wx.MessageBox("Ungültig Gruppenkomposition.", "Error", wx.OK | wx.ICON_ERROR)
            else:
                self.reset_view()
            return
        except group_compositor.InvalideGroupSize as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            return
        new_group = group_creator.get_current_group()
        self.iterations_choise.Set(list(map(lambda x: str(x), range(group_creator.get_iteration()+1))))
        self.iterations_choise.SetSelection(group_creator.get_iteration())
        self.check_pair_repetition_warning()
        self.group_grid.rerender_groups(new_group)
        
    def on_edit_aliases(self, _):
        if self.iterations_choise.GetSelection() == wx.NOT_FOUND:
            wx.MessageBox("Keine zu bearbeitenden Gruppen vorhanden.", "Error", wx.OK | wx.ICON_ERROR)
            return
        ui_enabled = True
        if self.edit_aliases_btn.GetLabel() == "Alias bearbeiten":
            self.edit_aliases_btn.SetLabel("Fertig")
            curent_group = group_creator.get_current_group(self.iterations_choise.GetSelection())
            acumulated_members = []
            for group in curent_group:
                for member in curent_group[group]:
                    acumulated_members.append(member)
            acumulated_members  = list(sorted(acumulated_members))
            self.group_grid.rerender_groups({"": acumulated_members})
            ui_enabled = False
        else:
            self.edit_aliases_btn.SetLabel("Alias bearbeiten")
            self.group_grid.rerender_groups(group_creator.get_current_group(self.iterations_choise.GetSelection()))
        self.InpNum.Enable(ui_enabled)
        self.InpCsv.Enable(ui_enabled)
        self.notebook_modes.Enable(ui_enabled)
        self.new_iteration_btn.Enable(ui_enabled)
        self.reset_btn.Enable(ui_enabled)
        self.export_csv_btn.Enable(ui_enabled)
        self.iterations_choise.Enable(ui_enabled)

    def on_export_csv(self, event):
        if not group_creator.get_current_group():
            wx.MessageBox("No groups to export.", "Error", wx.OK | wx.ICON_ERROR)
            return
        exit_code = wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv", defaultFile="GroupeExport.csv" ,style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if exit_code.ShowModal() == wx.ID_CANCEL:
            return
        path = exit_code.GetPath()
        try:
            group_creator.export_group_as_csv(group_creator.get_iteration(), path)
        except:
            wx.MessageBox("An error occurred while exporting the CSV file.", "Error", wx.OK | wx.ICON_ERROR)

if __name__ == "__main__":
    frame = MainFrameHandler(None)
    frame.Show(True)
    app.MainLoop()