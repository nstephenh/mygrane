import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

from collection import Series, Collection
from comic import Comic
from preferences import *
from subprocess import call


scandirectory = "~/Documents/Comics/Test"

global stuff

global titleFlow
titleFlow = Gtk.FlowBox()
titleFlow.set_valign(Gtk.Align.START)

global dastack
dastack = Gtk.Stack()
dastack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
dastack.set_transition_duration(1000)

window_width = 700
preview_width = window_width/2


class LibraryManager(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        maintitleScroll = Gtk.ScrolledWindow()
        maintitleScroll.add(titleFlow)
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

        global stuff
        stuff = Collection("/home/nsh/Documents/Comics/test2/")
        self.populate_titles(stuff, titleFlow)

        self.set_default_size(window_width, 400)
        dastack.add(maintitleScroll)
        dastack.set_visible_child(maintitleScroll)
        self.add(dastack)
        self.show_all()

    def add_title(self, title_object):
        button = Gtk.Button()
        img = Gtk.Image.new_from_pixbuf(title_object.thumbnail)
        button.add(img)
        print('added a cover: ' + title_object.file)
        switch = type(title_object)
        if switch is Comic:
            button.connect("clicked", self.on_comic_click, title_object.containing_directory + "/" + title_object.file)
        elif switch is Series:
            button.connect("clicked", self.on_series_click, title_object.file)
        return button

    def populate_titles(self, collection, flow):
        for title in collection.contains:
            flow.add(self.add_title(title))
        self.set_focus()
        self.show_all()

    def on_viewer_changed(self):
        pass

    def on_series_click(self, button, dir_to_open):
        #Switch the window to something else
        newFlow = Gtk.FlowBox()
        newFlow.set_valign(Gtk.Align.START)

        self.populate_titles(Collection(dir_to_open), flow=newFlow)
        newtitleScroll = Gtk.ScrolledWindow()
        newtitleScroll.add(newFlow)
        newtitleScroll.show()
        dastack.add(newtitleScroll)
        dastack.set_visible_child(newtitleScroll)
        self.show_all()

    def on_comic_click(self, button, file_to_open):
        call(["evince" + ' "' + file_to_open + '"', "-1"], shell=True)
        #os.system("evince" + ' "' + file_to_open + '"')
        print(file_to_open)

mainWindow = LibraryManager()
mainWindow.connect("delete-event", Gtk.main_quit)
Gtk.main()
