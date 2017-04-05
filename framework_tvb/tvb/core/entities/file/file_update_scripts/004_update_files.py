# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
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
# CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
# Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Upgrade script from H5 version 3 to version 4 (for tvb release 1.4.1)

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import os
import json
from tvb.basic.profile import TvbProfile
from tvb.basic.logger.builder import get_logger
from tvb.core.entities.storage import dao
from tvb.core.entities.file.exceptions import IncompatibleFileManagerException
from tvb.core.entities.file.hdf5_storage_manager import HDF5StorageManager
from tvb.core.entities.transient.structure_entities import DataTypeMetaData
from tvb.core.services.import_service import ImportService
from tvb.datatypes import projections

LOGGER = get_logger(__name__)
FIELD_PROJECTION_TYPE = "Projection_type"
FIELD_SURFACE_MAPPING = "Has_surface_mapping"
FIELD_VOLUME_MAPPING = "Has_volume_mapping"


def update(input_file):
    """
    :param input_file: the file that needs to be converted to a newer file storage version.
    """

    if not os.path.isfile(input_file):
        raise IncompatibleFileManagerException("The input path %s received for upgrading from 3 -> 4 is not a "
                                               "valid file on the disk." % input_file)

    folder, file_name = os.path.split(input_file)
    storage_manager = HDF5StorageManager(folder, file_name)

    root_metadata = storage_manager.get_metadata()
    if DataTypeMetaData.KEY_CLASS_NAME not in root_metadata:
        raise IncompatibleFileManagerException("File %s received for upgrading 3 -> 4 is not valid, due to missing "
                                               "metadata: %s" % (input_file, DataTypeMetaData.KEY_CLASS_NAME))
    class_name = root_metadata[DataTypeMetaData.KEY_CLASS_NAME]

    if "ProjectionSurface" in class_name and FIELD_PROJECTION_TYPE not in root_metadata:
        LOGGER.info("Updating ProjectionSurface %s from %s" % (file_name, folder))

        projection_type = projections.EEG_POLYMORPHIC_IDENTITY
        if "SEEG" in class_name:
            projection_type = projections.SEEG_POLYMORPHIC_IDENTITY
        elif "MEG" in class_name:
            projection_type = projections.MEG_POLYMORPHIC_IDENTITY

        root_metadata[FIELD_PROJECTION_TYPE] = json.dumps(projection_type)
        LOGGER.debug("Setting %s = %s" % (FIELD_PROJECTION_TYPE, projection_type))

    elif "TimeSeries" in class_name:
        LOGGER.info("Updating TS %s from %s" % (file_name, folder))

        service = ImportService()
        operation_id = int(os.path.split(folder)[1])
        dt = service.load_datatype_from_file(folder, file_name, operation_id, move=False)
        dt_db = dao.get_datatype_by_gid(dt.gid)

        if dt_db is not None:
            # DT already in DB (update of own storage, by making sure all fields are being correctly populated)
            dt_db.configure()
            dt_db.persist_full_metadata()
            try:
                # restore in DB, in case TVB 1.4 had wrongly imported flags
                dao.store_entity(dt_db)
            except Exception:
                LOGGER.exception("Could not update flags in DB, but we continue with the update!")

        elif FIELD_SURFACE_MAPPING not in root_metadata:
            # Have default values, to avoid the full project not being imported
            root_metadata[FIELD_SURFACE_MAPPING] = json.dumps(False)
            root_metadata[FIELD_VOLUME_MAPPING] = json.dumps(False)

    root_metadata[TvbProfile.current.version.DATA_VERSION_ATTRIBUTE] = TvbProfile.current.version.DATA_VERSION
    storage_manager.set_metadata(root_metadata)