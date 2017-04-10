import math
import os
import sys

import pint
import pytest

import src.calc

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')


class TestUM:
    def test_const(self):
        assert src.calc.calculate('e', src.calc.Environment()) == math.e

    def test_func(self):
        assert src.calc.calculate('cos(0)', src.calc.Environment()) == 1.0

    def test_matrix(self):
        assert src.calc.calculate('tr(T([2 1]) * [1 2])', src.calc.Environment()) == 4

    def test_def_func(self):
        env = src.calc.Environment()
        src.calc.calculate('def f(x,y) = x + y', env)
        assert env.get_function('f') == (False, (2, (['x', 'y'], ['apply', '+', ['x', 'y']])))

    def test_undef_func(self):
        env = src.calc.Environment()
        with pytest.raises(RuntimeError):
            env.get_function('f')

    def test_del_var(self):
        env = src.calc.Environment()
        with pytest.raises(AssertionError):
            assert env.del_var('x')

    def test_set_func_error(self):
        env = src.calc.Environment()
        with pytest.raises(RuntimeError):
            env.set_function('sqrt', 2, (['x', 'y'], ['apply', '+', ['x', 'y']]))

    def test_del_func2(self):
        env = src.calc.Environment()
        with pytest.raises(AssertionError):
            assert env.del_function('f')

    def test_del_rec_var(self):
        env = src.calc.Environment()
        env1 = src.calc.Environment(root=env)
        env.set_var('x', 1)
        env1.set_var('x', 2)
        assert env1.get_var('x') == 2
        env1.del_var('x')
        assert env1.get_var('x') == 1
        env1.del_var('x')
        with pytest.raises(RuntimeError):
            assert env1.get_var('x')

    def test_del_rec_func(self):
        env = src.calc.Environment()
        env1 = src.calc.Environment(root=env)
        env.set_function('f', 2, (['x', 'y'], ['apply', '+', ['x', 'y']]))
        env1.set_function('f', 2, (['x', 'y'], ['apply', '-', ['x', 'y']]))
        assert env1.get_function('f') == (False, (2, (['x', 'y'], ['apply', '-', ['x', 'y']])))
        env1.del_function('f')
        assert env1.get_function('f') == (False, (2, (['x', 'y'], ['apply', '+', ['x', 'y']])))
        env1.del_function('f')
        with pytest.raises(RuntimeError):
            assert env1.get_function('f')

    def test_set_data(self):
        env = src.calc.Environment()
        env.set_data([['x'], ['y']])
        assert env.get_data() == [['x'], ['y']]

    def test_unset_var(self):
        env = src.calc.Environment()
        src.calc.calculate('x = 1', env)
        src.calc.calculate('unset x', env)
        with pytest.raises(RuntimeError):
            assert env.get_var('x')

    def test_def_uniq(self):
        env = src.calc.Environment()
        with pytest.raises(RuntimeError):
            assert src.calc.calculate('def f(x,x) = x + y', env)

    def test_undef(self):
        env = src.calc.Environment()
        src.calc.calculate('def f(x,y) = x + y', env)
        src.calc.calculate('undef f', env)
        with pytest.raises(RuntimeError):
            assert env.get_function('f')

    def test_arity_error(self):
        env = src.calc.Environment()
        src.calc.calculate('def f(x) = x + y', env)
        with pytest.raises(RuntimeError):
            src.calc.calculate('f(2,3)', env)

    def test_arity_error2(self):
        env = src.calc.Environment()
        with pytest.raises(RuntimeError):
            src.calc.calculate('cos(c,2)', env)

    def test_function_env_set_var(self):
        env = src.calc.Environment()
        src.calc.calculate('def f(x,y) = x + y', env)
        assert src.calc.calculate('f(2,3)', env) == 5

    def test_convert(self):
        env = src.calc.Environment()
        ureg = pint.UnitRegistry()
        assert src.calc.calculate('3.6{kg} -> {mg}', env) == 3600000.0 * ureg('mg')

    def test_make_units(self):
        env = src.calc.Environment()
        ureg = pint.UnitRegistry()
        assert src.calc.calculate('3.6 {(kg * m) / s}->{(mg * m)/s}', env) == 3600000.0 * ureg('(mg * m)/s')
