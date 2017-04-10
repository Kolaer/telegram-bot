import os
import sys

import src.parser

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')


class TestUM:
    def test_num(self):
        assert src.parser.parse('1.1') == 1.1

    def test_neg(self):
        assert src.parser.parse('-2') == -2

    def test_complex_num_sub(self):
        assert src.parser.parse('2 - 1j') == ['apply', '-', [2.0, 1j]]

    def test_func_calc_args(self):
        assert src.parser.parse('sin(2)') == ['apply', 'sin', [2.0]]

    def test_assign_add_pow(self):
        assert src.parser.parse('z = x + y^3') == ['set', 'z', ['apply', '+', ['x', ['apply', 'pow', ['y', 3.0]]]]]

    def test_unset(self):
        assert src.parser.parse('unset x') == ['unset', 'x']

    def test_mul_var_args_def_func(self):
        assert src.parser.parse('def f(x, y) = (2 + x) * y') == ['def', 'f', ['x', 'y'],
                                                                 ['apply', '*', [['apply', '+', [2.0, 'x']], 'y']]]

    def test_undef(self):
        assert src.parser.parse('undef f') == ['undef', 'f']

    def test_matrix(self):
        assert src.parser.parse('[[1 2] [3 4]]') == ['matrix', [['matrix', [1.0, 2.0]], ['matrix', [3.0, 4.0]]]]

    def test_div(self):
        assert src.parser.parse('(1 + 2) / 3') == ['apply', '/', [['apply', '+', [1.0, 2.0]], 3.0]]

    def test_atom_units(self):
        assert src.parser.parse('x {(kg * m) / s}') == ['with_units', 'x', ['unit_div', ['unit_mul', 'kg', 'm'], 's']]

    def test_convert(self):
        assert src.parser.parse('x {kg} -> {mg}') == ['convert', ['with_units', 'x', 'kg'], 'mg']

    def test_number_base(self):
        assert src.parser.parse('<ff>16 + <101>2') == ['apply', '+', [255, 5]]
