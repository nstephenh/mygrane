import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

stuff = ["A comic","ANother comic","Number 4","Stuff","Ryan","Yet another thing"]

titleFlow = Gtk.FlowBox()
titleFlow.set_valign(Gtk.Align.START)

class LibraryManager(Gtk.Window):


    def __init__(self):
        Gtk.Window.__init__(self, title="Library Manager")
        titleScroll = Gtk.ScrolledWindow()
        titleScroll.add(titleFlow)

        self.set_default_size(600, 700)
        #self.populateTitles()
        self.add(titleScroll)
        self.show_all()

    def addTitle(self, titleObject):
        button = Gtk.Button()
        button.set_label(titleObject)
        print('added a button: ' + titleObject)
        return button
    def populateTitles(self):
        for title in stuff:
            titleFlow.add(self.addTitle(title))
        self.show_all()


mainWindow = LibraryManager()
mainWindow.populateTitles()
mainWindow.connect("delete-event", Gtk.main_quit)
Gtk.main()
