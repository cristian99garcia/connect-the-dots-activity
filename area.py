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

import math
import cairo
import random

from gettext import gettext as _

from levels import LEVELS

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf


COLORS = [(0.509803921569, 0.545098039216, 0.125490196078),
          (0.690196078431, 0.674509803922, 0.192156862745),
          (0.796078431373, 0.772549019608, 0.239215686275),
          (0.980392156863, 0.843137254902, 0.474509803922),
          (0.976470588235, 0.894117647059, 0.678431372549),
          (0.980392156863, 0.949019607843, 0.858823529412),
          (0.337254901961, 0.207843137255, 0.0705882352941),
          (0.607843137255, 0.290196078431, 0.043137254902),
          (0.827450980392, 0.4, 0.0),
          (0.996078431373, 0.541176470588, 0.0),
          (0.976470588235, 0.654901960784, 0.121568627451)]


def make_rect(x, y, width, height):
    rect = Gdk.Rectangle()
    rect.x = x
    rect.y = y
    rect.width = width
    rect.height = height

    return rect


class Area(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.level = -1
        self.color = None
        self.pen_pixbuf = None
        self.star_pixbuf = None
        self.points = {}  # index: [color, [x1, y1], [x2, y2]],
        self.brush_size = 10
        self.color_count = 0
        self.add_points = False
        self.pen = []
        self.level_data = {}
        self.over_pen = False

        self.set_size_request(800, 1)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)

        self.connect("draw", self.__draw_cb)
        self.connect("button-press-event", self.__press_cb)
        self.connect("button-release-event", self.__release_cb)
        self.connect("motion-notify-event", self.__motion_cb)

        self.load_random_color()
        self.load_pixbufs()

    def __draw_cb(self, widget, context):
        if "star" in self.level_data.keys():
            self.draw_lines(context)
            self.draw_dots(context)

            star_x = self.level_data["star"][0] - \
                self.star_pixbuf.get_width() / 2

            star_y = self.level_data["star"][1] - \
                self.star_pixbuf.get_height() / 2 + 30

            pen_x = self.pen[0] - self.pen_pixbuf.get_width() / 2
            pen_y = self.pen[1] - self.pen_pixbuf.get_height() / 2

            Gdk.cairo_set_source_pixbuf(
                context, self.star_pixbuf, star_x, star_y)
            context.paint()

            Gdk.cairo_set_source_pixbuf(
                context, self.pen_pixbuf, pen_x, pen_y)
            context.paint()

        else:
            self.show_next_level_message(context)

    def __press_cb(self, widget, event):
        self.load_random_color()

        if self.over_pen:
            self.add_points = True
            self.points[self.color_count] = [self.color, [self.pen]]

        self.redraw()

    def __release_cb(self, widget, event):
        if self.add_points:
            self.color_count += 1

        self.add_points = False
        self.redraw()

    def __motion_cb(self, widget, event):
        alloc = self.get_allocation()

        if self.pen == []:
            return

        rect1 = make_rect(event.x, event.y, 1, 1)

        width = self.pen_pixbuf.get_width()
        height = self.pen_pixbuf.get_height()
        rect2 = make_rect(
            self.pen[0] - width / 2, self.pen[1] - height / 2, width, height)

        collision = rect1.x >= rect2.x and \
            rect1.x <= rect2.x + rect2.width and \
            rect1.y >= rect2.y and \
            rect1.y <= rect2.y + rect2.height

        if collision and not self.over_pen and not self.add_points:
            self.over_pen = True
            self.pen_pixbuf = self.pen_pixbuf.scale_simple(
                72, 72, GdkPixbuf.InterpType.HYPER)

        elif not collision and self.over_pen and not self.add_points:
            self.over_pen = False
            self.pen_pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/pen.svg")

        if self.add_points:
            min_x = self.pen_pixbuf.get_width() / 2
            max_x = alloc.width - min_x
            min_y = self.pen_pixbuf.get_height() / 2
            max_y = alloc.height - min_y

            x = event.x if event.x >= min_x else min_x
            x = x if x <= max_x else max_x
            y = event.y if event.y >= min_y else min_y
            y = y if y <= max_y else max_y

            self.pen = [x, y]
            self.points[self.color_count][1].append(self.pen)

        self.redraw()

    def show_next_level_message(self, context):
        y = 60
        message = _("When you finish a drawing,") + "\n"
        message += _("click on the star to move on to the next one!")

        y += self.show_message(context, message, y=y)
        y += self.show_message(context, _("Try click on the star now."), y=y)

    def draw_dots(self, context):
        dot_radius = 15
        dot_line = 4
        index = 1

        context.set_font_size(20)
        context.select_font_face(
            "Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

        for dot in self.level_data["dots"]:
            x = dot[0]
            y = dot[1] + dot_radius * 2
            label = str(index)
            xb, yb, label_width, label_height, xa, ya = \
                context.text_extents(label)

            context.set_source_rgb(1, 1, 1)
            context.arc(x, y, dot_radius, 0, 2 * math.pi)
            context.fill()

            context.set_line_width(dot_line)
            context.set_source_rgb(0, 0, 0)
            context.arc(x, y, dot_radius, 0, 2 * math.pi)
            context.stroke()

            context.move_to(x - label_width / 2, y + label_height / 2)
            context.show_text(label)

            index += 1

    def draw_lines(self, context):
        context.set_line_width(self.brush_size * 2)
        for x in range(0, len(self.points.keys())):
            last_dot = []
            color = self.points[x][0]
            context.set_source_rgb(*color)

            for dot in self.points[x][1]:
                context.arc(dot[0], dot[1], self.brush_size, 0, 2 * math.pi)
                context.fill()

                if last_dot != []:
                    context.move_to(last_dot[0], last_dot[1])
                    context.line_to(dot[0], dot[1])
                    context.stroke()

                last_dot = dot

    def load_random_color(self):
        self.color = random.choice(COLORS)

    def load_pixbufs(self):
        self.pen_pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/pen.svg")
        self.star_pixbuf = GdkPixbuf.Pixbuf.new_from_file("images/star.svg")
        self.star_pixbuf = self.star_pixbuf.scale_simple(
            30, 30, GdkPixbuf.InterpType.HYPER)

    def next_level(self):
        self.level += 1
        if self.level >= len(LEVELS):
            self.level_data = self.get_random_level()
        else:
            self.level_data = LEVELS[self.level]

        self.load_level_data()
        self.redraw()

    def load_level_data(self):
        del self.points
        self.points = {}
        self.color_count = 0
        self.pen = [self.level_data["star"][0], self.level_data["star"][1] + 30]

    def get_random_level(self):
        alloc = self.get_allocation()
        min_x = self.pen_pixbuf.get_width() / 2
        max_x = alloc.width - min_x
        min_y = self.pen_pixbuf.get_height() / 2
        max_y = alloc.height - min_y - 30

        def get_random_pos():
            return [random.randint(min_x, max_x), random.randint(min_y, max_y)]

        dots = []
        for x in range(0, random.randint(12, 20)):
            dots.append(get_random_pos())

        return {
            "star": get_random_pos(),
            "dots": dots
        }

    def show_message(self, context, message, font_size=34, y=None):
        if len(message.splitlines()) > 1:
            y = 60
            for line in message.splitlines():
                y += self.show_message(context, line, font_size, y)

            return y

        else:
            alloc = self.get_allocation()

            context.set_source_rgb(0, 0, 0)
            context.set_font_size(font_size)

            xb, yb, width, height, xa, ya = context.text_extents(message)
            y = y or 60 + height

            if width > alloc.width:
                self.show_message(context, message, font_size - 10)

            else:
                context.move_to(alloc.width / 2 - width / 2, y)
                context.show_text(message)

            return height

    def redraw(self):
        self.queue_draw()
