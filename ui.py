import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

from collection import Collection
from preferences import *

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
        self.set_default_size(window_width, 400)


        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Library Manager"

        viewer_store = Gtk.ListStore(str)
        for viewer in viewers:
            viewer_store.append([viewer])

        viewselect = Gtk.ComboBox.new_with_model(viewer_store)
        viewselect.connect("changed", self.on_viewer_changed)

        hb.add(viewselect)
        self.set_titlebar(hb)

        print("Scanning files...")
        global stuff
        stuff = Collection("../../../Documents/Comics/Test/")
        self.populate_titles()

        self.set_default_size(window_width, 400)
        self.add(titleScroll)
        self.show_all()

    def add_title(self, title_object):
        button = Gtk.Button()
        img = Gtk.Image.new_from_pixbuf(title_object.thumbnail)
        button.add(img)
        print('added a cover: ' + title_object.file)
        return button

    def populate_titles(self):
        for title in stuff.contains:
            titleFlow.add(self.add_title(title))
        self.set_focus()

    def on_viewer_changed(self):
        pass
mainWindow = LibraryManager()
mainWindow.connect("delete-event", Gtk.main_quit)
Gtk.main()
