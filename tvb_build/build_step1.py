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
The distribution process is split in three.

The zero'th phase is to build an anaconda environment with all tvb's dependencies.
This preliminary phase is not used by the mac build as it is not anaconda based.

This script is the first phase.
It should be run when bundled data, documentation or tvb_bin/ scripts change.
This should happen rarely.

The second phase includes the source code and depends on the zip produced by this file.

.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""
import os
import shutil
from os.path import join
from tvb_build.tvb_documentor.doc_generator import DocGenerator
import tvb_bin
import tvb_data

# source paths
BIN_FOLDER = os.path.dirname(tvb_bin.__file__)
TVB_ROOT = os.path.dirname(os.path.dirname(BIN_FOLDER))
FW_FOLDER = join(TVB_ROOT, 'framework_tvb')
LICENSE_PATH = join(FW_FOLDER, 'LICENSE_TVB.txt')
RELEASE_NOTES_PATH = join(TVB_ROOT, 'tvb_documentation', 'RELEASE_NOTES')
DATA_SRC_FOLDER = os.path.dirname(tvb_data.__file__)
DEMOS_MATLAB_FOLDER = join(TVB_ROOT, 'matlab')

# dest paths
DIST_FOLDER = join(os.path.dirname(__file__), 'build', 'TVB_Distribution')

DATA_INSIDE_FOLDER = join(DIST_FOLDER, '_tvb_data')

INCLUDED_INSIDE_DATA = [
    "__init__.py",
    "Default_Project.zip",

    "connectivity/connectivity_76.zip",
    "connectivity/paupau.zip",
    "connectivity/connectivity_66.zip",
    "connectivity/connectivity_192.zip",
    "connectivity/__init__.py",

    "projectionMatrix/projection_eeg_62_surface_16k.mat",
    "projectionMatrix/projection_eeg_65_surface_16k.npy",
    "projectionMatrix/projection_meg_276_surface_16k.npy",
    "projectionMatrix/projection_seeg_588_surface_16k.npy",
    "projectionMatrix/__init__.py",

    "regionMapping/__init__.py",
    "regionMapping/regionMapping_16k_76.txt",
    "regionMapping/regionMapping_80k_80.txt",

    "sensors/eeg_unitvector_62.txt.bz2",
    "sensors/eeg_brainstorm_65.txt",
    "sensors/meg_151.txt.bz2",
    "sensors/meg_brainstorm_276.txt",
    "sensors/seeg_39.txt.bz2",
    "sensors/seeg_brainstorm_960.txt",
    "sensors/seeg_588.txt",
    "sensors/__init__.py",

    "surfaceData/__init__.py",
    "surfaceData/cortex_80k.zip",
    "surfaceData/cortex_16384.zip",
    "surfaceData/outer_skin_4096.zip",
    "surfaceData/inner_skull_4096.zip",
    "surfaceData/outer_skull_4096.zip",
    "surfaceData/scalp_1082.zip",
    "surfaceData/face_8614.zip",

    "local_connectivity/__init__.py",
    "local_connectivity/local_connectivity_16384.mat",
    "local_connectivity/local_connectivity_80k.mat",

    "obj/__init__.py",
    "obj/face_surface.obj",
    "obj/eeg_cap.obj",

    "mouse/allen_2mm/Connectivity.h5",
    "mouse/allen_2mm/Volume.h5",
    "mouse/allen_2mm/StructuralMRI.h5",
    "mouse/allen_2mm/RegionVolumeMapping.h5",
]


def _copy_dataset(dataset_files, dataset_destination):
    for pth in dataset_files:
        rel_pth = pth.split('/')
        origin = join(DATA_SRC_FOLDER, *rel_pth)
        destination = join(dataset_destination, *rel_pth)
        destination_folder = os.path.dirname(destination)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.copyfile(origin, destination)


def copy_distribution_dataset():
    """
    Copy the required data file from tvb_data folder:
    - inside TVB library package (for internal usage).
        Will be used during TVB functioning: import default project,
        load default for console profile, or code update events
    - in tvb_data folder, as example for users.
    """
    _copy_dataset(INCLUDED_INSIDE_DATA, DATA_INSIDE_FOLDER)


def build_step1():
    build_folder = os.path.dirname(DIST_FOLDER)

    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
    os.makedirs(DIST_FOLDER)

    # make top level dirs
    top_level_folders = ['docs']
    for d in top_level_folders:
        os.mkdir(join(DIST_FOLDER, d))

    # make help
    doc_generator = DocGenerator(TVB_ROOT, DIST_FOLDER)
    doc_generator.generate_pdfs()
    doc_generator.generate_online_help()

    shutil.copy2(LICENSE_PATH, join(DIST_FOLDER, 'LICENSE_TVB.txt'))
    shutil.copy2(RELEASE_NOTES_PATH, join(DIST_FOLDER, 'docs', 'RELEASE_NOTES.txt'))
    shutil.copytree(DEMOS_MATLAB_FOLDER, join(DIST_FOLDER, 'matlab'))

    copy_distribution_dataset()

    shutil.rmtree(join(DIST_FOLDER, DocGenerator.API))
    shutil.make_archive('TVB_build_step1', 'zip', build_folder)
    shutil.rmtree(DIST_FOLDER)
    shutil.move('TVB_build_step1.zip', build_folder)


if __name__ == '__main__':
    build_step1()

