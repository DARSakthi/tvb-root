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
File for cutting the "potato".
"""
import numpy
from tvb.core.utils import store_list_data

FILE_VERTICES = "vertices.txt"
FILE_TRIANGLES = "triangles.txt"

def process_edge(end1, end2, margin):
    """ Check edge"""
    if (end1, end2) in margin:
        margin.remove((end1, end2))
        return
    if (end2, end1) in margin:
        margin.remove((end2, end1))
        return
    margin.append((end1, end2))
 
 
import math

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def length(v):
    return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))
  
def is_valid_triangle(a, b, c, vertices): 
    """Determine if a given triangle shoud be added"""
    v1 = vertices[b] - vertices[a]
    v2 = vertices[b] - vertices[c]
    a = angle(v1, v2)
    if a > 4* math.pi/5:
        return False
    return True
    
    

if __name__ == '__main__':
    VERTICES = numpy.loadtxt(FILE_VERTICES) 
    TRIANGLES = numpy.loadtxt(FILE_TRIANGLES) 
    
    print numpy.apply_along_axis(numpy.average, 0, VERTICES)
    print numpy.apply_along_axis(max, 0, VERTICES)
    print numpy.apply_along_axis(min, 0, VERTICES)
    CENTER_1 = numpy.array([-1.44, 1.88, -52])
    CENTER_2 = numpy.array([-1.44, 27, -52])
    CENTER_3 = numpy.array([-1.44, -34, -52])
    CENTER_4 = numpy.array([-1.44, 55, -55])
    CENTER_5 = numpy.array([-1.44, -53, -55])
    
    TO_REMOVE_IDX = numpy.array([i for i, v in enumerate(VERTICES)
                            if (numpy.sqrt(numpy.sum((v-CENTER_1)**2)) < 60) or
                               (numpy.sqrt(numpy.sum((v-CENTER_2)**2)) < 36) or
                               (numpy.sqrt(numpy.sum((v-CENTER_3)**2)) < 40) or   # Fruntea
                               (numpy.sqrt(numpy.sum((v-CENTER_4)**2)) < 14) or
                               (numpy.sqrt(numpy.sum((v-CENTER_5)**2)) < 30)])
    print len(TO_REMOVE_IDX)
        
#    TO_REMOVE_IDX = numpy.array([i for i, v in enumerate(VERTICES) 
#                                   if v[2] < -49 or    #48
#                                      (abs(v[1]) > 48 and v[2]<-45) or #44
#                                      (abs(v[1]) > 60 and v[2]<-42)])
#    it was 1019

    TRIANGLES = [t for t in TRIANGLES if (t[0] not in TO_REMOVE_IDX 
                                          and t[1] not in TO_REMOVE_IDX and
                                          t[2] not in TO_REMOVE_IDX)]
    EDGE = []
    for t in TRIANGLES:
        process_edge(t[0], t[1], EDGE)
        process_edge(t[0], t[2], EDGE)
        process_edge(t[2], t[1], EDGE)
    print len(EDGE)
    print len(TRIANGLES)  
 
    CHAIN = EDGE.pop(0)
    CHAIN = [CHAIN[0], CHAIN[1]]
    CURRENT_END = CHAIN[-1]
    while len(EDGE) > 0:
        next_edge = [e for e in EDGE 
                       if e[0] == CURRENT_END or e[1] == CURRENT_END]
        if len(next_edge) < 1:
            print "Coudn't finish chain:"+ str(CURRENT_END) + " " + str(EDGE)
            break
        if len(next_edge) > 1:
            print "Multiple edges found: "+str(CURRENT_END) +" " +str(next_edge)
        EDGE.remove(next_edge[0])
        if next_edge[0][0] == CURRENT_END:
            next_edge = next_edge[0][1]
        else :
            next_edge = next_edge[0][0]
        CHAIN.append(next_edge)
        CURRENT_END = CHAIN[-1]
    print len(CHAIN)
    #print CHAIN
    
    for i, v in enumerate(CHAIN):
        if i > 1: #and is_valid_triangle(CHAIN[i-2], CHAIN[i-1], v, VERTICES):
            TRIANGLES.append([CHAIN[i-2], CHAIN[i-1], v])
        if i > 3: #and is_valid_triangle(CHAIN[i-4], CHAIN[i-2], v, VERTICES):
            TRIANGLES.append([CHAIN[i-4], CHAIN[i-2], v])
    print len(TRIANGLES)    
    store_list_data(numpy.array(TRIANGLES), "triangles", ".")
  
  

        
          
    
    