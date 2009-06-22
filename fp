#!/usr/bin/env python
##    Fonty Python Copyright (C) 2006,2007,2008,2009 Donn.C.Ingle
##    Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##    This file is part of Fonty Python.
##    Fonty Python is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    Fonty Python is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

import fontypythonmodules.i18n

import os
## Just clear up some sad facts:
if os.name != "posix": sys.exit(_("Sorry, only Gnu/Linux is supported at the moment."))

## start the show!
import fontypythonmodules.start
