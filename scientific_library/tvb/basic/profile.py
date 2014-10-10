# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
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
TVB Profile Manager (top level in TVB profile & settings).

This class is responsible for referring towards application settings,
based on current running environment (e.g. dev vs deployment), or developer profile choice (e.g. web vs console).

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>

"""

import sys
import copy
from tvb.basic.config.environment import Environment
from tvb.basic.config.profile_settings import BaseSettingsProfile



class TvbProfile():
    """
    ENUM-like class with current TVB profile and accepted values.
    """

    LIBRARY_PROFILE = "LIBRARY_PROFILE"
    COMMAND_PROFILE = "COMMAND_PROFILE"
    WEB_PROFILE = "WEB_PROFILE"
    DESKTOP_PROFILE = "DESKTOP_PROFILE"

    TEST_LIBRARY_PROFILE = "TEST_LIBRARY_PROFILE"
    TEST_POSTGRES_PROFILE = "TEST_POSTGRES_PROFILE"
    TEST_SQLITE_PROFILE = "TEST_SQLITE_PROFILE"

    ALL = [LIBRARY_PROFILE, COMMAND_PROFILE, WEB_PROFILE, DESKTOP_PROFILE,
           TEST_POSTGRES_PROFILE, TEST_SQLITE_PROFILE, TEST_LIBRARY_PROFILE]

    REGISTERED_PROFILES = {}

    CURRENT_PROFILE_NAME = None

    current = BaseSettingsProfile(False)
    env = Environment()

    _old_meta_path = copy.deepcopy(sys.meta_path)


    @classmethod
    def set_profile(cls, selected_profile, in_operation=False):
        """
        Sets TVB profile and do related initializations.
        """

        ### Ensure Python is using UTF-8 encoding (otherwise default encoding is ASCII)
        ### We should make sure UTF-8 gets set before reading from any TVB files
        ### e.g. TVB_STORAGE will differ if the .tvb.configuration file contains non-ascii bytes
        ### most of the comments in the simulator are having pieces outside of ascii coverage
        if cls.env.is_development() and sys.getdefaultencoding().lower() != 'utf-8':
            reload(sys)
            sys.setdefaultencoding('utf-8')

        if selected_profile is not None:
            ## Restore sys.meta_path, as some profiles (Library) are adding something
            sys.meta_path = copy.deepcopy(cls._old_meta_path)

            cls._load_framework_profiles(selected_profile)
            cls._build_profile_class(selected_profile, in_operation)


    @classmethod
    def _build_profile_class(cls, selected_profile, in_operation=False):
        """
        :param selected_profile: Profile name to be loaded.
        """

        if selected_profile in cls.REGISTERED_PROFILES:
            current_class = cls.REGISTERED_PROFILES[selected_profile]

            cls.current = current_class()

            if in_operation:
                # set flags IN_OPERATION,  before initialize** calls, to avoid LoggingBuilder being created there
                cls.current.prepare_for_operation_mode()

            if not cls.env.is_development():
                # initialize deployment first, because in case of a contributor setup this tried to reload
                # and initialize_profile loads already too many tvb modules,
                # making the reload difficult and prone to more failures
                cls.current.initialize_for_deployment()
            cls.current.initialize_profile()

        else:
            raise Exception("Invalid profile %s" % selected_profile)

        cls.CURRENT_PROFILE_NAME = selected_profile


    @classmethod
    def _load_framework_profiles(cls, new_profile):

        from tvb.basic.config.profile_settings import LibrarySettingsProfile, TestLibraryProfile
        cls.REGISTERED_PROFILES[TvbProfile.LIBRARY_PROFILE] = LibrarySettingsProfile
        cls.REGISTERED_PROFILES[TvbProfile.TEST_LIBRARY_PROFILE] = TestLibraryProfile

        if not cls.is_library_mode(new_profile):
            try:
                from tvb.config.profile_settings import CommandSettingsProfile, WebSettingsProfile
                from tvb.config.profile_settings import TestPostgresProfile, TestSQLiteProfile

                cls.REGISTERED_PROFILES[TvbProfile.COMMAND_PROFILE] = CommandSettingsProfile
                cls.REGISTERED_PROFILES[TvbProfile.WEB_PROFILE] = WebSettingsProfile
                cls.REGISTERED_PROFILES[TvbProfile.TEST_POSTGRES_PROFILE] = TestPostgresProfile
                cls.REGISTERED_PROFILES[TvbProfile.TEST_SQLITE_PROFILE] = TestSQLiteProfile

            except ImportError:
                pass


    @staticmethod
    def is_library_mode(new_profile=None):

        lib_profiles = [TvbProfile.LIBRARY_PROFILE, TvbProfile.TEST_LIBRARY_PROFILE]
        result = (new_profile in lib_profiles
                  or (new_profile is None and TvbProfile.CURRENT_PROFILE_NAME in lib_profiles)
                  or (new_profile is None and TvbProfile.CURRENT_PROFILE_NAME is None)
                  or not TvbProfile.env.is_framework_present())

        return result


    @staticmethod
    def is_first_run():

        return TvbProfile.current.manager.is_first_run()