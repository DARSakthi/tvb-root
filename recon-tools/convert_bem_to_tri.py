import os
import sys
import glob
import utils

SUBJECTS_DIR = os.environ['SUBJECTS_DIR']
SUBJECT = os.environ['SUBJECT']

surfs_glob = '%s/%s/bem/watershed/*_surface-low' % (SUBJECTS_DIR, SUBJECT)
for surf_name in glob.glob(surfs_glob):
    utils.convert_fs_to_brain_visa(surf_name)
