#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import logging
import unittest
import tempfile
from pkg_resources import resource_filename as rs

import netCDF4 as nc4

from cc_plugin_ugrid.checker_10 import UgridChecker10
from cc_plugin_ugrid import logger
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestUgridChecker10(unittest.TestCase):

    def setUp(self):
        self.check = UgridChecker10()

    def nc(self, ncpath):
        _, tf = tempfile.mkstemp(suffix='.nc')
        shutil.copy(ncpath, tf)
        ncd = nc4.Dataset(tf, 'r+')
        self.addCleanup(ncd.close)
        self.addCleanup(lambda: os.remove(tf))
        return ncd

    def test_check_mesh_topology_variable(self):
        ncd = self.nc(rs('cc_plugin_ugrid', os.path.join('resources', 'adcirc.nc4')))

        r = self.check.check_mesh_topology_variable(ncd)
        assert r.value == (1, 1)

        mt = ncd.get_variables_by_attributes(cf_role='mesh_topology')[0]

        mt.cf_role = 'must fail'
        r = self.check.check_mesh_topology_variable(ncd)
        assert r.value == (0, 1)

        mt.cf_role = 'grid_toplogy'
        r = self.check.check_mesh_topology_variable(ncd)
        assert r.value == (0, 1)

        del mt.cf_role
        r = self.check.check_mesh_topology_variable(ncd)
        assert r.value == (0, 1)

    def test_check_topology_dimension(self):
        ncd = self.nc(rs('cc_plugin_ugrid', os.path.join('resources', 'adcirc.nc4')))

        r = self.check.check_topology_dimension(ncd)
        assert r.value == (1, 1)

        mt = ncd.get_variables_by_attributes(cf_role='mesh_topology')[0]

        mt.topology_dimension = 0
        r = self.check.check_topology_dimension(ncd)
        assert r.value == (0, 1)

        mt.topology_dimension = 9
        r = self.check.check_topology_dimension(ncd)
        assert r.value == (0, 1)

    def test_check_node_coordinates_size(self):
        ncd = self.nc(rs('cc_plugin_ugrid', os.path.join('resources', 'adcirc.nc4')))

        r = self.check.check_node_coordinates_size(ncd)
        assert r.value == (1, 1)

        mt = ncd.get_variables_by_attributes(cf_role='mesh_topology')[0]

        mt.topology_dimension = 3
        r = self.check.check_node_coordinates_size(ncd)
        assert r.value == (0, 1)

        mt.topology_dimension = 2
        mt.node_coordinates = 'first second third'
        r = self.check.check_node_coordinates_size(ncd)
        assert r.value == (0, 1)

    def test_check_node_coordinates_exist(self):
        ncd = self.nc(rs('cc_plugin_ugrid', os.path.join('resources', 'adcirc.nc4')))

        r = self.check.check_node_coordinates_exist(ncd)
        assert r.value == (1, 1)

        mt = ncd.get_variables_by_attributes(cf_role='mesh_topology')[0]

        mt.node_coordinates = 'foo bar'
        r = self.check.check_node_coordinates_exist(ncd)
        assert r.value == (0, 1)

    def test_check_connectivity(self):
        ncd = self.nc(rs('cc_plugin_ugrid', os.path.join('resources', 'adcirc.nc4')))

        r = self.check.check_connectivity(ncd)
        assert r.value == (1, 1)

        mt = ncd.get_variables_by_attributes(cf_role='mesh_topology')[0]

        mt.face_node_connectivity = 'FAIL'
        r = self.check.check_connectivity(ncd)
        assert r.value == (0, 1)

        del mt.face_node_connectivity
        r = self.check.check_connectivity(ncd)
        assert r.value == (0, 1)
