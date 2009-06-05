#!/usr/bin/env python
##	Fonty Python Copyright (C) 2006,2007,2008,2009 Donn.C.Ingle
##	Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##	This file is part of Fonty Python.
##	Fonty Python is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	Fonty Python is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.


import fontypythonmodules.i18n
import fontypythonmodules.sanitycheck
import fontypythonmodules.fpversion

import os, sys, glob, fnmatch
from distutils.core import setup, Extension
import distutils.command.install_data

## Code borrowed from wxPython's setup and config files
## Thanks to Robin Dunn for the suggestion.
## I am not 100% sure what's going on, but it works!
def opj(*args):
	path = os.path.join(*args)
	return os.path.normpath(path)
	
# Specializations of some distutils command classes
class wx_smart_install_data(distutils.command.install_data.install_data):
	"""need to change self.install_dir to the actual library dir"""
	def run(self):
		install_cmd = self.get_finalized_command('install')
		self.install_dir = getattr(install_cmd, 'install_lib')
		return distutils.command.install_data.install_data.run(self)
		
def find_data_files(srcdir, *wildcards, **kw):
	# get a list of all files under the srcdir matching wildcards,
	# returned in a format to be used for install_data
	
	## A list of partials within a filename that would disqualify it
	## from appearing in the tarball.
	badnames=[".pyc","~","no_"]

	def walk_helper(arg, dirname, files):
		if 'CVS' in dirname:
			return
		names = []
		lst, wildcards = arg
		for wc in wildcards:
			wc_name = opj(dirname, wc)
			for f in files:
				filename = opj(dirname, f)
				#if ".pyc" not in filename and "~" not in filename:
				## This hairy looking line excludes the filename
				## if any part of one of  badnames is in it:
				L=len([bad for bad in badnames if bad in filename])
				if L == 0:
					print "USING:",filename
					if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
						names.append(filename)
		if names:
			lst.append( (dirname, names ) )

	file_list = []
	recursive = kw.get('recursive', True)
	if recursive:
		os.path.walk(srcdir, walk_helper, (file_list, wildcards))
	else:
		walk_helper((file_list, wildcards),
					srcdir,
					[os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
	return file_list
	
	
## This is a list of files to install, and where:
## Make sure the MANIFEST.in file points to all the right 
## directories too.
files = find_data_files('fontypythonmodules/', '*.*')

## Jan 20 2008 - Add an icon and .desktop file
## Unsure about the absolute path to /usr/share
## but this works on my system.
files.append( ('/usr/share/pixmaps',['fontypython.png']) )
files.append( ('/usr/share/applications',['fontypython.desktop']) )

setup(name = "fontypython",
	version = fontypythonmodules.fpversion.version,
	description = fontypythonmodules.strings.description,
	author = "Donn.C.Ingle",
	author_email = fontypythonmodules.strings.contact,
	license = "GNU GPLv3",
	url = "https://savannah.nongnu.org/projects/fontypython/",
	packages = ['fontypythonmodules'],
	data_files = files,
	## Borrowed from wxPython too:
	## Causes the data_files to be installed into the modules directory.
	## Override some of the default distutils command classes with my own.
	cmdclass = { 'install_data':	wx_smart_install_data },

	#'fontypython' and 'fp' are in the root.
	scripts = ["fontypython", "fp"],
long_description = fontypythonmodules.strings.long_description,
	classifiers=[
	  'Development Status :: 4 - Beta',
	  'Environment :: X11 Applications :: GTK',
	  'Intended Audience :: End Users/Desktop',
	  'Intended Audience :: Developers',
	  'License :: OSI Approved :: GNU General Public License (GPL)',
	  'Operating System :: POSIX :: Linux',
	  'Programming Language :: Python',
	  'Topic :: Desktop Environment',
	  'Topic :: Text Processing :: Fonts'
	  ]	
)
