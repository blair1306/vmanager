# This module provides a listbox with dynamic content that can be updated by calling it's update function.

from ..ui import create_listbox


class DynamicListBox(object):
    """
    A listbox with dynamic content.
    """
    def __init__(self, update_func, _listbox):
        """
        @param update_func: function used to update the content of the listbox
        @param listbox: the listbox to show the contents on.
        """
        self._update_func = update_func
        self._listbox = _listbox

        self._list = []

    def update(self):
        """
        Update the content of it's list and it's listbox.
        """
        self._list = self._update_func()
        self._listbox.update_options(self._list)
    
    @property
    def selections(self):
        """
        Get a list of all items under selection.
        """
        index_list = self._listbox.get_selected_index_list()
        selection_list = [self._list[index] for index in index_list]

        return selection_list