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
# CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
# Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
# Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
# The Virtual Brain: a simulator of primate brain network dynamics.
# Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

from tvb.core.entities.model import AlgorithmTransientGroup
from tvb.adapters.analyzers.bct_adapters import BaseBCT, BaseUndirected, bct_description, \
    LABEL_CONN_WEIGHTED_UNDIRECTED, LABEL_CONN_WEIGHTED_DIRECTED


BCT_GROUP_CLUSTERING = AlgorithmTransientGroup("Clustering Algorithms", "Brain Connectivity Toolbox")


class ClusteringCoefficient(BaseBCT):
    """
    """
    _ui_group = BCT_GROUP_CLUSTERING
    _ui_connectivity_label = "Binary directed connection matrix:"

    _ui_name = "Clustering Coefficient BD"
    _ui_description = bct_description("clustering_coef_bd.m")
    _matlab_code = "C = clustering_coef_bd(A);"


    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.weights
        result = self.execute_matlab(self._matlab_code, **kwargs)
        measure = self.build_connectivity_measure(result, 'C', connectivity, "Clustering Coefficient BD")
        return [measure]


class ClusteringCoefficientBU(BaseUndirected):
    """
    """
    _ui_group = BCT_GROUP_CLUSTERING

    _ui_name = "Clustering Coefficient BU"
    _ui_description = bct_description("clustering_coef_bu.m")
    _matlab_code = "C = clustering_coef_bu(A);"

    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.weights
        result = self.execute_matlab(self._matlab_code, **kwargs)
        measure = self.build_connectivity_measure(result, 'C', connectivity, "Clustering Coefficient BU")
        return [measure]


class ClusteringCoefficientWU(BaseUndirected):
    """
    """
    _ui_group = BCT_GROUP_CLUSTERING
    _ui_connectivity_label = LABEL_CONN_WEIGHTED_UNDIRECTED

    _ui_name = "Clustering Coeficient WU"
    _ui_description = bct_description("clustering_coef_wu.m")
    _matlab_code = "C = clustering_coef_wu(A);"

    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.scaled_weights()
        result = self.execute_matlab(self._matlab_code, **kwargs)
        measure = self.build_connectivity_measure(result, 'C', connectivity, "Clustering Coefficient WU")
        return [measure]


class ClusteringCoefficientWD(ClusteringCoefficient):
    """
    """
    _ui_connectivity_label = LABEL_CONN_WEIGHTED_DIRECTED

    _ui_name = "Clustering Coeficient WD"
    _ui_description = bct_description("clustering_coef_wd.m")
    _matlab_code = "C = clustering_coef_wd(A);"

    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.scaled_weights()
        result = self.execute_matlab(self._matlab_code, **kwargs)
        measure = self.build_connectivity_measure(result, 'C', connectivity, "Clustering Coefficient WD")
        return [measure]


class TransitivityBinaryDirected(BaseBCT):
    """
    """
    _ui_group = BCT_GROUP_CLUSTERING
    _ui_connectivity_label = "Binary directed connection matrix:"

    _ui_name = "Transitivity Binary Directed"
    _ui_description = bct_description("transitivity_bd.m")
    _matlab_code = "T = transitivity_bd(A);"

    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.weights
        result = self.execute_matlab(self._matlab_code, **kwargs)
        value = self.build_float_value_wrapper(result, 'T', "Transitivity Binary Directed")
        return [value]


class TransitivityWeightedDirected(TransitivityBinaryDirected):
    """
    """
    _ui_connectivity_label = LABEL_CONN_WEIGHTED_DIRECTED

    _ui_name = "Transitivity Weighted Directed"
    _ui_description = bct_description("transitivity_wd.m")
    _matlab_code = "T = transitivity_wd(A);"

    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.scaled_weights()
        result = self.execute_matlab(self._matlab_code, **kwargs)
        value = self.build_float_value_wrapper(result, 'T', "Transitivity Weighted Directed")
        return [value]


class TransitivityBinaryUnDirected(BaseUndirected):
    """
    """
    _ui_group = BCT_GROUP_CLUSTERING

    _ui_name = "Transitivity Binary Undirected"
    _ui_description = bct_description("transitivity_bu.m")
    _matlab_code = "T = transitivity_bu(A);"

    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.weights
        result = self.execute_matlab(self._matlab_code, **kwargs)
        value = self.build_float_value_wrapper(result, 'T', "Transitivity Binary Undirected")
        return [value]


class TransitivityWeightedUnDirected(TransitivityBinaryUnDirected):
    """
    """
    _ui_connectivity_label = LABEL_CONN_WEIGHTED_UNDIRECTED

    _ui_name = "Transitivity Weighted undirected"
    _ui_description = bct_description("transitivity_wu.m")
    _matlab_code = "T = transitivity_wu(A);"

    def launch(self, connectivity, **kwargs):
        kwargs['A'] = connectivity.scaled_weights()
        result = self.execute_matlab(self._matlab_code, **kwargs)
        value = self.build_float_value_wrapper(result, 'T', "Transitivity Weighted Undirected")
        return [value]
