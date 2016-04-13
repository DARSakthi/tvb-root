# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
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
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""

import os
import cherrypy
import formencode
import threading
import subprocess
from time import sleep
from formencode import validators
from tvb.basic.profile import TvbProfile
from tvb.core.utils import check_matlab_version
from tvb.core.services.settings_service import SettingsService
from tvb.core.services.exceptions import InvalidSettingsException
from tvb.interfaces.web.controllers import common
from tvb.interfaces.web.controllers.decorators import check_admin, using_template, jsonify, handle_error
from tvb.interfaces.web.controllers.users_controller import UserController


class SettingsController(UserController):
    """
    Controller for TVB-Settings web page.
    Inherit from UserController, to have the same fill_default_attributes method (with versionInfo).
    """

    def __init__(self):
        UserController.__init__(self)
        self.settingsservice = SettingsService()


    @cherrypy.expose
    @handle_error(redirect=True)
    @using_template('user/base_user')
    @check_admin
    def settings(self, save_settings=False, **data):
        """Main settings page submit and get"""
        template_specification = dict(mainContent="../settings/system_settings", title="System Settings")
        if save_settings:
            try:
                form = SettingsForm()
                data = form.to_python(data)
                isrestart, isreset = self.settingsservice.save_settings(**data)
                if isrestart:
                    thread = threading.Thread(target=self._restart_services, kwargs={'should_reset': isreset})
                    thread.start()
                    common.add2session(common.KEY_IS_RESTART, True)
                    common.set_important_message('Please wait until TVB is restarted properly!')
                    raise cherrypy.HTTPRedirect('/tvb')
                # Here we will leave the same settings page to be displayed.
                # It will continue reloading when CherryPy restarts.
            except formencode.Invalid, excep:
                template_specification[common.KEY_ERRORS] = excep.unpack_errors()
            except InvalidSettingsException, excep:
                self.logger.error('Invalid settings!  Exception %s was raised' % (str(excep)))
                common.set_error_message(excep.message)
        template_specification.update({'keys_order': self.settingsservice.KEYS_DISPLAY_ORDER,
                                       'config_data': self.settingsservice.configurable_keys,
                                       common.KEY_FIRST_RUN: TvbProfile.is_first_run()})
        return self.fill_default_attributes(template_specification)


    def _restart_services(self, should_reset):
        """
        Restart CherryPy and Backend.
        """
        mplh5 = TvbProfile.current.web.MPLH5_Server_Thread
        if mplh5 is not None:
            mplh5.shutdown()
            mplh5.server_close()
        else:
            self.logger.warning('For some reason the mplh5 never started.')
        cherrypy.engine.exit()

        self.logger.info("Waiting for Cherrypy to shut down ... ")

        sleep(5)

        python_path = TvbProfile.current.PYTHON_INTERPRETER_PATH
        proc_params = [python_path, '-m', 'tvb_bin.app', 'start', TvbProfile.CURRENT_PROFILE_NAME]
        if should_reset:
            proc_params.append('-reset')

        self.logger.info("Starting CherryPy again ... ")
        subprocess.Popen(proc_params, shell=False)


    @cherrypy.expose
    @handle_error(redirect=False)
    @jsonify
    def check_db_url(self, **data):
        """
        Action on DB-URL validate button.
        """
        try:
            storage_path = data[self.settingsservice.KEY_STORAGE]
            if os.path.isfile(storage_path):
                raise InvalidSettingsException('TVB Storage should be set to a folder and not a file.')
            if not os.path.isdir(storage_path):
                try:
                    os.mkdir(storage_path)
                except OSError:
                    return {'status': 'not ok',
                            'message': 'Could not create root storage for TVB. Please check write permissions!'}
            self.settingsservice.check_db_url(data[self.settingsservice.KEY_DB_URL])
            return {'status': 'ok', 'message': 'The database URL is valid.'}
        except InvalidSettingsException, excep:
            self.logger.error(excep)
            return {'status': 'not ok', 'message': 'The database URL is not valid.'}


    @cherrypy.expose
    @handle_error(redirect=False)
    @jsonify
    def validate_matlab_path(self, **data):
        """
        Check if the set path from the ui actually corresponds to a matlab executable.
        """
        submitted_path = data[self.settingsservice.KEY_MATLAB_EXECUTABLE]
        if len(submitted_path) == 0:
            return {'status': 'ok',
                    'message': 'No Matlab/Ocatve path was given. Some analyzers will not be available.'}

        if os.path.isfile(submitted_path):
            version = check_matlab_version(submitted_path)
            if version:
                return {'status': 'ok', 'message': "Valid Matlab/Octave. Found version: '%s'." % (version,)}
            else:
                return {'status': 'not ok', 'message': "Invalid Matlab/Octave. Found version: '%s' ." % (version,)}
        else:
            return {'status': 'not ok', 'message': 'Invalid Matlab/Octave path.'}


class DiskSpaceValidator(formencode.FancyValidator):
    """
    Custom validator for TVB disk space / user.
    """

    def _convert_to_python(self, value, _):
        """
        Validation required method.
        :param value is user-specified value, in MB
        """
        try:
            value = long(value)
            return value
        except ValueError:
            raise formencode.Invalid('Invalid disk space %s. Should be number' % value, value, None)


class PortValidator(formencode.FancyValidator):
    """
    Custom validator for OS Port number.
    """

    def _convert_to_python(self, value, _):
        """ 
        Validation required method.
        """
        try:
            value = int(value)
        except ValueError:
            raise formencode.Invalid('Invalid port %s. Should be number between 0 and 65535.' % value, value, None)
        if 0 < value < 65535:
            return value
        else:
            raise formencode.Invalid('Invalid port number %s. Should be in interval [0, 65535]' % value, value, None)


class ThreadNrValidator(formencode.FancyValidator):
    """
    Custom validator number of threads.
    """

    def _convert_to_python(self, value, _):
        """ 
        Validation required method.
        """
        try:
            value = int(value)
        except ValueError:
            raise formencode.Invalid('Invalid number %s. Should be number between 1 and 16.' % value, value, None)
        if 0 < value < 17:
            return value
        else:
            raise formencode.Invalid('Invalid number %d. Should be in interval [1, 16]' % value, value, None)


class SurfaceVerticesNrValidator(formencode.FancyValidator):
    """
    Custom validator for the number of vertices allowed for a surface
    """
    # This limitation is given by our Max number of colors in pick mechanism
    MAX_VALUE = 256 * 256 * 256 + 1


    def _convert_to_python(self, value, _):
        """ 
        Validation required method.
        """
        msg = 'Invalid value: %s. Should be a number between 1 and %d.'
        try:
            value = int(value)
            if 0 < value < self.MAX_VALUE:
                return value
            else:
                raise formencode.Invalid(msg % (str(value), self.MAX_VALUE), value, None)
        except ValueError:
            raise formencode.Invalid(msg % (value, self.MAX_VALUE), value, None)


class MatlabValidator(formencode.FancyValidator):
    """
    Custom validator for the number of vertices allowed for a surface
    """


    def _convert_to_python(self, value, _):
        """ 
        Validation method for the Matlab Path.
        """
        version = check_matlab_version(value)
        if version:
            return value
        else:
            raise formencode.Invalid('No valid matlab installation was found at the path you provided.', '', None)


class AsciiValidator(formencode.FancyValidator):
    """
    Allow only ascii strings
    """
    def _convert_to_python(self, value, _):
        try:
            return str(value).encode('ascii')
        except UnicodeError:
            raise formencode.Invalid('Invalid ascii string %s' % value, '', None)


class SettingsForm(formencode.Schema):
    """
    Validate Settings Page inputs.
    """

    ADMINISTRATOR_NAME = formencode.All(validators.UnicodeString(not_empty=True), validators.PlainText())
    ADMINISTRATOR_PASSWORD = validators.UnicodeString(not_empty=True)
    ADMINISTRATOR_EMAIL = validators.Email(not_empty=True)

    WEB_SERVER_PORT = PortValidator()
    MPLH5_SERVER_PORT = PortValidator()
    URL_WEB = validators.URL(not_empty=True, require_tld=False)
    URL_MPLH5 = AsciiValidator(not_empty=True)

    SELECTED_DB = validators.UnicodeString(not_empty=True)
    URL_VALUE = validators.UnicodeString(not_empty=True)
    DEPLOY_CLUSTER = validators.Bool()

    TVB_STORAGE = AsciiValidator(not_empty=True)
    USR_DISK_SPACE = DiskSpaceValidator(not_empty=True)
    MATLAB_EXECUTABLE = MatlabValidator()
    MAXIMUM_NR_OF_THREADS = ThreadNrValidator()
    MAXIMUM_NR_OF_VERTICES_ON_SURFACE = SurfaceVerticesNrValidator()
    MAXIMUM_NR_OF_OPS_IN_RANGE = validators.Int(min=5, max=5000, not_empty=True)



