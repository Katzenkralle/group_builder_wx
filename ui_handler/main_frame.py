import wx
import wx.grid
import sys

from group_creator import KillableThread
from group_creator import GroupCalculator as group_creator
from .layout import main_frame
from .input import NumInpHandler, CsvInpHandler
from .interactive_grid import InteractiveGrid
from .helpers import RedirectText
from .constants import EVT_FORCE_RERENDER_BINDER

class MainFrameHandler(main_frame.MainFrame):
    """
    The "Hub" for all frontend interactions, and events.
    Also implements the 'export to csv' functionality.
    Layout is constructed in the base class :class:`ui_handler.layout.main_frame.MainFrame`.

    The following events are bound:
        - notebook_modes: :const:`wx.EVT_NOTEBOOK_PAGE_CHANGED` -> :meth:`on_page_change`
        - edit_aliases_btn: :const:`wx.EVT_BUTTON` -> :meth:`on_edit_aliases`
        - new_iteration_btn: :const:`wx.EVT_BUTTON` -> :meth:`new_iteration_prep`
        - reset_btn: :const:`wx.EVT_BUTTON` -> :meth:`reset_state`
        - export_csv_btn: :const:`wx.EVT_BUTTON` -> :meth:`on_export_csv`
        - iterations_choise: :const:`wx.EVT_CHOICE` -> :meth:`on_iteration_change` 
    """
    
    @staticmethod
    def execute_in_thread(func, kw_args, callback_func):
        """
        Execute a function in a separate thread and call the callback function with the result.
        A :class:`group_creator.utils.KillableThread` is used to enable the user to cancel the thread.

        :param func: The function to execute.
        :type func: function
        :param kw_args: The arguments for the function.
        :type kw_args: dict | None
        :param callback_func: The function to call after the execution (recives result of `func`).

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
            - :class:`ui_handler.input.NumInpHandler` 
            - :class:`ui_handler.input.CsvInpHandler`
            - :class:`ui_handler.interactive_grid.InteractiveGrid`

        Then calls :meth:`new_iteration_prep` to generate the first group composition.

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
        if int(self.iterations_choise.GetSelection()) >= group_creator().pair_repetition_brakepoinnt:
            self.pair_repetition_warning.SetLabel("Achtung: Wiederholung von Paaren")
            self.pair_repetition_warning.GetParent().Layout()
        else:
            self.pair_repetition_warning.SetLabel("")
        if group_creator().pair_repetition_brakepoinnt == sys.maxsize:
            self.pair_repetition_info.SetLabel("Noch keine Wiederholung von Paaren")
        else:
            self.pair_repetition_info.SetLabel(f"Ab Iteration {group_creator().pair_repetition_brakepoinnt} Wiederholung von Paaren")
        
    def reset_state(self, _, generate_new = True):
        """
        Resets the state of the group_creator object, also deleting aliases.
        If the user is in the CSV input mode, it will try to read the CSV file again.

        :param _: The event that triggered the reset, not used by the Methode.
        :param generate_new: If `True` a new group composition will be generated - Defaults to `true`.
        :type generate_new: bool

        :return: None
        """
        group_creator().reset_groups()
        group_creator().alias = {}
        if self.notebook_modes.GetSelection() == 1:
            try:
                group_creator().select_from_csv_file([self.InpCsv.members_header_csv.GetStringSelection(),
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
        Render the selected itteration to the :class:`ui_handler.interactive_grid.InteractiveGrid` or create a new Itteration.
        """
        iter_choise = self.iterations_choise.GetSelection()
        if iter_choise != wx.NOT_FOUND and group_creator().get_current_group(iter_choise):
            self.group_grid.rerender_groups(group_creator().get_current_group(iter_choise))
        else:
            self.new_iteration_prep()

    def on_iteration_change(self, event):
        """
        Render the selected itteration to the :class:`ui_handler.interactive_grid.InteractiveGrid`.
        Check :meth:`check_pair_repetition_warning` to display a warning if the pair repetition is reached.

        :param event: The event that triggered the change.
        :type event: wx.CommandEvent

        :return: None
        """
        group = group_creator().get_current_group(iteration=int(event.GetString()), replace_alias=False)
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
        if group_creator().n_groups and group_creator().n_members:
            self.new_iteration_prep()
        else:
            self.reset_view()

    def new_iteration_prep(self, _ = None):
        """
        Prepare the generation of a new group composition.
        If a new group composition is already being generated, the operation will be canceled.
        The generation will be done in a separate thread, called by :meth:`execute_in_thread`
        to prevent the UI from freezing.
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
                self.new_iteration_thread = self.execute_in_thread(group_creator().create_groups, None, self.__new_iteration_handler)
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
            wx.MessageBox("Ungültig Gruppenkomposition.", "Error", wx.OK | wx.ICON_ERROR)
            return
                    
        new_group = group_creator().get_current_group()
        self.iterations_choise.Set(list(map(lambda x: str(x), range(group_creator().get_iteration()+1))))
        self.iterations_choise.SetSelection(group_creator().get_iteration())
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
            curent_group = group_creator().get_current_group(self.iterations_choise.GetSelection())
            acumulated_members = []
            for group in curent_group:
                for member in curent_group[group]:
                    acumulated_members.append(member)
            acumulated_members  = list(sorted(acumulated_members))
            self.group_grid.rerender_groups({"": acumulated_members})
            ui_enabled = False
        else:
            self.edit_aliases_btn.SetLabel("Alias bearbeiten")
            self.group_grid.rerender_groups(group_creator().get_current_group(self.iterations_choise.GetSelection()))
        self.deactivate_buttons(ui_enabled, include_edit_aliases=False)

    def on_export_csv(self, _):
        """
        Allows exporting the current group composition as a CSV file.
        The user can select the path and name of the file.
        If there are no groups to export, an error message will be displayed in a :class:`wx.MessageBox`.

        :param _: The event that triggered the export, not used by the Methode.

        :return: None
        """
        if not group_creator().get_current_group():
            wx.MessageBox("No groups to export.", "Error", wx.OK | wx.ICON_ERROR)
            return
        exit_code = wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv", defaultFile="GroupeExport.csv" ,style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if exit_code.ShowModal() == wx.ID_CANCEL:
            return
        path = exit_code.GetPath()
        try:
            group_creator().export_group_as_csv(group_creator().get_iteration(), path)
        except:
            wx.MessageBox("An error occurred while exporting the CSV file.", "Error", wx.OK | wx.ICON_ERROR)
