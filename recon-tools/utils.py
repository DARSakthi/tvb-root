import os
import numpy as np
from nibabel import freesurfer

SUBJECTS_DIR, SUBJECT = [os.environ[key] for key in 'SUBJECTS_DIR SUBJECT'.split()]

def vertex_normals(v, f):
    vf = v[f]
    fn = np.cross(vf[:,1] - vf[:, 0], vf[:, 2] - vf[:, 0])
    vf = [set() for _ in xrange(len(v))]
    for i, fi in enumerate(f):
        for j in fi:
            vf[j].add(i)
    vn = np.zeros_like(v)
    for i, fi in enumerate(vf):
        fni = fn[list(fi)]
        norm = fni.sum(axis=0)
        norm /= np.sqrt((norm**2).sum())
        vn[i] = norm
    return vn

def write_brain_visa_surf(fname, v, f):
    vn = vertex_normals(v, f)
    with open(fname, 'w') as fd:
        fd.write('- %d\n' % len(vn))
        for (vx, vy, vz), (nx, ny, nz) in zip(v, vn):
            fd.write('%f %f %f %f %f %f\n' % (vx, vy, vz, nx, ny, nz))
        fd.write('- %d %d %d\n' % ((len(f),)*3))
        for i, j, k in f:
            fd.write('%d %d %d\n' % (i, j, k))

def convert_fs_to_brain_visa(fs_surf):
    v, f = freesurfer.read_geometry(fs_surf)
    write_brain_visa_surf(fs_surf + '.tri', v, f)

def read_annot(hemi, annot_name):
    annot_fname = '%s.%s.annot' % (hemi, annot_name)
    annot_path = os.path.join(SUBJECTS_DIR, SUBJECT, 'label', annot_fname)
    return freesurfer.read_annot(annot_path)

def annot_to_lut(hemi, annot_name, lut_path):
    _, ctab, names = read_annot(hemi, annot_name)
    with open(lut_path, 'w') as fd:
        for name, (r, g, b, a, id) in zip(names, ctab):
	    fd.write('%d\t%s\t%d %d %d %d\n' % (id, name, r, g, b, a))

def annot_to_conn_conf(hemi, annot_name, conn_conf_path):
    _, _, names = read_annot(hemi, annot_name)
    with open(conn_conf_path, 'w') as fd:
        for id, name in enumerate(names):
	    fd.write('%d\t%s\n' % (id, name))
