# Парсрер выражений вида: 1, 1+2, 1 + 2, 13e3, -23.5, 10+2j, sin(2)**2 + cos(3)^3, x = 3, def f(x,y,z) = x+y*z,f(x,2,1)

from lark import Lark, Transformer


class TreeTransformer(Transformer):
    def unset(self, x):
        return ["unset", str(x[0])]

    def undef(self, func):
        return ["undef", str(func[0])]

    def num(self, x):
        return float(x[0])

    def complex_num(self, x):
        return complex(0, float(x[0]))

    def neg(self, x):
        return -x[0]

    def sub(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "-", a, b]

    def add(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "+", a, b]

    def mul(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "*", a, b]

    def div(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "/", a, b]

    def pow(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "pow", a, b]

    def var(self, x):
        return str(x[0])

    def assign(self, x):
        a = str(x[0])
        b = x[1]
        return ["set", a, b]

    def func_call(self, x):
        a = str(x[0])
        b = x[1]
        return ["apply", a, b]

    def var_args(self, x):
        return [str(a) for a in x]

    def def_func(self, x):
        a = str(x[0])
        b = x[1]
        c = x[2]
        return ["def", a, b, c]

    def atom_units(self, x):
        a = x[0]
        b = x[1]
        return ['with_units', a, b]

    def unit(self, x):
        return ["unit", str(x[0])]

    def unit_mul(self, x):
        a = x[0]
        b = x[1]
        return ["unit_mul", a, b]

    def unit_div(self, x):
        a = x[0]
        b = x[1]
        return ["unit_div", a, b]

    def matrix(self, x):
        return ['matrix', x]


def parse(s):
    parser = Lark(r"""
    ?toplevel : expr
              | assign
              | unset
              | def_func
              | undef_func -> undef

    ?assign : NAME "=" expr

    ?unset : "unset" NAME

    ?var_args : NAME ("," NAME)*

    ?def_func : "def" NAME "(" var_args? ")" "=" expr

    ?undef_func : "undef" NAME

    ?expr : term
          | expr "+" term -> add
          | expr "-" term -> sub

    ?term : exp
          | term "*" exp -> mul
          | term "/" exp -> div

    ?exp  : atom
          | exp ("**" | "^") atom -> pow

    ?args : expr ("," expr)*

    ?units : NAME -> unit
           | units "*" NAME -> unit_mul
           | units "/" NAME -> unit_div
           | "(" units ")"

    ?matrix : "[" expr+ "]"

    ?atom : NUMBER -> num
          | NUMBER ("i" | "j") -> complex_num
          | NAME -> var
          | "-" atom -> neg
          | NAME "(" args? ")" -> func_call
          | matrix
          | atom "{" units "}" -> atom_units
          | "(" expr ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
    """, start='toplevel', parser='lalr', transformer=TreeTransformer())

    return parser.parse(s)

# Примеры
if __name__ == '__main__':
    print(parse('1'))
    print(parse('1j'))
    print(parse('-2'))
    print(parse('2 - 1j'))
    print(parse('sin(2)'))
    print(parse('(1 + 2) * 3'))
    print(parse('x = y'))
    print(parse('z = x + y^3'))
    print(parse('unset x'))
    print(parse('def f(x, y) = (2 + x) * y'))
    print(parse('undef f'))
    print(parse('x {kg}'))
    print(parse('[[1 2] [3 4]]'))
