import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

from collection import Series

scandirectory = "~/Documents/Comics/Test"

global stuff

titleFlow = Gtk.FlowBox()
titleFlow.set_valign(Gtk.Align.START)

window_width = 700
preview_width = window_width/2


class LibraryManager(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        titleScroll = Gtk.ScrolledWindow()
        titleScroll.add(titleFlow)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Library Manager"
        self.set_titlebar(hb)

        print("Scanning files...")
        global stuff
        stuff = Series("../../../Documents/Comics/Test/").contains
        self.populate_titles()

        self.set_default_size(window_width, 400)
        self.add(titleScroll)
        self.show_all()

    def add_title(self, title_object):
        button = Gtk.Button()
        h = title_object.thumbnail.get_height()
        w = title_object.thumbnail.get_width()
        r = h/w  # Preserve Aspect Ratio
        pixbuf = Pixbuf.scale_simple(title_object.thumbnail, preview_width, preview_width*r, True)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        button.add(img)
        print('added a cover: ' + title_object.file)
        return button

    def populate_titles(self):
        for title in stuff:
            titleFlow.add(self.add_title(title))
        self.show_all()

mainWindow = LibraryManager()
mainWindow.populate_titles()
mainWindow.connect("delete-event", Gtk.main_quit)
Gtk.main()
