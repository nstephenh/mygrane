import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('GdkPixbuf', '2.0')
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

import zipfile

from comic import Comic



class ViewerWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)


        PageFlow = Gtk.FlowBox()
        PageFlow.set_valign(Gtk.Align.START)
        PageFlow.set_max_children_per_line(1)
        PageFlow.set_selection_mode(Gtk.SelectionMode.NONE)

        PageScroll = Gtk.ScrolledWindow()
        PageScroll.add(PageFlow)
        PageScroll.show()


        self.add(PageScroll)
        self.set_default_size(600, 1000)
        self.addPages(Comic("/home/nsh/Documents/Comics/format definition", "Punisher War Journal 001 (2007).ve.cbz"))
        self.show_all()
        # self.connect with a resize event to reload pages

    def addPages(self, issue):
        zf = zipfile.ZipFile(issue.containing_directory + "/" + issue.file)
        for file_in_zip in zf.namelist():
            if ".jpg" in file_in_zip.lower() or ".png" in file_in_zip.lower():
                print(file_in_zip)
                loader = PixbufLoader()
                loader.write(zf.read(file_in_zip))
                loader.close()
                thumbnail = loader.get_pixbuf()
                h = thumbnail.get_height()
                w = thumbnail.get_width()
                r = h/w  # Preserve Aspect Ratio
                windowwidth= self.get_size()[0]
                pixbuf = Pixbuf.scale_simple(thumbnail, windowwidth, windowwidth*r, True)
                self.get_child().get_child().get_child().add(Gtk.Image.new_from_pixbuf(pixbuf))


print("Test")
mainWindow = ViewerWindow()
mainWindow.connect("delete-event", Gtk.main_quit)
Gtk.main()