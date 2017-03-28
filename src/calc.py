import math
import operator
from numbers import Number

import numpy as np

from src import parser


class Environment(object):
    """Класс окружений, сохраняет функции и переменные, множество окружений имеет древовидную иерархию"""
    def __make(self):
        """Встроенные переменные и функции"""
        self.variables = {'e': math.e, 'pi': math.pi}
        self.functions = {'+': (2, operator.add),
                          '-': (2, operator.sub),
                          'neg': (1, lambda x: -x),
                          '*': (2, operator.mul),
                          '/': (2, operator.truediv),
                          'pow': (2, np.power),
                          'sin': (1, np.sin),
                          'cos': (1, np.cos),
                          'tan': (1, np.tan),
                          'ctg': (1, lambda x: 1 / np.tan(x)),
                          'ln': (1, np.log),
                          'lg': (1, np.log10),
                          'log2': (1, np.log2),
                          'fact': (1, lambda x: math.gamma(x + 1)),
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


def calculate(s, env):
    """String, Environment -> Complex
        Выполнение вычисления в контексте окружения"""

    def make_matrix(x):
        """Построение массива для создания матрицы"""
        if isinstance(x, Number):
            return x
        if x[0] == "matrix":
            return [make_matrix(y) for y in x[1]]

    def evl(expr, env):
        """Вычислене выражения в окружении"""
        if isinstance(expr, Number):
            return expr

        if isinstance(expr, str):
            if expr != "set" and expr != "apply" and expr != "unset" and expr != "def" and expr != "undef" \
                    and expr != "matrix" and expr != "with_units":
                return env.get_var(expr)

        (expr_type, *expr_body) = expr

        if expr_type == "matrix":
            return np.matrix(make_matrix(expr))

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


# Примеры
if __name__ == "__main__":
    env = Environment()
    print(calculate('x = 3', env))
    print(calculate('fact(x ^ 2)', env))
    print(calculate('def f(x, y) = x + y', env))
    print(calculate('f(2, 3)', env))
    print(calculate('unset x', env))
    print(calculate('undef f', env))
    print(calculate('cos(0)', env))
    print(calculate('-2 + 2', env))
    print(calculate('tr(T([2 1]) * [1 2])', env))
    print()
    print(env)