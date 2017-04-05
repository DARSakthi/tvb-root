# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
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

from numba import cuda, int32, float32

def make_euler(dt, f, n_svar, n_step):
    "Construct CUDA device function for Euler scheme."

    n_step = int32(n_step)
    dt = float32(dt)

    @cuda.jit(device=True)
    def scheme(X, I):
        dX = cuda.local.array((n_svar,), float32)
        for i in range(n_step):
            f(dX, X, I)
            for j in range(n_svar):
                X[j] += dX[j]

    return scheme


def make_rk4(dt, f, n_svar, n_step):
    "Construct CUDA device function for Runge-Kutta 4th order scheme."

    n_step = int32(n_step)
    dt = float32(dt)

    @cuda.jit(device=True)
    def scheme(X, I):
        k = cuda.shared.array((4, n_svar, 64), float32)
        x = cuda.shared.array((n_svar, 64), float32)
        t = cuda.threadIdx.x
        for i in range(n_step):
            f(k[0], X, I)
            for j in range(n_svar):
                x[j, t] = X[j, t] + (dt / float32(2.0)) * k[0, j, t]
            f(k[1], x, I)
            for j in range(n_svar):
                x[j, t] = X[j, t] + (dt / float32(2.0)) * k[1, j, t]
            f(k[2], x, I)
            for j in range(n_svar):
                x[j, t] = X[j, t] + dt * k[2, j, t]
            f(k[3], x, I)
            for j in range(n_svar):
                X[j, t] += (dt/float32(6.0)) * (k[0, j, t] + k[3, j, t] + float32(2.0)*(k[1, j, t] + k[2, j, t]))

    return scheme