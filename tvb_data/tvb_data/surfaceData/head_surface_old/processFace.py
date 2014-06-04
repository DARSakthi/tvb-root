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

"""
Utility file, to adjust the skin-surface coordinates into something that is a TVB compatible surface.
We received only 3D coordinates (x, y, z), and we had to:
- compute normals
- compute some triangles for rendering (luckily, the vertices were ordered)
- remove what appears to be misplaced vertices (inside the head form)


.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import numpy
from tvb.core.utils import store_list_data

FILE_X = "headsurf.XData"
FILE_Y = "headsurf.YData"
FILE_Z = "headsurf.ZData"

if __name__ == '__main__':
    # Scale to align with our cortical-surface
    data_x = numpy.loadtxt(FILE_X) * 0.92
    data_y = numpy.loadtxt(FILE_Y) * 0.92
    data_z = numpy.loadtxt(FILE_Z) * 0.92

    vertices, normals, triangles = [], [], []
    center = numpy.array([numpy.average(data_x), numpy.average(data_y), numpy.average(data_z)])
    low_center = center + numpy.array([0, 0, -90])
    low_center1 = center + numpy.array([0, 40, -90])
    low_center2 = center + numpy.array([0, -40, -90])
    up_center = center + numpy.array([0, 15, 20])
    up_center1 = center + numpy.array([0, -15, 28])
    up_center2 = center + numpy.array([0, 25, 15])
    up_center3 = center + numpy.array([0, -25, 15])
    center1 = center + numpy.array([[-35, -29, 5]])
    center2 = center + numpy.array([[35, -20, -5]])
    #up_y = 0, radius = 37
    print center
    print numpy.array([numpy.min(data_x), numpy.min(data_y), numpy.min(data_z)])
    print numpy.array([numpy.max(data_x), numpy.max(data_y), numpy.max(data_z)])

    for i in range(data_x.shape[1]):
        for j in range(3):
            point = numpy.array([data_x[j][i], data_y[j][i], data_z[j][i]])
            direction = point - center
            direction = direction / numpy.sqrt(numpy.sum(direction ** 2))
            vertices.append(point)
            normals.append(direction)

    to_remove_idx = numpy.array([i for i, v in enumerate(vertices)
                                 if (numpy.sqrt(numpy.sum((v - low_center) ** 2)) < 37) or
                                    (numpy.sqrt(numpy.sum((v - low_center1) ** 2)) < 31) or
                                    (numpy.sqrt(numpy.sum((v - low_center2) ** 2)) < 27) or
                                    (numpy.sqrt(numpy.sum((v - up_center) ** 2)) < 62) or
                                    (numpy.sqrt(numpy.sum((v - up_center1) ** 2)) < 65) or
                                    (numpy.sqrt(numpy.sum((v - up_center2) ** 2)) < 57) or
                                    (numpy.sqrt(numpy.sum((v - up_center3) ** 2)) < 61) or
                                    (numpy.sqrt(numpy.sum((v - center1) ** 2)) < 30.5) or
                                    (numpy.sqrt(numpy.sum((v - center2) ** 2)) < 31) or
                                    (numpy.sqrt(numpy.sum((v - center) ** 2)) < 55)])
    print len(to_remove_idx)

    for i in xrange(len(vertices) / 3):
        if ((i * 3 not in to_remove_idx) and
                ((i * 3 + 1) not in to_remove_idx) and
                ((i * 3 + 2) not in to_remove_idx)):
            triangles.append([i * 3, i * 3 + 1, i * 3 + 2])

    #store_list_data(vertices, "vertices", ".")
    #store_list_data(normals, "normals", ".")
    store_list_data(triangles, "triangles", ".")

    #alpha = numpy.ones((len(vertices), 1)) * numpy.array([1.0, 0.0])
    #alpha_idx = numpy.ones((len(vertices), 1), dtype=int) * numpy.array([62, 1, 1])
    #store_list_data(alpha, "alpha", ".")
    #store_list_data(alpha_idx, "alpha_idx", ".")
    
    
    
    