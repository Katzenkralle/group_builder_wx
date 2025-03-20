import wx

from group_creator import GroupCalculator as group_creator
from .layout import num_input, csv_input
from .helpers import ForceRerender
from .constants import GROUPS_INITIAL_VALUE, MEMBERS_INITIAL_VALUE, EVT_FORCE_RERENDER

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
                group_creator().n_groups = value
            case "member":
                group_creator().n_members = value
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
    Layout is constructed in the base class :class:`ui_handler.layout.num_input.NumInput`.
    
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
        try:
            self.combo_groups.Set([str(i) for i in range(2, (group_creator().n_members//2+1))])
            self.combo_groups.SetValue(str(group_creator().n_members//4))
        except TypeError:
            pass

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
        Updates the values of groups and members in :class:`group_creator.group_compositor.GroupCalculator` to the current values of the input fields
        by calling :meth:`InpUtilsMixin.on_group_composition_value_change`.

        :return: None
        """
        self.on_group_composition_value_change("member", int(self.combo_members.GetValue()))
        self.on_group_composition_value_change("group", int(self.combo_groups.GetValue()))

class CsvInpHandler(csv_input.CsvInput, InpUtilsMixin):
    """
    Handles the user input for the CSV input tab.
    Uses the :class:`InpUtilsMixin` to update the group composition with the user input.
    Layout is constructed in the base class :class:`ui_handler.layout.csv_input.CsvInput`.

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
        Sets the values of groups in :class:`group_creator.group_compositor.GroupCalculator`
        to the current value of the input field by calling :meth:`InpUtilsMixin.on_group_composition_value_change`.
        If a column of a CSV file is selected it will try to set the members in 
        :class:`group_creator.group_compositor.GroupCalculator` appropriately.
        If the column selection is invalid, the value will be set to `None`        

        :return: None
        """
        group_creator().n_members = None
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
        Updates the members in :class:`group_creator.group_compositor.GroupCalculator` with the selected columns from the CSV file.
        
        :param _: The event that triggered the change, not used by the Methode.
        :param trigger_rerender: If `True` a :class:`ui_handler.helpers.ForceRerender` event will be posted to the parent window.
        :type trigger_rerender: bool

        :return: None
        """

        group_creator().select_from_csv_file([self.members_header_csv.GetStringSelection(), self.members_header_csv_sub.GetStringSelection()])
        if trigger_rerender:
            wx.PostEvent(self.GetParent(), ForceRerender(EVT_FORCE_RERENDER, self.GetId()))

    def on_csv_fileselect(self, event):
        """
        Reads the columns of the selected CSV file and updates the choices in the header selection fields.
        Also sets the recomended group size and posts a :class:`ui_handler.helpers.ForceRerender` event to the parent window.

        :param event: The event that triggered the file selection.
        :type event: wx.FileDirPickerEvent

        :return: None
        """
        headers = {}
        try: 
            headers = group_creator().read_csv_columns(event.GetPath())
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
        self.combo_groups.Set([str(i) for i in range(2, group_creator().n_members//2)])
        self.combo_groups.SetValue(str(group_creator().n_members//4))
        wx.PostEvent(self.GetParent(), ForceRerender(EVT_FORCE_RERENDER, self.GetId()))
