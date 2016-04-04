import nibabel, gdist, scipy.io, os
SUBJECTS_DIR, SUBJECT = [os.environ[key] for key in ['SUBJECTS_DIR', 'SUBJECT']]
for h in 'rl':
  surf_path = '%s/%s/surf/%sh.pial.low' % (SUBJECTS_DIR, SUBJECT, h)
  v, f = nibabel.freesurfer.read_geometry(surf_path)
  mat_path = '%s/%s/surf/%sh.pial.low.gdist.mat' % (SUBJECTS_DIR, SUBJECT, h)
  mat = gdist.local_gdist_matrix(v, f.astype('<i4'), max_distance=40.0)
  scipy.io.savemat(mat_path, {'gdist': mat})

