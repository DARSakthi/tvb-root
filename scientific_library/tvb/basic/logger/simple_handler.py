# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#
"""
This module contains a simple file handlers used to log messages
for different parts of application.

.. moduleauthor:: Calin Pavel <calin.pavel@codemart.ro>
"""

import os
from logging.handlers import TimedRotatingFileHandler
from tvb.basic.profile import TvbProfile



class SimpleTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    This is a custom rotating file handler which computes the full path for log file 
    depending on the TVB configuration.
    """


    def __init__(self, filename, when='h', interval=1, backupCount=0):
        """
        Only set our logging path, and call superclass.
        """
        log_file = os.path.join(TvbProfile.current.TVB_LOG_FOLDER, filename)
        TimedRotatingFileHandler.__init__(self, log_file, when, interval, backupCount)
    
    
        
