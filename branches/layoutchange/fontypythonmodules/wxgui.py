## Fonty Python Copyright (C) 2017 Donn.C.Ingle
## Contact: donn.ingle@gmail.com - I hope this email lasts.
##
## This file is part of Fonty Python.
## Fonty Python is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Fonty Python is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

import locale
import strings
import fontybugs
import fpsys # Global objects
import fpversion
## Now, bring in all those big modules
import wx


## June 25th 2016
## Remarking these two lines because they are causing a segfault:
##  ../src/common/stdpbase.cpp(62): assert "traits" failed in Get(): 
##  create wxApp before calling this
##  Segmentation fault (core dumped)
##
##  I do not know how to test or fix this, hence simply removing it.
##  AFAICT, stock buttons will be in the system language.
##
## Setup wxPython to access translations : enables the stock buttons.
#langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
#mylocale = wx.Locale( langid )

## Fetch my own pubsub stuff
from pubsub import * #I want all the topics.
ps = CPubsub()

## Fetch the dialogue classes *About, Settings, Help, etc.*
import dialogues

## DND: NB--Comments that have DND: in them mean DO NOT DELETE. They are used by me via grep on the cli.


from gui_FontSources import *
from gui_FontView import *
from gui_PogTargets import *


class StatusBar(wx.StatusBar):
    """
    The status bar
    """
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1) # default style is good

        ##Sept2017
        ## Test if there's a need to warn about missing .fonts dir.
        try:
            fpsys.iPC.probeNoFontsDirError()
        except fontybugs.NoFontsDir as e:
            no_fonts_dir = True
            shorterr = e.short_unicode_of_error()
        else:
            no_fonts_dir = False

        ## Field 1 is Welcome...
        ## Field 2 is normal conversation.
        ## Field 3 <if missing user fonts dir> is the warning message.
        ## Last field "gripper" (32px)
        self.SetFieldsCount( 4 if no_fonts_dir else 3 )

        self.SetStatusText( _("Welcome to Fonty Python, vers %s") % fpversion.version, 0)

        if no_fonts_dir:
            self.SetStatusText( shorterr, 2)
            self.SetStatusWidths([300,-2,-1,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*3) #SB_SUNKEN is not available to me. 
        else:
            self.SetStatusWidths([300,-2,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*2)

    def Report(self, msg):
        self.SetStatusText(msg, 1)


class MainFrame(wx.Frame):
    """
    The main frame for the app. Has some functionality for menu items.
    """
    def __init__(self,parent,title) :
        ## Draw the frame
        title = title + "   -   " + locale.getpreferredencoding()
        wx.Frame.__init__(self,parent,-1,title,fpsys.config.pos,fpsys.config.size)

        #print "Main frame:", self.GetSizeTuple()[0]

        ## Try to show an icon
        try:
            image = wx.Image(fpsys.mythingsdir + 'fplogo.png', wx.BITMAP_TYPE_PNG)
            image = image.ConvertToBitmap()
            icon = wx.EmptyIcon()
            icon.CopyFromBitmap(image)
            self.SetIcon(icon)
        except:
            pass


        ## STATUS BAR
        ## ---------------------------------------
        self.sb = StatusBar(self)
        self.SetStatusBar(self.sb)

        ## MENUS
        ## ---------------------------------------
        self.menuBar = wx.MenuBar()

        ## FILE MENU : Changed to "Tools" menu Sep 2009
        menu1 = wx.Menu()
        menu1.Append(101, _("&Settings\tCtrl+S"), _("Change settings"))
        menu1.AppendSeparator()
        ## Jan 18 2008
        menu1.Append( 102, _("&Check fonts"), _("Find those fonts that crash Fonty.") )
        menu1.Append( 103, _("&Purge Pog.See TogglePurgeMenuItem for actual string."), _("Remove all ghost fonts from the selected Pog.") )

        self.MENUPURGE = menu1

        self.exit = menu1.Append(104, _("&Exit"), _("Close the app"))
        self.menuBar.Append(menu1, _("&Tools"))


        ## SELECT MENU: June 2009
        menu3 = wx.Menu()
        menu3.Append( 301, _("&Select ALL the source fonts"), _("Select ABSOLUTELY ALL the fonts in the chosen source."))
        menu3.Append( 302, _("&Clear ENTIRE selection"), _("Clear the selection completely.") )
        self.menuBar.Append(menu3, _("&Selection"))
        self.MENUSELECTION = menu3

        ## HELP MENU
        menu2 = wx.Menu()
        menu2.Append(201, _("H&elp\tF1"))
        menu2.Append(202, _("&About"))
        self.menuBar.Append(menu2, _("&Help"))

        self.SetMenuBar(self.menuBar)

        ## Setup the ESC key and the LEFT / RIGHT keys
        accel = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.exit.GetId()),
            (wx.ACCEL_CTRL, wx.WXK_RIGHT, wx.ID_FORWARD),
            (wx.ACCEL_CTRL, wx.WXK_LEFT, wx.ID_BACKWARD)
            ])
        self.SetAcceleratorTable(accel)

        ## Bind the Left and Right key shortcuts.	
        self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_FORWARD )
        self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_BACKWARD )

        ## The X close window button.
        self.Bind( wx.EVT_CLOSE, self.onHandleESC )

        ## Bind events for the menu items
        self.Bind(wx.EVT_MENU, self.onHandleESC, self.exit)
        self.Bind(wx.EVT_MENU, self.menuSettings, id = 101)
        self.Bind(wx.EVT_MENU, self.menuCheckFonts, id = 102 )
        self.Bind(wx.EVT_MENU, self.menuPurgePog, id = 103 )
        self.Bind(wx.EVT_MENU, self.menuAbout, id = 202)
        self.Bind(wx.EVT_MENU, self.menuHelp, id = 201)
        # June 2009
        self.Bind(wx.EVT_MENU, self.menuSelectionALL, id=301)
        self.Bind(wx.EVT_MENU, self.menuSelectionNONE, id=302)


        ## THE MAIN GUI
        ## ------------------------------------------------------------------

        ## A temporary switch to test out various ideas
        self.whatgui = 4

        MINSCREENWIDTH = 800 #old skool

        ## PRIMARY GUI
        ## ===========
        ## No splitters at all.
        ## Box across: two
        ## Left box: Box vertical: two (source/target)
        ## Right box: Fontview
        ## :- kind of shape.

        ## NOTE:
        ## =====
        ## I tried a splitter window of 2 across
        ## left: a panel with sizer of two high of: source, then target guis
        ## right: fontview
        ## This one freezes the app when you resize to the right... :(
        ## Hard to reproduce. I used gdb and got it to crash, then
        ## did a 'bt' and saw some complaints about get text extents
        ## might be a bug in my font drawing code..?

        minw = 320
        fvminw = MINSCREENWIDTH - minw
        ms = wx.Size(minw,1)

        self.panelFontSources = FontSourcesPanel(self)
        self.panelFontSources.SetMinSize(ms)

        self.panelTargetPogChooser = TargetPogChooser(self)
        self.panelTargetPogChooser.SetMinSize(ms)

        self.fontViewPanel = FontViewPanel(self)
        self.fontViewPanel.SetMinSize(wx.Size(fvminw,1))

        stsizer = wx.BoxSizer(wx.VERTICAL)
        stsizer.Add( self.panelFontSources, 1, wx.EXPAND|wx.ALL,border = 5 )
        stsizer.Add( self.panelTargetPogChooser, 1, wx.EXPAND|wx.ALL,border = 5 )


        lrsizer = wx.BoxSizer(wx.HORIZONTAL)
        lrsizer.Add( stsizer, 0, wx.EXPAND)
        lrsizer.Add( self.fontViewPanel, 1, wx.EXPAND|wx.ALL, border = 5 )

        self.SetSizer(lrsizer)

        ## Idle/resize idea from here:
        ##https://stackoverflow.com/questions/13479831/what-is-the-simplest-way-of-monitoring-when-a-wxpython-frame-has-been-resized
        self.resized = False
        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.Bind(wx.EVT_SIZE, self.onFrameSize)


        ## GUI ENDS
        ## =============

        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        ## Now to subscribe to have my various def called from other places:
        ps.sub(show_error, self.ErrorBox) ##DND: class MainFrame
        ps.sub(show_error_and_abort, self.ErrorAbort) ##DND: class MainFrame
        ps.sub(show_message, self.MessageBox) ##DND: class MainFrame
        ps.sub(print_to_status_bar, self.StatusbarPrint) ##DND: class MainFrame
        ## Dec 2007 - Used on middle click in gui_Fitmap.py
        ps.sub( menu_settings, self.menuSettings ) ##DND: class MainFrame
        ps.sub( toggle_selection_menu_item, self.toggleSelectionMenuItem ) ##DND: class MainFrame

        ps.sub( toggle_purge_menu_item, self.TogglePurgeMenuItem ) ##DND: class MainFrame


        ## call the big one - the big chief, the big cheese:
        ## This eventually draws all the Fitmaps - giving the middle a width.
        ps.pub( update_font_view ) #DND: It's in gui_FontView.py under class FontViewPanel


        self.SetMinSize(wx.Size(MINSCREENWIDTH,600)) #Old Skool: Assuming monitor size...
        self.Layout()


        ## This is to draw the correct icons depending on cli params.
        self.panelTargetPogChooser.pogTargetlist.SortOutTheDamnImages(False)

    def onFrameSize(self,evt):
        self.resized = True
        evt.Skip()

    def onIdle(self, evt):
        #print "Idle runs"
        if self.resized:
            #print "  Idle updates fontViewPanel"
            ps.pub( update_font_view )
            self.resized = False

    def OnAccelKey(self,evt):
        ps.pub( left_or_right_key_pressed, evt ) #fwd this business on-to a func in gui_FontView.py

    def toggleSelectionMenuItem(self, onoff):
        #HIG says to leave top menu alone and only toggle sub-items.
        self.MENUSELECTION.Enable(301,onoff[0])
        self.MENUSELECTION.Enable(302,onoff[0])

    def StatusbarPrint(self, args):
        self.sb.Report(args[0])

    def MessageBox(self, args):
        dlg = wx.MessageDialog(self, args[0] , _("Warning"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def ErrorBox(self, args):
        dlg = wx.MessageDialog(self, args[0], _("Error"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def ErrorAbort(self, args):
        self.ErrorBox(args) #Pass it along to be displayed
        self.endApp()

    def onHandleESC(self, e) :
        print strings.done
        self.endApp()

    def endApp(self) :
        """
        Save app's vital statistics and exit.
        See the end of start.py where it's actually saved.
        """
        ## Dec 2007 - I was using the wrong func and the
        ## main window kept getting smaller!
        fpsys.config.size = self.GetSizeTuple()

        ##June 2009 - fetch and record the value of the recurse folders checkbox.
        fpsys.config.recurseFolders = app.GetTopWindow().panelFontSources.nb.recurseFolders.GetValue()
        self.Destroy()

    def menuSettings(self, e):
        lastnuminpage, lastpoints, lasttext = fpsys.config.numinpage ,fpsys.config.text, fpsys.config.points
        dlg = dialogues.DialogSettings(self)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            ## Did anything change?
            num = int(dlg.inputPageLen.GetValue())
            points = int(dlg.inputPointSize.GetValue())
            txt = dlg.inputSampleString.GetValue()
            ignoreAdjust = dlg.chkAdjust.GetValue() #Sept 2009
            if (num, txt, points) != (lastnuminpage, lastpoints, lasttext):
                fpsys.config.numinpage = int(num)
                fpsys.config.points = int(points)
                if len(txt) > 0: fpsys.config.text =  txt

            fpsys.config.ignore_adjustments = ignoreAdjust #Sept 2009
            fpsys.config.CMC.SET_CURRENT_APPNAME( dlg.CHOSEN_CHARACTER_MAP) # Oct 2009

            ## Now to refresh things:
            ## Sept 2009 : size change means we need new values for fitmaps
            ps.pub( reset_top_left_adjustments ) ##DND : In ScrolledFontView
            ps.pub( update_font_view )
        dlg.Destroy()

    def menuAbout(self, e):
        dlg =dialogues.DialogAbout(self)
        val = dlg.ShowModal()
        dlg.Destroy()

    def menuHelp(self, e):
        # July 2016
        # =========
        # Made the initial size of the help dialog smaller
        # Was requested by a user who has a small screen
        # ~600px wide is about as narrow as I can get it...
        dlg = dialogues.DialogHelp(self, size=(676, 400))
        val = dlg.ShowModal()
        dlg.Destroy()

    def menuCheckFonts( self, e ):
        """
        Added Jan 18 2008
        User can visit suspicious directories with this tool
        to gather a list of fonts that kill the app. They will be
        marked as such and hereafter be safe to use.
        """
        ## Set startdir to the one our own dircontrol is in
        if fpsys.state.viewpattern == "F":
            startdir = fpsys.state.viewobject.path
        else:
            ##Let's get it from the config object
            startdir = fpsys.config.lastdir
        dlg = dialogues.DialogCheckFonts( self, startdir )
        val = dlg.ShowModal()
        dlg.Destroy()

    def menuSelectionALL(self,e):
        if not fpsys.state.cantick: return # Can't tick if this is False.
        fpsys.state.numticks=0
        vo=fpsys.state.filteredViewObject # We want to select what is FILTERED
        for fi in vo:
            if not fi.inactive:
                fi.ticked=True
                fpsys.state.numticks += 1
        ## Now update the view
        ps.pub( update_font_view )

    def menuSelectionNONE(self,e):
        fpsys.state.numticks=0
        vo=fpsys.state.viewobject # We *REALLY* mean select NONE. So ignore filter.
        for fi in vo:
            if not fi.inactive:
                fi.ticked=False
        ## Now update the view
        ps.pub( update_font_view )

    def TogglePurgeMenuItem(self, vis):
        vis=vis[0]
        #print vis
        #print fpsys.state.viewobject.name
        self.MENUPURGE.Enable(103,vis)

        ## July 2016
        ## =========
        ## Make the label of the menu reflect the view Pog's name
        ## so it's clear which selection counts for purging.
        if vis:
            self.MENUPURGE.SetLabel(103, _("&Purge \"%s\"\tCtrl+P" % fpsys.state.viewobject.name ) )
        else:
            self.MENUPURGE.SetLabel(103, _("&Purge Pog\tCtrl+P")) #Reflect original string, as it's got translations already.


    def menuPurgePog(self,e):
        ##The menu item only becomes active for Pogs that are not installed,
        ##so we can purge without further tests:
        pogname = fpsys.state.viewobject.name
        dlg = wx.MessageDialog(self,_("Do you want to purge %s?\n\nPurging means all the fonts in the pog\nthat are not pointing to actual files\nwill be removed from this pog.") % pogname, _("Purge font?"), wx.YES_NO | wx.ICON_INFORMATION )
        if dlg.ShowModal() == wx.ID_YES:
            ## pog.purge() Raises
            ## 	  PogEmpty
            ## 	  PogInstalled
            try:
                fpsys.state.viewobject.purge()
            except(fontybugs.PogEmpty, fontybugs.PogInstalled),e:
                ps.pub(show_error, unicode( e ))
                ps.pub(print_to_status_bar, _("%s has not been purged.") % pogname)
                return

            ## Update GUI
            ps.pub(print_to_status_bar, _("%s has been purged.") % pogname)

            ps.pub(update_font_view)




# Code for debugging:
##http://wiki.wxpython.org/Widget%20Inspection%20Tool
## Use ctrl+alt+i to open it.
#import wx.lib.mixins.inspection
## Start the main frame and then show it.
class App(wx.App ):# , wx.lib.mixins.inspection.InspectionMixin) :
    """
    The main wxPython app starts here
    """
    def OnInit(self):
        #self.Init()  # initialize the inspection tool

        ## Initial dialogue to inform user about wx unicode version.
        if not "unicode" in wx.PlatformInfo:
            wx.MessageBox(_("I am sorry, but Unicode is not supported by this installation of wxPython. Fonty Python relies on Unicode and will simply not work without it.\n\nPlease fetch and install the Unicode version of python-wxgtk."),
                caption=_("SORRY: UNICODE MUST BE SUPPORTED"),
                style=wx.OK | wx.ICON_EXCLAMATION )
            raise SystemExit

        ## Probe for delayed errors in PathControl
        ## and show them in message boxes.
        try:
            fpsys.iPC.probeAllErrors()

        ## App stopping errors:
        except (fontybugs.NoFontypythonDir, fontybugs.UpgradeFail) as e:
            wx.MessageBox( e.unicode_of_error(),
                caption=_("FATAL ERROR"),
                style=wx.OK | wx.ICON_ERROR )
            ## This one is unrecoverable:
            raise SystemExit

        ## Warning only
        except fontybugs.NoFontsDir as e:
            ## This looks horrible. I will remark it.
            ## The app deals with it in context.
            #    wx.MessageBox( e.unicode_of_error(),
            #        caption=_("WARNING"),
            #        style=wx.OK | wx.ICON_ERROR )
            pass

        # Start a splash screen - which then starts the main frame
        MySplash = FontySplash()
        MySplash.Show()

        return True

class FontySplash(wx.SplashScreen):
        """
        2016 July
        =========
            Trying a diff way to show the splash screen.
            It's a little better. It shows fast and
            remains there while the frame loads behind it.

            Borrowing from the wxPython demo's code.
        """
        def __init__(self, parent=None):
            aBitmap = wx.Bitmap( fpsys.mythingsdir + "splash.png", wx.BITMAP_TYPE_PNG )
            splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
            splashDuration = 1000 # milliseconds

            wx.SplashScreen.__init__(self, aBitmap, splashStyle, splashDuration, parent)
            self.Bind(wx.EVT_CLOSE, self.OnExit)

            # Nice! Kick the show off in x millis.
            self.fc = wx.FutureCall(500,self.showMain)

        def OnExit(self, evt):
            # The program will freeze without this line.
            evt.Skip()	# Make sure the default handler runs too...
            self.Hide()

            # if the timer is still running, force the main frame to start
            if self.fc.IsRunning():
                self.fc.Stop()
                self.showMain()

        def showMain(self):
            ## Oct 2009
            ##  this is the only place I can get the system font family
            fpsys.DFAM = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetFamily()

            frame = MainFrame(None, _("Fonty Python: bring out your fonts!"))
            app.SetTopWindow(frame)

            frame.Show(True)

            if self.fc.IsRunning():
                self.Raise()


#Start the app!
app = App(0)
app.MainLoop()
