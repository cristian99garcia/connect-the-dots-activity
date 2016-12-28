#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from gettext import gettext as _

from area import Area

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from sugar3.activity import activity
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton


class ConnectTheDotsActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.make_toolbar()

        hbox = Gtk.HBox()
        self.set_canvas(hbox)

        self.area = Area()
        hbox.pack_start(self.area, True, False, 0)

        self.show_all()

    def make_toolbar(self):
        toolbarbox = ToolbarBox()
        self.set_toolbar_box(toolbarbox)

        button = ActivityToolbarButton(self)
        toolbarbox.toolbar.insert(button, -1)

        toolbarbox.toolbar.insert(Gtk.SeparatorToolItem(), -1)

        button_new = ToolButton("new-button")
        button_new.set_tooltip(_("New"))
        button_new.connect("clicked", self._next_level)
        toolbarbox.toolbar.insert(button_new, -1)

        label = Gtk.Label(_(
            "Click on the star and then drag the turtle from 1 to 2 to 3..."))

        item = Gtk.ToolItem()
        item.add(label)
        toolbarbox.toolbar.insert(item, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbarbox.toolbar.insert(separator, -1)

        button = StopButton(self)
        toolbarbox.toolbar.insert(button, -1)

    def _next_level(self, button):
        self.area.next_level()
