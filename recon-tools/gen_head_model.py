import os
import glob

SUBJECTS_DIR = os.environ['SUBJECTS_DIR']
SUBJECT = os.environ['SUBJECT']

surfs_glob = '%s/%s/bem/watershed/*_surface-low.tri' % (SUBJECTS_DIR, SUBJECT)
surfs = glob.glob(surfs_glob)

if len(surfs) == 0:
    raise Exception('tri surfaces not found!')

hm_base = '%s/%s/bem/head_model' % (SUBJECTS_DIR, SUBJECT)
hm_temp = """# Domain Description 1.1

Interfaces 3

Interface Skull: "{0}_outer_skull_surface-low.tri"
Interface Cortex: "{0}_inner_skull_surface-low.tri"
Interface Head: "{0}_outer_skin_surface-low.tri"

Domains 4

Domain Scalp: Skull -Head
Domain Brain: -Cortex
Domain Air: Head
Domain Skull: Cortex -Skull
""".format('%s/%s/bem/watershed/%s' % (SUBJECTS_DIR, SUBJECT, SUBJECT))

hm_geom = hm_base + '.geom'
with open(hm_geom, 'w') as fd:
    fd.write(hm_temp)
print ('%s written.' % (hm_geom,))

hm_cond = hm_base + '.cond'
with open(hm_cond, 'w') as fd:
    fd.write("""# Properties Description 1.0 (Conductivities)

Air         0.0
Scalp       1
Brain       1
Skull       0.03
""")
print ('%s written.' % (hm_cond,))
