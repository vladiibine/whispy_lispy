# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from whispy_lispy import scopes2


class ScopeTestCase(unittest.TestCase):
    def test_normal_scopes_see_values_from_parents(self):
        s1 = scopes2.Scope()
        s1['a'] = 'a'
        s2 = scopes2.Scope(parent=s1)
        self.assertEqual(s2['a'], 'a')
        self.assertTrue('a' in s2)

    def test_parameters_of_ancestor_are_visible(self):
        fs1 = scopes2.FunctionScope(param_names=('a',), arguments=(1,))
        s2 = scopes2.Scope(parent=fs1)

        self.assertTrue('a' in s2)
        self.assertEqual(s2['a'], 1)

    def test_closure_is_visible(self):
        fs1 = scopes2.FunctionScope(closure_scope={'a': 'a'})
        fs2 = scopes2.FunctionScope(parent=fs1)

        self.assertTrue('a' in fs2)
        self.assertEqual(fs2['a'], 'a')

    def test_mix_normal_and_function_scopes(self):
        s1 = scopes2.Scope()
        s1[1] = 1

        s2 = scopes2.Scope(parent=s1)
        s2[2] = 2

        fs3 = scopes2.FunctionScope(parent=s2)

        self.assertTrue(2 in fs3)
        self.assertTrue(1 in fs3)

