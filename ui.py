import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf


stuff = [["Test 1", "./Example Covers/test cover1.jpg"],
         ["Test 2", "./Example Covers/test cover 2.jpg"],
         ["Test 3", "./Example Covers/test cover 3.jpg"],
         ["Test 4", "./Example Covers/test cover 4.jpg"]]

titleFlow = Gtk.FlowBox()
titleFlow.set_valign(Gtk.Align.START)

window_width = 700
preview_width = window_width/2

class LibraryManager(Gtk.Window):


    def __init__(self):
        Gtk.Window.__init__(self, title="Library Manager")
        titleScroll = Gtk.ScrolledWindow()
        titleScroll.add(titleFlow)

        self.set_default_size(window_width, 400)
        self.add(titleScroll)
        self.show_all()

    def add_title(self, title_object):
        button = Gtk.Button()
        #button.set_label(title_object[0])
        pixbuf = Pixbuf.new_from_file_at_scale(title_object[1], -1, preview_width, True)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        button.add(img)
        print('added a cover: ' + title_object[0])
        return button

    def populate_titles(self):
        for title in stuff:
            titleFlow.add(self.add_title(title))
        self.show_all()

mainWindow = LibraryManager()
mainWindow.populate_titles()
mainWindow.connect("delete-event", Gtk.main_quit)
Gtk.main()
