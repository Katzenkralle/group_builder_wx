import wx.grid
from layout import main_frame, num_input, csv_input
import wx
from wx.lib.mixins.grid import GridAutoEditMixin
import group_compositor
import sys
from utils import KillableThread

group_creator = group_compositor.GroupCalculator(allow_setting_invalid_inputs=True)

if 'app' not in globals():
    # Needet to allow imports from files other than main.py
    app = wx.App(False)


GROUPS_INITIAL_VALUE = 4
MEMBERS_INITIAL_VALUE = 12

HIGHLIGHT_COLOR = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
BACKGROUND_COLOR = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

EVT_FORCE_RERENDER = wx.NewEventType()
EVT_FORCE_RERENDER_BINDER = wx.PyEventBinder(EVT_FORCE_RERENDER)

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

        wx.CallAfter(self.out.AppendText, string)

    def flush(self):
        """
        Dummy methode. Required for compatibility with `sys.stdout`.
        """
        pass


class InpUtilsMixin:
    """
    Handels the numeric inputs of the user. This includes validation and event handling.
    """
    def on_group_composition_value_change(self, target: str, value = None):
        """
        Updates the group composition for ``target``. With the value provided.
        If the value is not a number, or an invalid target is selected nothing will be done.

        :param target: The target to update. Can be "group" or "member".
        :type target: str
        :param value: The new value.
        :type value: str

        :return: None
        """
        try:
            value = int(value)
        except ValueError:
            value = None
        match target:
            case "group":
                group_creator.n_groups = value
            case "member":
                group_creator.n_members = value
            case None:
                pass
        return
    
    def only_allow_number(self, event):
        """
        Allows only numeric input for age and height fields by preventing propagation 
        of non-numeric key events.

        :param event: The event that triggered the input.
        :type event: wx.KeyEvent

        :return: None
        """
        key_code = event.GetKeyCode()
        # Check if the key is a number, backspace, or a control key (e.g., arrow keys)
        if key_code in range(48, 58) or key_code in [wx.WXK_BACK, wx.WXK_RETURN]:
            event.Skip()  # Allow the input
        else:
            event.StopPropagation()  # Reject the input

class NumInpHandler(num_input.NumInput, InpUtilsMixin):
    """
    Handles the user input for the numeric input tab.
    Uses the :class:`InpUtilsMixin` to update the group composition with the user input.
    Layout is constructed in the base class :class:`layout.num_input.NumInput`.
    
    The following events are bound:
        - combo_members: :const:`wx.EVT_TEXT` -> :meth:`on_change_members`
        - combo_members, combo_groups: :const:`wx.EVT_CHAR` -> :meth:`InpUtilsMixin.only_allow_number`
        - combo_groups: :const:`wx.EVT_TEXT` -> :meth:`InpUtilsMixin.on_group_composition_value_change`
    """
    def __init__(self, parent):
        """
        Initializes the UI with the given parent widget and sets default values.
        
        :param parent: The parent window for this handler.
        :type parent: wx.Window

        :return: None     
        """
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
        """
        First updates the group composition with the new value from the event by calling :meth:`InpUtilsMixin.on_group_composition_value_change`.
        Then takes the new value from the event, updates `combo_groups` with new suggestions,
        and selects the middle value.

        :param event: The event that triggered the change.
        :type event: wx.CommandEvent

        :return: None
        """
        self.on_group_composition_value_change("member", event.GetString())
        self.combo_groups.Set([str(i) for i in range(2, group_creator.n_members//2)])
        self.combo_groups.SetValue(str(group_creator.n_members//4))

    def Enable(self, enable=True):
        """
        Used to enable or disable the input fields.

        :param enable: Defaults to `true`.
        :type enable: bool

        :return: None
        """
        self.combo_groups.Enable(enable)
        self.combo_members.Enable(enable)

    def on_activation(self):
        """
        Updates the values of groups and members in `group_creator` to the current values of the input fields
        by calling :meth:`InpUtilsMixin.on_group_composition_value_change`.

        :return: None
        """
        self.on_group_composition_value_change("member", int(self.combo_members.GetValue()))
        self.on_group_composition_value_change("group", int(self.combo_groups.GetValue()))

class CsvInpHandler(csv_input.CsvInput, InpUtilsMixin):
    """
    Handles the user input for the CSV input tab.
    Uses the :class:`InpUtilsMixin` to update the group composition with the user input.
    Layout is constructed in the base class :class:`layout.csv_input.CsvInput`.

    The following events are bound:
        - csv_filepicker: :const:`wx.EVT_FILEPICKER_CHANGED` -> :meth:`on_csv_fileselect`
        - members_header_csv, members_header_csv_sub: :const:`wx.EVT_CHOICE` -> :meth:`on_header_selection_change`
        - combo_groups: :const:`wx.EVT_TEXT` -> :meth:`InpUtilsMixin.on_group_composition_value_change`
        - combo_groups: :const:`wx.EVT_CHAR` -> :meth:`InpUtilsMixin.only_allow_number`
    """
    
    def __init__(self, parent):
        """
        Initializes the UI with the given parent widget and sets default values.

        :param parent: The parent window for this handler.
        :type parent: wx.Window

        :return: None
        """
        super().__init__(parent)
        self.combo_groups.Set([str(i) for i in range(2, 11)])
        self.combo_groups.Bind(wx.EVT_TEXT, lambda e: self.on_group_composition_value_change("group", e.GetString()))
        self.combo_groups.Bind(wx.EVT_CHAR, self.only_allow_number)
        self.combo_groups.SetValue(str(GROUPS_INITIAL_VALUE))

        self.csv_filepicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_csv_fileselect)
        self.members_header_csv.Bind(wx.EVT_CHOICE, self.on_header_selection_change)
        self.members_header_csv_sub.Bind(wx.EVT_CHOICE, self.on_header_selection_change)
    
    def on_activation(self):
        """
        Sets the values of groups in `group_creator` to the current value of the input field by calling :meth:`InpUtilsMixin.on_group_composition_value_change`.
        If a column of a CSV file is selected it will try to set the members in `group_creator` appropriately.
        If the column selection is invalid, the value will be set to `None`        

        :return: None
        """
        group_creator.n_members = None
        self.on_group_composition_value_change("group", int(self.combo_groups.GetValue()))
        try:
            self.on_header_selection_change(None, trigger_rerender=False)
        except ValueError:
            pass
    
    def Enable(self, enable=True):
        """
        Used to enable or disable the input fields.

        :param enable: Defaults to `true`.
        :type enable: bool
        
        :return: None
        """
        self.combo_groups.Enable(enable)
        self.csv_filepicker.Enable(enable)
        self.members_header_csv.Enable(enable)
        self.members_header_csv_sub.Enable(enable)

    def on_header_selection_change(self, _, trigger_rerender = True):
        """
        Updates the members in `group_creator` with the selected columns from the CSV file.
        
        :param _: The event that triggered the change, not used by the Methode.
        :param trigger_rerender: If `True` a class:`ForceRerender` event will be posted to the parent window.
        :type trigger_rerender: bool

        :return: None
        """

        group_creator.select_from_csv_file([self.members_header_csv.GetStringSelection(), self.members_header_csv_sub.GetStringSelection()])
        if trigger_rerender:
            wx.PostEvent(self.GetParent(), ForceRerender(EVT_FORCE_RERENDER, self.GetId()))

    def on_csv_fileselect(self, event):
        """
        Reads the columns of the selected CSV file and updates the choices in the header selection fields.
        Also sets the recomended group size and posts a class:`ForceRerender` event to the parent window.

        :param event: The event that triggered the file selection.
        :type event: wx.FileDirPickerEvent

        :return: None
        """
        headers = {}
        try: 
            headers = group_creator.read_csv_columns(event.GetPath())
        except Exception as e:
            wx.MessageBox(f"CSV-Datei kann nicht Verarbeitet werden. ({e})", "Error", wx.OK | wx.ICON_ERROR)
            self.csv_filepicker.SetPath("")
            return
        self.members_header_csv.Set(headers)
        self.members_header_csv.SetSelection(0)
        self.members_header_csv_sub.Set([""] + headers)
        self.members_header_csv_sub.SetSelection(0)
        # Must trigger mannually, because the event is not triggered by the SetSelection method
        self.on_header_selection_change(None, trigger_rerender=False)
        self.combo_groups.Set([str(i) for i in range(2, group_creator.n_members//2)])
        self.combo_groups.SetValue(str(group_creator.n_members//4))
        wx.PostEvent(self.GetParent(), ForceRerender(EVT_FORCE_RERENDER, self.GetId()))


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
            group_creator.alias[int(member)] = self.GetCellValue(row, 2)
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
            self.SetCellValue(i, 2, str(group_creator.alias.get(member, "")))
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
        n_rows = max([group_creator.n_members, len(groups)])
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
    """
    The "Hub" for all frontend interactions, and events.
    Also implements the 'export to csv' functionality.
    Layout is constructed in the base class :class:`layout.main_frame.MainFrame`.

    The following events are bound:
        - notebook_modes: :const:`wx.EVT_NOTEBOOK_PAGE_CHANGED` -> :meth:`on_page_change`
        - edit_aliases_btn: :const:`wx.EVT_BUTTON` -> :meth:`on_edit_aliases`
        - new_iteration_btn: :const:`wx.EVT_BUTTON` -> :meth:`on_new_iteration`
        - reset_btn: :const:`wx.EVT_BUTTON` -> :meth:`reset_state`
        - export_csv_btn: :const:`wx.EVT_BUTTON` -> :meth:`on_export_csv`
        - iterations_choise: :const:`wx.EVT_CHOICE` -> :meth:`on_iteration` 
    """
    
    @staticmethod
    def execute_in_thread(func, kw_args, callback_func):
        """
        Execute a function in a separate thread and call the callback function with the result.
        A :class:`KillableThread` is used to enable the user to cancel the thread.

        :param func: The function to execute.
        :type func: function
        :param kw_args: The arguments for the function.
        :type kw_args: dict | None
        :param callback_func: The function to call after the execution

        :return: The thread object.
        """
        def wrapper():
            res = None
            try:
                if kw_args is None:
                    res = func()
                else:
                    res = func(kw_args)
            except Exception as e:
                print(e)
            wx.CallAfter(callback_func, res)
        proc = KillableThread(target=wrapper, daemon=True)
        proc.start()
        return proc

    def __init__(self, parent):
        """
        Constructs the main frame with the given parent widget and adds:
            - :class:`NumInpHandler` 
            - :class:`CsvInpHandler`
            - :class:`InteractiveGrid`

        Then calls :meth:`on_new_iteration` to generate the first group composition.

        :param parent: The parent window for this handler.
        :type parent: wx.Window

        :return: None
        """
        super().__init__(parent)
        self.InpNum = NumInpHandler(self.notebook_modes)
        self.InpCsv = CsvInpHandler(self.notebook_modes)
        self.notebook_modes.AddPage(self.InpNum, "Mittels Eingabe", select=True)
        self.notebook_modes.AddPage(self.InpCsv, "Mittels CSV-Datei")

        self.notebook_modes.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_change)

        self.edit_aliases_btn.Bind(wx.EVT_BUTTON, self.on_edit_aliases)
        self.new_iteration_btn.Bind(wx.EVT_BUTTON, self.new_iteration_prep)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.reset_state)
        self.export_csv_btn.Bind(wx.EVT_BUTTON, self.on_export_csv)

        self.iterations_choise.Bind(wx.EVT_CHOICE, self.on_iteration_change)
        
        self.group_grid = InteractiveGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.grid_container.Add( self.group_grid, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.notebook_modes.Bind(EVT_FORCE_RERENDER_BINDER, self.rerender_iter_or_create)

        sys.stdout = RedirectText(self.cli_output)
        sys.stderr = RedirectText(self.cli_output)

        self.new_iteration_thread = None
        self.new_iteration_prep()

    def deactivate_buttons(self, ui_enabled = True, include_edit_aliases = True, include_new_iteration = True):
        """
        Enable or disable the buttons and inputs of the UI.

        :param ui_enabled: If `True` the UI will be enabled - Defaults to `True`.
        :type ui_enabled: bool
        :param include_edit_aliases: If `True` the edit_aliases_btn will be included - Defaults to `True`.
        :type include_edit_aliases: bool
        :param include_new_iteration: If `True` the new_iteration_btn will be included - Defaults to `True`.
        :type include_new_iteration: bool
        """
        self.InpNum.Enable(ui_enabled)
        self.InpCsv.Enable(ui_enabled)
        self.notebook_modes.Enable(ui_enabled)
        self.reset_btn.Enable(ui_enabled)
        self.export_csv_btn.Enable(ui_enabled)
        self.iterations_choise.Enable(ui_enabled)
        if include_edit_aliases:
            self.edit_aliases_btn.Enable(ui_enabled)
        if include_new_iteration:
            self.new_iteration_btn.Enable(ui_enabled)

    def check_pair_repetition_warning(self):
        """
        Display a hint at which point the pairs are repeated.

        :return: None
        """
        if int(self.iterations_choise.GetSelection()) >= group_creator.pair_repetition_brakepoinnt:
            self.pair_repetition_warning.SetLabel("Achtung: Wiederholung von Paaren")
            self.pair_repetition_warning.GetParent().Layout()
        else:
            self.pair_repetition_warning.SetLabel("")
        if group_creator.pair_repetition_brakepoinnt == sys.maxsize:
            self.pair_repetition_info.SetLabel("Noch keine Wiederholung von Paaren")
        else:
            self.pair_repetition_info.SetLabel(f"Ab Iteration {group_creator.pair_repetition_brakepoinnt} Wiederholung von Paaren")
        
    def reset_state(self, _, generate_new = True):
        """
        Resets the state of the group_creator object, also deleting aliases.
        If the user is in the CSV input mode, it will try to read the CSV file again.

        :param _: The event that triggered the reset, not used by the Methode.
        :param generate_new: If `True` a new group composition will be generated - Defaults to `true`.
        :type generate_new: bool

        :return: None
        """
        group_creator.reset_groups()
        group_creator.alias = {}
        if self.notebook_modes.GetSelection() == 1:
            try:
                group_creator.select_from_csv_file([self.InpCsv.members_header_csv.GetStringSelection(),
                                                     self.InpCsv.members_header_csv_sub.GetStringSelection()])
            except ValueError:
                pass
        if generate_new:
            self.new_iteration_prep()

    def reset_view(self):
        """
        Resets the view by deleting all rows in the grid and resetting the iteration selection.

        :return: None
        """
        try:
            self.group_grid.DeleteRows(0, self.group_grid.GetNumberRows())
            self.iterations_choise.Set([])
        except:
            pass

    def rerender_iter_or_create(self, _):
        """
        Render the selected itteration to the :class:`InteractiveGrid` or create a new Itteration.
        """
        iter_choise = self.iterations_choise.GetSelection()
        if iter_choise != wx.NOT_FOUND and group_creator.get_current_group(iter_choise):
            self.group_grid.rerender_groups(group_creator.get_current_group(iter_choise))
        else:
            self.new_iteration_prep()

    def on_iteration_change(self, event):
        """
        Render the selected itteration to the :class:`InteractiveGrid`.
        Check :meth:`check_pair_repetition_warning` to display a warning if the pair repetition is reached.

        :param event: The event that triggered the change.
        :type event: wx.CommandEvent

        :return: None
        """
        group = group_creator.get_current_group(iteration=int(event.GetString()), replace_alias=False)
        self.check_pair_repetition_warning()
        self.group_grid.rerender_groups(group)

    def on_page_change(self, event):
        """
        Handle the page change event of the notebook_modes.
        Triggering the activation of the new page and resetting the view of, if possible, 
        directly generating a new group composition.

        :param event: The event that triggered the change.
        :type event: wx.CommandEvent

        :return: None
        """
        self.reset_state(None, generate_new=False)
        match event.GetSelection():
            case 0:
                self.InpNum.on_activation()
            case 1:
                self.InpCsv.on_activation()
            case  _:
                print("Invalid page. This should not happen")
        #self.reset_view()
        if group_creator.n_groups and group_creator.n_members:
            self.new_iteration_prep()
        else:
            self.reset_view()

    def new_iteration_prep(self, _ = None):
        """
        Prepare the generation of a new group composition.
        If a new group composition is already being generated, the generation will be canceled.
        The generation will be done in a separate thread to prevent the UI from freezing.
        After the generation, :meth:`__new_iteration_handler` will be called.

        :param _: The event that triggered the new iteration, not used by the Methode.

        :return: None
        """
        match self.new_iteration_btn.Label:
            case "Abbrechen...":
                if self.new_iteration_thread:
                    self.new_iteration_thread.kill()
                wx.EndBusyCursor()
                self.new_iteration_btn.Label = "Neu Zusammensetzen"
                self.deactivate_buttons(True, include_new_iteration=False)
                return
            case _:
                wx.BeginBusyCursor()
                self.new_iteration_btn.Label = "Abbrechen..."
                self.deactivate_buttons(False, include_new_iteration=False)
                self.new_iteration_thread = self.execute_in_thread(group_creator.create_groups, None, self.__new_iteration_handler)
                return
        

    def __new_iteration_handler(self, return_value = None):
        """
        Handle the visualization of the new group composition.
        If the group composition is invalid, an error message will be displayed.

        :param return_value: The return value of the group composition generation.
        :type return_value: dict{str: list[int]} | None

        :return: None
        """
        wx.EndBusyCursor()
        self.new_iteration_btn.Label = "Neu Zusammensetzen"
        self.deactivate_buttons(True, include_new_iteration=False)
        if not return_value:
            if self.notebook_modes.GetSelection() == 0:
                wx.MessageBox("Ungültig Gruppenkomposition.", "Error", wx.OK | wx.ICON_ERROR)
            else:
                self.reset_view()
            return
                    
        new_group = group_creator.get_current_group()
        self.iterations_choise.Set(list(map(lambda x: str(x), range(group_creator.get_iteration()+1))))
        self.iterations_choise.SetSelection(group_creator.get_iteration())
        self.check_pair_repetition_warning()
        self.group_grid.rerender_groups(new_group)
        
    def on_edit_aliases(self, _):
        """
        Allow the user to directly added the aliasses of al members by sequnecielly displaying all members in the grid.
        All other inputs will be disabled during the editing process.
        If ther are no Groups deffined a error in a :class:`wx.MessageBox` will be displayed.
        After the edeting the previous state of the grid will be restored.

        :param _: The event that triggered the edit, not used by the Methode.
        
        :return: None
        """
        if self.iterations_choise.GetSelection() == wx.NOT_FOUND:
            wx.MessageBox("Keine zu bearbeitenden Gruppenmitglieder vorhanden.", "Error", wx.OK | wx.ICON_ERROR)
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
        self.deactivate_buttons(ui_enabled, include_edit_aliases=False)

    def on_export_csv(self, _):
        """
        Allows exporting the current group composition as a CSV file.
        The user can select the path and name of the file.
        If there are no groups to export, an error message will be displayed in a :class:`wx.MessageBox`.

        :param _: The event that triggered the export, not used by the Methode.

        :return: None
        """
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
