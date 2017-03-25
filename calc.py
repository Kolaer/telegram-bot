import math
import operator
from numbers import Number

import parser


class Environment(object):

    def __make(self):
        def sqrt(x):
            if isinstance(x, complex):
                return math.sqrt(x)
            if x >= 0:
                return math.sqrt(x)
            return complex(0, math.sqrt(-x))

        self.variables = {'e': math.e, 'pi': math.pi}
        self.functions = {'+': (2, operator.add),
                          '-': (2, operator.sub),
                          'neg': (1, lambda x: -x),
                          '*': (2, operator.mul),
                          '/': (2, operator.truediv),
                          'pow': (2, operator.pow),
                          'sin': (1, math.sin),
                          'cos': (1, math.cos),
                          'tan': (1, math.tan),
                          'ctg': (1, lambda x: 1 / math.tan(x)),
                          'ln': (1, math.log),
                          'lg': (1, math.log10),
                          'log2': (1, math.log2),
                          'fact': (1, lambda x: math.gamma(x + 1)),
                          'sqrt': (1, sqrt)}

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
        self.variables[variable] = value

    def del_var(self, variable):
        if variable in self.variables:
            del self.variables[variable]
            return

        if self.root is None:
            return

        self.root.del_var(variable)

    def get_var(self, variable):
        if variable in self.variables:
            return self.variables[variable]

        if self.root is None:
            raise RuntimeError("Variable {} not found".format(variable))

        return self.root.get_var(variable)

    def set_function(self, function, arity, body):
        if function in self.functions and self.functions[function][0]:
            raise RuntimeError('Trying overwrite a built-in function')

        self.functions[function] = (False, (arity, body))

    def del_function(self, function):
        if function in self.functions:
            del self.functions[function]
            return

        if self.root is None:
            return

        self.root.del_function(function)

    def get_function(self, function):
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

    def evl(expr, env):
        if isinstance(expr, Number):
            return expr

        if isinstance(expr, str):
            if expr != "set" and expr != "apply" and expr != "unset" and expr != "def" and expr != "undef" \
                    and expr != "matrix" and expr != "with_units":
                return env.get_var(expr)

        (expr_type, *expr_body) = expr

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
        (builtin, (arity, fn)) = env.get_function(f)

        if builtin:
            if arity == len(f_args):

                f_args = map(lambda x: evl(x, env), f_args)

                return fn(*f_args)
            else:
                raise RuntimeError("Function {} has arity {}, but called with {} args.".format(f, arity, len(f_args)))

        function_env = Environment(root=env)

        (f_vars, body) = fn

        if arity != len(f_args):
            raise RuntimeError("Function {} has arity {}, but called with {} args.".format(f, arity, len(f_args)))

        for i in range(len(f_vars)):
            function_env.set_var(f_vars[i], evl(f_args[i], env))

        return evl(body, function_env)

    expr = parser.parse(s)

    return evl(expr, env)

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
    print()
    print(env)
