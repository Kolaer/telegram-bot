import math
import operator
from numbers import Number

import numpy as np
import pint

from src import parser

ureg = pint.UnitRegistry()

class Environment(object):
    """Класс окружений, сохраняет функции и переменные, множество окружений имеет древовидную иерархию"""
    def __make(self):
        """Встроенные переменные и функции"""
        self.variables = {'e': math.e, 'pi': math.pi}
        self.functions = {'+': (2, operator.add),
                          '-': (2, operator.sub),
                          'neg': (1, operator.neg),
                          '*': (2, operator.mul),
                          '/': (2, operator.truediv),
                          'pow': (2, np.power),
                          'sin': (1, np.sin),
                          'cos': (1, np.cos),
                          'tan': (1, np.tan),
                          'ln': (1, np.log),
                          'lg': (1, np.log10),
                          'log2': (1, np.log2),
                          'sqrt': (1, np.lib.emath.sqrt),
                          'T': (1, np.transpose),
                          'tr': (1, np.trace),
                          'D': (1, np.linalg.det),
                          'rk': (1, np.linalg.matrix_rank),
                          'inv': (1, np.linalg.inv)}

        for (key, val) in self.functions.items():
            self.functions[key] = True, val

    def __init__(self, root=None):
        if root is None:
            self.root = None
            self.__make()
        else:
            self.root = root
            self.variables = dict()
            self.functions = dict()

    def set_var(self, variable, value):
        """Установка переменной"""
        self.variables[variable] = value

    def del_var(self, variable):
        """Рекурсивное удаление переменной"""
        if variable in self.variables:
            del self.variables[variable]
            return

        if self.root is None:
            return

        self.root.del_var(variable)

    def get_var(self, variable):
        """Рекурсивное получение значения переменной"""
        if variable in self.variables:
            return self.variables[variable]

        if self.root is None:
            raise RuntimeError("Variable {} not found".format(variable))

        return self.root.get_var(variable)

    def set_function(self, function, arity, body):
        """Установка функции"""
        if function in self.functions and self.functions[function][0]:
            raise RuntimeError('Trying overwrite a built-in function')

        self.functions[function] = (False, (arity, body))

    def del_function(self, function):
        """Рекурсивное удаление функции"""
        if function in self.functions:
            del self.functions[function]
            return

        if self.root is None:
            return

        self.root.del_function(function)

    def get_function(self, function):
        """Рекурсивное получение функции"""
        if function in self.functions:
            return self.functions[function]

        if self.root is None:
            raise RuntimeError("Function {} not found".format(function))

        return self.root.get_function(function)

    def __repr__(self):
        res = ""

        for (key, val) in self.variables.items():
            res += "{}: {}\n".format(key, val)

        res += "~~~~\n"

        for fn in self.functions:
            res += "func. {}\n".format(fn)

        return res

    def get_data(self):
        return [self.variables, self.functions]

    def set_data(self, data):
        self.variables = data[0]
        self.functions = data[1]

def calculate(s, env):
    """String, Environment -> Complex
        Выполнение вычисления в контексте окружения"""

    def make_matrix(x):
        """Построение массива для создания матрицы"""
        if isinstance(x, Number):
            return x
        if x[0] == "matrix":
            return [make_matrix(y) for y in x[1]]

    def make_units(x):
        if isinstance(x, str):
            return x
        if x[0] == "unit_mul":
            a = make_units(x[1])
            b = make_units(x[2])
            return '({} * {})'.format(a, b)
        if x[0] == "unit_div":
            a = make_units(x[1])
            b = make_units(x[2])
            return '({} / {})'.format(a, b)

    def evl(expr, env):
        """Вычислене выражения в окружении"""
        if isinstance(expr, Number):
            return expr

        if isinstance(expr, str):
            if expr not in ["set", "apply", "unset", "def", "undef", "matrix", "with_units", "convert"]:
                return env.get_var(expr)

        (expr_type, *expr_body) = expr

        if expr_type == "matrix":
            return np.matrix(make_matrix(expr))

        if expr_type == "with_units":
            val, units = expr_body
            return evl(val, env) * ureg(make_units(units))

        if expr_type == "convert":
            val, units = expr_body
            return evl(val, env).to(ureg(make_units(units)))

        if expr_type == "set":
            (variable, value_expr) = expr_body
            env.set_var(variable, evl(value_expr, env))
            return

        if expr_type == "unset":
            env.del_var(expr_body[0])
            return

        if expr_type == "def":
            (f_name, f_args, f_body) = expr_body

            arity = len(f_args)
            if arity != len(set(f_args)):
                raise RuntimeError("All args. must be uniq.")

            env.set_function(f_name, arity, (f_args, f_body))

            return

        if expr_type == "undef":
            env.del_function(expr_body[0])
            return

        if expr_type == "apply":
            (f_name, f_args) = expr_body

            return apply(f_name, f_args, env)

    def apply(f, f_args, env):
        """Применение функции к аргументам (создаётся под-окружение для вычисления)"""
        (builtin, (arity, fn)) = env.get_function(f)

        # Встроенная функция (обычная функция из питона)
        if builtin:
            if arity == len(f_args):

                f_args = map(lambda x: evl(x, env), f_args)

                return fn(*f_args)
            else:
                raise RuntimeError("Function {} has arity {}, but called with {} args.".format(f, arity, len(f_args)))

        # Пользователькая функция

        function_env = Environment(root=env)

        (f_vars, body) = fn

        if arity != len(f_args):
            raise RuntimeError("Function {} has arity {}, but called with {} args.".format(f, arity, len(f_args)))

        # Вычисление аргументов
        for i in range(len(f_vars)):
            function_env.set_var(f_vars[i], evl(f_args[i], env))

        return evl(body, function_env)

    expr = parser.parse(s)

    return evl(expr, env)


