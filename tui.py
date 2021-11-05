import curses
import math
import time
import builtins


PASSWORD_ASCII = r"""
 ____                                     _     
|  _ \ __ _ ___ _____      _____  _ __ __| |___ 
| |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` / __|
|  __/ (_| \__ \__ \\ V  V / (_) | | | (_| \__ \
|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|___/
                                                
"""

def print(*args):
    builtins.print(*args)
    time.sleep(1)





KEY_CTRL_UP        = 567
KEY_CTRL_DOWN      = 526
KEY_CTRL_LEFT      = 546
KEY_CTRL_RIGHT     = 561
KEY_CTRL_BACKSPACE = 8
KEY_CTRL_DEL       = 520
KEY_ENTER          = 10

L_MOUSE_UP = 1
L_MOUSE_DOWN = 2
R_MOUSE_UP = 1024
R_MOUSE_DOWN = 2048
M_MOUSE_UP = 32
M_MOUSE_DOWN = 64
MOUSE_DRAG = 268435456

valid_chars = {
    "`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", 
    "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", 
    "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\", 
    "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "{", "}", "|", 
    "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'",
    "A", "S", "D", "F", "G", "H", "J", "K", "L", ":", '"',
    "z", "x", "c", "v", "b", "n", "m", ",", ".", "/",
    "Z", "X", "C", "V", "B", "N", "M", "<", ">", "?",
    " "
}

# STDSCR is global
STDSCR = None

def addstr_slow(y, x, string):
    try:
        for c in string:
            STDSCR.addstr(y, x, c)
            STDSCR.refresh()
            time.sleep(0.001)
            x += 1
    except curses.error:
        pass

def addstr_fast(y, x, string):
    try:
        STDSCR.addstr(y, x, string)
    except curses.error:
        pass

addstr = addstr_fast

def move_cursor(y, x):
    try:
        STDSCR.move(y, x)
    except curses.error:
        pass


class Borders:
    def __init__(self, chars, title=None, align="left"):
        self.chars = list(chars)
        self.title = title
        self.align = align

    def draw(self, by, bx, bh, bw):
        self.y = by
        self.x = bx
        self.h = bh
        self.w = bw
        self.draw_borders()
        if self.title:
            self.draw_title()

    def draw_borders(self):
        addstr(self.y, self.x,
               self.chars[0] + (self.w - 2) * self.chars[1] + self.chars[2])

        for i in range(self.y + 1, self.y + self.h - 1):
            addstr(i, self.x,
                   self.chars[3])
            addstr(i, self.x + self.w - 1,
                   self.chars[4])

        addstr(self.y + self.h - 1, self.x,
               self.chars[5] + (self.w - 2) * self.chars[6] + self.chars[7])


    def draw_title(self):
        if self.align == "left":
            addstr(self.y, self.x + 1,
                   " " + self.title + " ")
        elif self.align == "right":
            addstr(self.y, self.w + self.x - len(self.title) - 3,
                   " " + self.title + " ")
        else:
            addstr(self.y, self.x + int(self.w / 2 - len(self.title) / 2),
                   " " + self.title + " ")


ASCII         = "+-+||+-+"
CURVED        = "╭─╮││╰─╯"
STRAIGHT      = "┌─┐││└─┘"
DOUBLE        = "╔═╗║║╚═╝"
THICK         = "┏━┓┃┃┗━┛"
CURVED_RIGHT  = "┌─╮││└─╯"
CURVED_CORNER = "╭─╮││└─╯"

DEFAULT_BORDER = Borders(STRAIGHT)

class Widget:
    @property
    def w(self):
        if self.borders:
            return self.bw - 2
        return self.bw

    @property
    def h(self):
        if self.borders:
            return self.bh - 2
        return self.bh

    @property
    def x(self):
        if self.borders:
            return self.bx + 1
        return self.bx

    @property
    def y(self):
        if self.borders:
            return self.by + 1
        return self.by

    @w.setter
    def w(self, value):
        if self.borders:
            self.bw = value + 2
        else:
            self.bw = value

    @h.setter
    def h(self, value):
        if self.borders:
            self.bh = value + 2
        else:
            self.bh = value

    @x.setter
    def x(self, value):
        self.bx = value

    @y.setter
    def y(self, value):
        self.by = value

    def resize(self, height, width, bounds=False):
        if bounds:
            self.bh = height
            self.bw = width
        else:
            self.h = height
            self.w = width

    def on_press(self, button, y, x):
        pass

    def on_drag(self, button, y, x):
        pass

    def on_release(self, button, y, x):
        pass

    def set_title(self, title):
        self.borders.title = title
        self.borders.draw_borders()
        if title:
            self.borders.draw_title()

    def __init__(self, interactive=False, align="left", valign="top",
                 bg_color=1, fg_color=2, borders=None, 
                 expandx=False, expandy=False,
                 width=0, height=0, display=True, x=0, y=0):

        self.parent = None

        self.y = y
        self.x = x

        self.display = display

        if borders is True:
            self.borders = DEFAULT_BORDER
        else:
            self.borders = borders

        self.h, self.w = height, width

        self.interactive = interactive
        self.expandx = expandx
        self.expandy = expandy

        self.bg_color = bg_color
        self.fg_color = fg_color

        self.align = align
        self.valign = valign

    def request_redraw(self):
        self.parent.request_redraw()

#    def draw_borders(self):
#        addstr(self.by, self.bx, self.borders[0] + self.w * self.borders[1] + self.borders[2])
#        for i in range(self.by + 1, self.by + self.bh - 1):
#            addstr(i, self.bx, self.borders[3])
#            addstr(i, self.bx + self.w + 1, self.borders[4])
#        addstr(self.by + self.bh - 1, self.bx, self.borders[5] + self.w * self.borders[6] + self.borders[7])

    def focus(self):
        move_cursor(self.y, self.x)
        return self

    def request_focus(self):
        self.parent.request_focus(self)

    def request_refocus(self):
        self.parent.request_refocus()

    def set_parent(self, parent):
        self.parent = parent

    def next_widget(self):
        return None

    def get_widget(self, y, x):
        return self

    def draw_borders(self):
        if self.borders:
            self.borders.draw(self.by, self.bx,
                              self.bh, self.bw)

    def move(self, y, x):
        self.y = y
        self.x = x

    def draw(self):
        self.draw_borders()
        self.redraw()

    def redraw(self):
        self.draw_func(self.y, self.x)


class Separator(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw_func(self, y, x):
        pass

class TextWidget(Widget):
    def __init__(self, text, fill_char=None, **kwargs):
        super().__init__(**kwargs)
        self.fill_char = fill_char
        self.lines = text.split("\n")
        self.h = len(self.lines)
        w = max(len(line) for line in self.lines)
        if w > self.w:
            self.w = w

    @property
    def text(self):
        return "\n".join(self.lines)

    def draw_func(self, y, x):
        if self.valign == "center":
            y += (self.h - len(self.lines)) // 2
        elif self.valign == "bottom":
            y += self.h - len(self.lines)

        for line in self.lines:
            text = line[-self.w:]
            if self.fill_char:
                text = len(text) * self.fill_char
            if self.align == "left":
                text = text.ljust(self.w)
            elif self.align == "right":
                text = text.rjust(self.w)
            if self.align == "center":
                text = text.center(self.w)
            addstr(y, x, text)
            y += 1

class Button(TextWidget):
    def __init__(self, text, hook=None, borders=True,
                 interactive=True, **kwargs):
        super().__init__(
            text, borders=borders, interactive=interactive,
            **kwargs
        )
        self.hook = (lambda b: None) if hook is None else hook

    def on_press(self, button, y, x):
        if button == L_MOUSE_DOWN:
            self.hook(self)

    def on_key(self, ch):
        if ch == KEY_ENTER:
            self.hook(self)



class Label(TextWidget):
    def __init__(self, text, **kwargs):
        super().__init__(text, **kwargs)

class Input(Widget):
    def __init__(self, empty_text="", fill_char=None, borders=True, interactive=True, **kwargs):
        super().__init__(borders=borders, interactive=interactive, **kwargs)
        self.fill_char = fill_char
        self.h += 1
        self.cursor_idx = 0
        self.view_start = 0
        self.text = ""

    def on_press(self, button, y, x):
        if button == L_MOUSE_DOWN:
            self.request_focus()

    def focus(self):
        move_cursor(self.y, self.x + min(self.cursor_idx - self.view_start, self.w))
        return self

    def draw_func(self, y, x):
        if self.cursor_idx < self.view_start:
            self.view_start = self.cursor_idx
        elif self.cursor_idx > self.view_start + self.w:
            self.view_start = self.cursor_idx - self.w
        text = self.text[self.view_start:self.view_start + self.w]
        if self.fill_char:
            text = len(text) * self.fill_char
        if self.align == "left":
            text = text.ljust(self.w)
        elif self.align == "right":
            text = text.rjust(self.w)
        if self.align == "center":
            text = text.center(self.w)
        addstr(y, x, text)

    def jump_forward_word(self):
        idx = self.cursor_idx + 1
        while idx < len(self.text) and self.text[idx] in (" ", "\t"):
            idx += 1
        while idx < len(self.text) and self.text[idx] not in (" ", "\t"):
            idx += 1
        return idx

    def jump_back_word(self):
        idx = self.cursor_idx - 1
        while idx > 0 and self.text[idx] in (" ", "\t"):
            idx -= 1
        while idx > 0 and self.text[idx - 1] not in (" ", "\t"):
            idx -= 1
        return idx

    def on_key(self, ch):
        if ch == curses.KEY_BACKSPACE:
            if self.cursor_idx > 0:
                self.text = self.text[:self.cursor_idx - 1] + self.text[self.cursor_idx:]
                self.cursor_idx -= 1
                if self.view_start > 0:
                    self.view_start -= 1
        elif ch == KEY_CTRL_BACKSPACE:
            if self.cursor_idx > 0:
                idx = self.jump_back_word()
                self.text = self.text[:idx] + self.text[self.cursor_idx:]
                if self.view_start > 0:
                    self.view_start -= self.cursor_idx - idx
                    if self.view_start < 0:
                        self.view_start = 0
                self.cursor_idx = idx
        elif ch == KEY_CTRL_DEL:
            if self.cursor_idx < len(self.text):
                idx = self.jump_forward_word()
                self.text = self.text[:self.cursor_idx] + self.text[idx:]
        elif ch == KEY_CTRL_LEFT:
            if self.cursor_idx > 0:
                self.cursor_idx = self.jump_back_word()
        elif ch == KEY_CTRL_RIGHT:
            if self.cursor_idx < len(self.text):
                self.cursor_idx = self.jump_forward_word()
        elif ch == KEY_CTRL_UP:
            pass
        elif ch == KEY_CTRL_DOWN:
            pass
        elif ch == curses.KEY_DC:
            if self.cursor_idx < len(self.text):
                self.text = self.text[:self.cursor_idx] + self.text[self.cursor_idx + 1:]
        elif ch == curses.KEY_LEFT:
            if self.cursor_idx > 0:
                self.cursor_idx -= 1
        elif ch == curses.KEY_RIGHT:
            if self.cursor_idx < len(self.text):
                self.cursor_idx += 1
        elif ch == curses.KEY_UP:
            pass
        elif ch == curses.KEY_DOWN:
            pass
        elif chr(ch) in valid_chars:
            self.text = self.text[:self.cursor_idx] + chr(ch) + self.text[self.cursor_idx:]
            self.cursor_idx += 1 
        if self.cursor_idx - self.view_start >= self.w:
            self.view_start = self.cursor_idx - self.w + 1
        self.redraw()
        move_cursor(self.y, self.x + self.cursor_idx - self.view_start)


#class Title:
#    def __init__(self, title, align="left"):
#        self.title = title
#        self.align = align
#
#    def draw(self, y, x, w, h):
#        if self.align == "left":
#            addstr(y, x + 1, " " + self.title + " ")
#        elif self.align == "right":
#            addstr(y, w + x - len(self.title) - 3, " " + self.title + " ")
#        else:
#            addstr(y, x + int(w / 2 - len(self.title) / 2), " " + self.title + " ")

class Container(Widget):
    def get_min_area(self):
        self.refresh_widths()
        self.refresh_heights()
        return self.bh, self.bw

    def iter_widgets(self):
        for widget in self.widgets:
            if widget.display:
                yield widget

    def clear(self):
        self.active_widget_idx = 0
        self.widgets = []

    def __init__(self, *widgets, title=None, **kwargs):
        super().__init__(**kwargs)
        self.widgets = []
        self.active_widget_idx = 0
        for widget in widgets:
            widget.parent = self
            self.add(widget)

    def request_focus(self, widget):
        self.active_widget_idx = self.widgets.index(widget)
        self.parent.request_focus(self)

    def focus(self):
        return self.widgets[self.active_widget_idx].focus()

    def next_widget(self):
        if not self.widgets:
            return None

        if self.active_widget_idx is None:
            self.active_widget_idx = 0
        else:
            widget = self.widgets[self.active_widget_idx].next_widget()
            if widget:
                return widget
            self.active_widget_idx += 1
        if self.active_widget_idx >= len(self.widgets):
            self.active_widget_idx = None
            return None

        widget = self.widgets[self.active_widget_idx]
        if widget.interactive:
            return widget
        return self.next_widget()

    def get_widget(self, y, x):
        for widget in self.iter_widgets():
            if widget.bx <= x < widget.bx + widget.bw and \
                    widget.by <= y < widget.by + widget.bh:
                return widget.get_widget(y, x)
        return self

    def find_closest_widget(self, y, x, direction, current_widget):
        min_dist = 0
        closest = None

        for widget in self.iter_widgets():
            dist, target = widget.find_closest_widget(y, x, direction, current_widget)
            if target is None:
                continue
            if closest is None or dist < min_dist:
                min_dist = dist
                closest = target

        return min_dist, closest

class Row(Container):
    def add(self, widget, idx=None):
        widget.parent = self
        if idx is not None:
            self.widgets.insert(idx, widget)
        else:
            self.widgets.append(widget)
        self.refresh_heights()
        self.refresh_widths()

    def refresh_widths(self):
        self.w = 0
        for widget in self.iter_widgets():
            self.w += widget.bw

    def refresh_heights(self):
        self.h = 0
        for widget in self.iter_widgets():
            if widget.bh > self.h:
                self.h = widget.bh

    def resize(self, height, width, bounds=False):
        super().resize(height, width, bounds)

        expanded_widgets = 0
        for widget in self.iter_widgets():
            if widget.expandx:
                expanded_widgets += 1
            else:
                width -= widget.bw

        if expanded_widgets:
            avg_width = width / expanded_widgets
            counter = 0
            widths = []
            for i in range(expanded_widgets):
                counter = (counter + avg_width) - int(counter)
                widths.append(int(counter))
            if sum(widths) < width:
                widths[-1] += 1

        for widget in self.iter_widgets():
            width  = widths.pop() if widget.expandx else widget.bw
            height = self.h if widget.expandy else widget.bh
            widget.resize(height, width, bounds=True)

    def draw_func(self, y, x):
        for widget in self.iter_widgets():
            widget.move(y, x)
            widget.draw()
            x += widget.bw


class Frame(Container):
    def add(self, widget, idx=None):
        widget.set_parent(self)
        if idx is not None:
            self.widgets.insert(idx, widget)
        else:
            self.widgets.append(widget)
        self.refresh_heights()
        self.refresh_widths()

    def refresh_heights(self):
        self.h = 0
        for widget in self.iter_widgets():
            self.h += widget.bh

    def refresh_widths(self):
        self.w = 0
        for widget in self.iter_widgets():
            if widget.bw > self.w:
                self.w = widget.bw

    def center_contents(self, x=True, y=True):
        if x:
            widgets = self.widgets
            self.widgets = []
            for widget in widgets:
                row = Row(expandx=True)
                row.add(Separator(expandx=True))
                row.add(widget)
                row.add(Separator(expandx=True))
                self.add(row)
        if y:
            self.add(Separator(expandy=True), idx=0)
            self.add(Separator(expandy=True))

    def draw_func(self, y, x):
        for widget in self.iter_widgets():
            widget.move(y, x)
            widget.draw()
            y += widget.bh

    def resize(self, height, width, bounds=False):
        super().resize(height, width, bounds)
        self.resize_widgets()

    def resize_widgets(self):
        height = self.h

        expanded_widgets = 0
        for widget in self.iter_widgets():
            if widget.expandy:
                expanded_widgets += 1
            else:
                height -= widget.bh

        if expanded_widgets:
            avg_height = height / expanded_widgets
            counter = 0
            heights = []
            for i in range(expanded_widgets):
                counter = (counter + avg_height) - int(counter)
                heights.append(int(counter))
            if sum(heights) < height:
                heights[-1] += 1

        for widget in self.iter_widgets():
            height = heights.pop() if widget.expandy else widget.bh
            width  = self.w if widget.expandx else widget.bw
            widget.resize(height, width, bounds=True)


class FloatingFrame(Frame):
    def __init__(self, *widgets, **kwargs):
        super().__init__(*widgets, **kwargs)

    def on_press(self, button, y, x):
        if button == L_MOUSE_DOWN:
            self.start_y = y
            self.start_x = x

    def on_drag(self, button, y, x):
        if button == L_MOUSE_DOWN:
            dy = y - self.start_y
            dx = x - self.start_x
            if dx == 0 and dy == 0:
                return
            self.by += dy
            self.bx += dx
            self.start_x = x
            self.start_y = y
            self.request_redraw()

    def on_release(self, button, y, x):
        if button == L_MOUSE_DOWN:
            dy = y - self.start_y
            dx = x - self.start_x
            if dx == 0 and dy == 0:
                return
            self.by += dy
            self.bx += dx
            self.request_redraw()

class CenterFrame(Frame):
    def __init__(self, *widgets, **kwargs):
        super().__init__()

        self.grown = False

        self.frame = Frame(*widgets, **kwargs)
        self.expandy = True
        self.expandx = True

        self.top_sep = Separator(expandy=True)
        self.bottom_sep = Separator(expandy=True)
        self.left_sep = Separator(expandx=True)
        self.right_sep = Separator(expandx=True)

        self.row = Row(
            self.left_sep, self.frame, self.right_sep,
            expandx=True
        )

        super().add(self.top_sep)
        super().add(self.row)
        super().add(self.bottom_sep)

    def shrink(self, duration=0.2, dt=0.02):
        if not self.grown:
            raise Exception("CenterFrame is already shrunk")

        self.frame.expandx = False
        self.frame.expandy = True
        self.row.expandx = True
        self.row.expandy = False

        self.top_sep.display = True
        self.bottom_sep.display = True
        self.left_sep.display = True
        self.right_sep.display = True

        self.frame.resize(self.h, self.w, bounds=True)
        min_h, min_w = self.frame.get_min_area()

        t = 0
        curses.curs_set(0)

        while True:
            new_h = self.h - (self.h - min_h) * (t / duration)
            new_w = self.w - (self.w - min_w) * (t / duration)
            self.frame.resize(int(new_h), int(new_w), bounds=True)
            self.row.bh = self.frame.bh
            self.row.bw = self.frame.bw
            self.resize_widgets()
            self.request_redraw()
            time.sleep(dt)
            t += dt
            if t > duration:
                break

        self.grown = False
        self.frame.resize(min_h, min_w, bounds=True)
        self.row.bh = self.frame.bh
        self.row.bw = self.frame.bw

        curses.curs_set(1)
        self.resize_widgets()
        self.request_redraw()
        self.request_refocus()

    def grow(self, duration=0.2, dt=0.02):
        if self.grown:
            raise Exception("CenterFrame is already grown")

        t = 0
        max_h, max_w = self.h, self.w
        bh, bw = self.frame.bh, self.frame.bw
        curses.curs_set(0)

        while True:
            new_h = bh + (max_h - bh) * (t / duration)
            new_w = bw + (max_w - bw) * (t / duration)
            self.frame.resize(int(new_h), int(new_w), bounds=True)
            self.row.bh = self.frame.bh
            self.row.bw = self.frame.bw
            self.resize_widgets()
            self.request_redraw()
            time.sleep(dt)
            t += dt
            if t > duration:
                break

        self.grown = True

        self.frame.expandx = True
        self.frame.expandy = True
        self.row.expandx = True
        self.row.expandy = True

        self.top_sep.display = False
        self.bottom_sep.display = False
        self.left_sep.display = False
        self.right_sep.display = False

        curses.curs_set(1)
        self.resize_widgets()
        self.request_redraw()
        self.request_refocus()

    def add(self, widget, idx=None):
        self.frame.add(widget, idx)


class Window:
    def __init__(self):
        self.frame = Frame()
        self.floating_widgets = []
        self.frame.set_parent(self)
        self.active_widget = None
        self.pressed_button = 0

    def request_focus(self, widget):
        self.active_widget = widget.focus()

    def request_refocus(self):
        if self.active_widget:
            self.active_widget.focus()

    def request_redraw(self):
        self.redraw()

    def start(self):
        try:
            curses.wrapper(self.wrapper)
        except KeyboardInterrupt:
            pass

    def redraw(self):
        STDSCR.erase()
        self.frame.draw()
        if self.floating_widgets:
            for widget in self.floating_widgets:
                widget.draw()
        STDSCR.refresh()

    def focus(self, widget):
        self.active_widget = widget
        if self.active_widget:
            self.active_widget.focus()

    def jump_widget(self, direction):
        y, x = 0, 0
        if self.active_widget:
            y, x = self.active_widget.y, self.active_widget.x

        _, widget = self.frame.find_closest_widget(y, x, direction,  self.active_widget)
        if widget:
            self.active_widget = widget
            self.active_widget.focus()

    def cycle_widgets(self):
        widget = self.frame.next_widget()
        if widget:
            self.active_widget = widget
            self.active_widget.focus()
        else:
            widget = self.frame.next_widget()
            if widget:
                self.active_widget = widget
                self.active_widget.focus()

    def next_widget(self):
        return None

    def center_contents(self, x=True, y=True):
        self.frame.center_contents(y, x)

    def resize(self):
        self.frame.resize(*STDSCR.getmaxyx())
        self.redraw()

    def wrapper(self, stdscr):
        global STDSCR
        STDSCR = stdscr

        curses.mousemask(
            curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION);
        #stdscr.nodelay(1)
        curses.mouseinterval(0)

        builtins.print('\033[?1003h')


        self.resize()
        #self.redraw()
        self.cycle_widgets()

        while True:
            ch = STDSCR.getch()
            if ch == curses.KEY_RESIZE:
                self.resize()
            elif ch == ord("\t"):
                self.cycle_widgets()
            #elif ch == ord("h"):
            #    self.jump_widget((-1, 0))
            #elif ch == ord("j"):
            #    self.jump_widget((0, 1))
            #elif ch == ord("k"):
            #    self.jump_widget((0, -1))
            #elif ch == ord("l"):
            #    self.jump_widget((1, 0))
            elif ch == curses.KEY_MOUSE:
                self.handle_mouse()
            elif self.active_widget:
                self.active_widget.on_key(ch)

    def handle_mouse(self):
        _, x, y, _, b = curses.getmouse()

        if b == MOUSE_DRAG:
            if self.dragged_widget:
                self.dragged_widget.on_drag(self.pressed_button, y, x)
        elif b in { L_MOUSE_UP, M_MOUSE_UP, R_MOUSE_UP }:
            if b * 2 == self.pressed_button:
                self.dragged_widget.on_release(self.pressed_button, y, x)
                self.dragged_widget = None
                self.pressed_button = 0

        elif b in { L_MOUSE_DOWN, M_MOUSE_DOWN, R_MOUSE_DOWN }:
            if not self.pressed_button:
                clicked_floating = False
                for fwidget in self.floating_widgets:
                    if fwidget.bx <= x <= fwidget.bx + fwidget.w:
                        if fwidget.by <= y <= fwidget.by + fwidget.h:
                            widget = fwidget.get_widget(y, x)
                            clicked_floating = True
                            break

                if not clicked_floating:
                    widget = self.frame.get_widget(y, x)

                if not widget:
                    return

                self.dragged_widget = widget
                self.pressed_button = b
                self.dragged_widget.on_press(self.pressed_button, y, x)
        

    def add(self, widget, idx=None):
        widget.parent = self
        if isinstance(widget, FloatingFrame):
            self.floating_widgets.append(widget)
        else:
            self.frame.add(widget, idx)

    def set_layout(self, *widgets):
        self.frame.clear()
        for widget in widgets:
            widget.parent = self
            self.frame.add(widget)


def login(button):
    return
    if center_frame.grown:
        center_frame.frame.set_title("LOGIN")
        center_frame.shrink()
    else:
        center_frame.frame.set_title(None)
        center_frame.grow()

if __name__ == "__main__":
    tui = Window()

    username_input = Input(width=20, borders=Borders(CURVED))
    password_input = Input(fill_char="*", width=20, borders=Borders(CURVED))
    login_box = Frame(
        Row(Label("Username", valign="center", expandy=True), username_input),
        Row(Label("Password", valign="center", expandy=True), password_input),
        Button("Login", login)
    )
    floating_frame = FloatingFrame(
        login_box,
        x=5, y=5,
        borders=Borders(CURVED, title="LOGIN", align="center")
    )
    tui.add(floating_frame)
    from random import randint
    for i in range(10):
        tui.add(Row(
            Label(str(randint(0,99999999))),
            Label(", "),
            Label(str(randint(0,99999999))),
            Label(", "),
            Label(str(randint(0,99999999)))
        ))

    tui.start()
