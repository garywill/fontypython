## Fonty Python Copyright (C) 2006, 2007, 2008, 2009, 2017 Donn.C.Ingle
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

import wx, os

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
##langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
##mylocale = wx.Locale( langid )


from pubsub import * #I want all the topics.

import fontybugs

import fpsys

from wxgui import ps
from gui_PogChooser import *
from gui_DirChooser import ATree

import fontyfilter

import fpwx

class FontSourcesPanel(wx.Panel):
    """
    A panel to represent the entire Source GUI.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id = -1)#, style = wx.BORDER_RAISED)

        ## Notebook label and icon
        view_icon = fpwx.icon(self, 'icon_source')
        view_label = fpwx.large_label(self,_("Sources: Folders or Pogs") )

        ## A horiz sizer to hold the icon and text
        self.sizer_iconandtext = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_iconandtext.Add( view_icon, 0, wx.TOP |
                wx.BOTTOM | wx.LEFT, border = 4 )

        self.sizer_iconandtext.Add( view_label, 1, wx.LEFT |
                wx.BOTTOM | wx.ALIGN_BOTTOM, border = 6 )

        ## Now the actual notebook
        self.nb = NoteBook(self, name="notebook")

        ## Make a Vertical sizer to hold them.
        self.sizerNotebook = wx.BoxSizer(wx.VERTICAL)

        ## Add them to the sizer.
        self.sizerNotebook.Add(self.sizer_iconandtext, 0, wx.EXPAND)
        self.sizerNotebook.Add(self.nb,1,wx.EXPAND)

        self.SetSizer(self.sizerNotebook)
        self.Layout()

class DirControl(ATree):
    """
    The Directory tree view. Note: Directory names are all UNICODE!
    """
    def __init__(self, parent):
        if fpsys.state.viewpattern == "F":
            startdir = fpsys.state.viewobject.path
        else:
            ##Let's get it from the config object
            lastdir = fpsys.config.lastdir

            if os.path.exists(lastdir):
                startdir = lastdir
            else:
                startdir = os.environ['HOME']
        ATree.__init__(self, parent, startdir) 
        ## NOTE: The click event is bound in the Notebook.

class NoteBook(wx.Notebook):
    """
    THIS IS THE VIEW or SOURCE of fonts.
    Has two tabs - Folders and Pogs
    """
    def __init__(self, parent, name="notebook_not_named"):
        wx.Notebook.__init__(self, parent, style=wx.NB_TOP, name = name)
        self.imlist = wx.ImageList(16, 16)

        pan1 = wx.Panel(self)

        ## THE DIR CONTROL
        self.dircontrol = DirControl(pan1)

        # Get a ref to the dircontrol.
        self.tree = self.dircontrol.GetTreeCtrl()

        ## Add them to a sizer
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add( self.dircontrol,1, wx.EXPAND )
        pan1.SetSizer(box)
        box.Layout()

        self.pogindexselected = 0

        ## The SOURCE POG control
        pan2 = wx.Panel(self)
        page = 0
        s = None
        if fpsys.state.viewpattern  == "P":
            s = fpsys.state.viewobject.name
            if s == "EMPTY": s= None #Very first run, the view will be an EMPTY object.
            page = 1
        self.ctrlPogSource = PogChooser(pan2, whoami="SOURCEPOG", select = s)


        ps.sub( source_pog_has_been_selected, self.OnViewPogClick) ##DND: class NoteBook
        ps.sub( select_no_view_pog, self.SelectNoView) ##DND: class NoteBook
        ps.sub( add_pog_item_to_source, self.AddItem ) #DND: class NoteBook
        ps.sub( remove_pog_item_from_source, self.RemoveItem ) #DND: class NoteBook


        ## Dud tree events, causing bad behaviour:
        ## EVT_LIST_ITEM_SELECTED
        ## EVT_LEFT_UP

        ## Bind to another event solve the problem of 
        ##  EVT_LEFT_UP firing when the little
        ##  open-branch/tree arrow was pressed.
        ##  5.3.2009 Michael Hoeft
        ## Nov 2017: Also subscribe this for use in wxgui - since 
        ## I moved the recurseFolders into there.
        ps.sub( fake_click_the_source_dir_control, self.__onDirCtrlClick )
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.__onDirCtrlClick)

        ## Had a context menu, but not using it.
        #self.tree.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.ctrlPogSource,1,wx.EXPAND)
        pan2.SetSizer(box2)
        box2.Layout()

        self.AddPage(pan1, _("Source Folders"))
        self.AddPage(pan2, _("Source Pogs"))

        # sadly, the artprovider icons suck, and I can't get access 
        # to the "stock items" either. Fuck it. 
        source_folder_icon = self.imlist.Add(
                fpwx.wxbmp('icon_source_folder_16x16') )
        source_pog_icon = self.imlist.Add(
                fpwx.wxbmp('icon_source_pog_16x16') )

        self.AssignImageList(self.imlist)
        self.SetPageImage(0, source_folder_icon)
        self.SetPageImage(1, source_pog_icon)

        self.SetSelection(page)

        # Dec 2017: Remarked this Bind. See notes in old handler
        #self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, 
        # self.onPageChanged) # Bind page changed event

        ## If the app is started with a Folder as the Source, then
        ## check if we must recurse. If so, fake a click to kick that off.
        ## Sept 2017
        if fpsys.state.viewpattern  == "F":
            self.__onDirCtrlClick() # Fake an event


    def onPageChanged(self, e):
        """
        The notebook page change handler.
        Remarked the Bind Dec 2017.
        
        A click on the notebook tabs should not make assumptions
        about what source to select.

        By ignoring this, the new eye icon remains on the last 
        selected directory.

        It's not perfect, because coming back to the dir control
        shows what was selected before, but you can't click on the
        same selection and get a result. You must click-off and 
        click-on to get the view to update.
        
        I moved the UnselectAll call into OnViewPogClick so that
        when you click on an actual source Pog, the tree control
        now moves out of play.

        I leave this code for the future.
        """
        self.ctrlPogSource.ClearLastIndex()
        if self.GetSelection() == 0: # The dircontrol
            #pass
            ## I want to force the dir control to clear the selection.
            ## Reason: When you return to this control (from Pog page),
            ## the selection from last visit is still there. 
            ## Clicking on it again does NOT UPDATE the font view. 
            ## This is wierd. So, clearing the selection makes it moot.

            ## This actually works:
            # wx.CallAfter( self.__onDirCtrlClick)
            # However.. I think it's weird.
            # When you click a tab in the notebook, it should
            # not make assumptions about what you mean.
            self.tree.UnselectAll() # Found this method in the wxpython book.


    def __onDirCtrlClick(self, evt = None):
        if evt:
            # I want this event to eventually arrive in
            # the Atree class; thus Skip()
            # (See gui_DirChooser.py)
            evt.Skip() # Happens when this handler finishes.

        wx.BeginBusyCursor() #Thanks to Suzuki Alex on the wxpython list!
        p = self.dircontrol.GetPath()

        try:
            fpsys.instantiateViewFolder( p, fpsys.config.recurseFolders )
            fpsys.config.lastdir = p
        except fontybugs.FolderHasNoFonts, err:
            pass # update_font_view handles this with a std message.

        ps.pub(reset_to_page_one)# reset before updating!  
        ps.pub(update_font_view)

        wx.EndBusyCursor()
        wx.CallAfter( self.SetFocus )

    def OnViewPogClick(self, args):
        """
        args[0] is pogname, args[1] is pognochange
        """
        # Dec 2017: Force no-selection in dir control
        # so the gui's visual "logic" makes sense: I.e we
        # are now looking at a Pog, not a Folder any more.
        self.tree.UnselectAll()

        ## Check pognochange, it means this is the same pog as last time.
        if args[1]: return

        ## instantiateViewPog calls pog.genList which bubbles:
        ## PogInvalid
        ## BUT - this error only makes sense from the
        ## cli pov. By the time the gui is running, that
        ## pog has been renamed .badpog and therefore 
        ## won't even appear in the list. So, don't bother
        ## catching it.
        fpsys.instantiateViewPog(args[0])

        if fpsys.state.samepogs: #forbid same pogs selection
            ps.pub(clear_targetpog_selection)
        else:
            ps.pub(reset_to_page_one)
        ps.pub(update_font_view)

    def AddItem(self, pogname):
        self.ctrlPogSource.AddItem(pogname[0]) #[0] bit is because pogname is a tuple from pubsub.

    def RemoveItem(self, pogname):
        self.ctrlPogSource.RemoveItem(pogname[0])

    def SelectNoView(self):
        ## Purpose: To select no viewobject and clear view pog list selections
        ## Called when a TARGET item is clicked AND samepogs it True
        wx.BeginBusyCursor()
        self.ctrlPogSource.ClearSelection()
        fpsys.SetViewPogToEmpty()
        wx.EndBusyCursor()
