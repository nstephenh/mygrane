import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


from collection import Series, Collection
from comic import Comic
from preferences import *
from subprocess import call

global stuff

global titleFlow
titleFlow = Gtk.FlowBox()
titleFlow.set_valign(Gtk.Align.START)

global dastack
dastack = Gtk.Stack()
dastack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
dastack.set_transition_duration(1000)

import preferences

window_width = preferences.window_width
preview_width = preferences.cover_width


class LibraryManager(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.mainTitleScroll = Gtk.ScrolledWindow()
        self.mainTitleScroll.add(titleFlow)
        self.set_default_size(window_width, 400)


        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Library Manager"

        viewer_store = Gtk.ListStore(str)
        for viewer in viewers:
            viewer_store.append([viewer])

        viewselect = Gtk.ComboBox.new_with_model(viewer_store)
        viewselect.connect("changed", self.on_viewer_changed)

        #hb.add(viewselect)

        back_button = Gtk.Button("<")
        back_button.connect("clicked", self.view_library)
        hb.add(back_button)

        self.set_titlebar(hb)
        self.show_all()
        global stuff
        stuff = Collection(preferences.library_directory)
        self.populate_titles(stuff, titleFlow)

        self.set_default_size(window_width, 400)
        dastack.add(self.mainTitleScroll)
        dastack.set_visible_child(self.mainTitleScroll)
        self.add(dastack)
        self.show_all()

    def add_title(self, title_object):
        title_object.set_thumbnail()
        button = Gtk.Button()
        img = Gtk.Image.new_from_pixbuf(title_object.thumbnail)
        button.add(img)
        print('added a cover: ' + title_object.file)
        switch = type(title_object)
        if switch is Comic:
            button.connect("clicked", self.on_comic_click, title_object.containing_directory + "/" + title_object.file)
        elif switch is Series:
            button.connect("clicked", self.on_series_click, title_object)
        return button

    def view_library(self, button):
        dastack.set_visible_child(self.mainTitleScroll)
        self.show_all()

    def populate_titles(self, collection, flow):
        for title in collection.contains:
            flow.add(self.add_title(title))
        self.set_focus()
        #self.show_all()

    def on_viewer_changed(self):
        pass

    def on_series_click(self, button, series):
        #Switch the window to something else
        newFlow = Gtk.FlowBox()
        newFlow.set_valign(Gtk.Align.START)

        self.populate_titles(series.to_collection(), flow=newFlow)
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


try:
    os.mkdir(datadir)
except FileExistsError:
    pass
mainWindow = LibraryManager()
mainWindow.connect("delete-event", Gtk.main_quit)
Gtk.main()
