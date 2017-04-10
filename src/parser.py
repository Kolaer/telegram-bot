# Парсрер выражений вида: 1, 1+2, 1 + 2, 13e3, -23.5, 10+2j, sin(2)**2 + cos(3)^3, x = 3, def f(x,y,z) = x+y*z,f(x,2,1)

from lark import Lark, Transformer


class TreeTransformer(Transformer):
    """Класс-трансформер для преобразования AST"""

    def unset(self, x):
        return ["unset", str(x[0])]

    def undef(self, func):
        return ["undef", str(func[0])]

    def num(self, x):
        try:
            return int(x[0])
        except:
            return float(x[0])

    def complex_num(self, x):
        return complex(0, float(x[0]))

    def neg(self, x):
        return -x[0]

    def sub(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "-", [a, b]]

    def add(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "+", [a, b]]

    def mul(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "*", [a, b]]

    def div(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "/", [a, b]]

    def pow(self, x):
        a = x[0]
        b = x[1]
        return ["apply", "pow", [a, b]]

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
        return str(x[0])

    def unit_mul(self, x):
        a = x[0]
        b = x[1]
        return ["unit_mul", a, str(b)]

    def unit_div(self, x):
        a = x[0]
        b = x[1]
        return ["unit_div", a, str(b)]

    def units(self, x):
        return x[0]

    def matrix(self, x):
        return ['matrix', x]

    def args(self, x):
        return x

    def convert(self, x):
        val, to = x
        return ["convert", val, to]

    def number_base(self, x):
        digits = x[:-1]
        base = int(str(x[-1]))

        tmp = 1
        res = 0

        digits.reverse()

        for digit in digits:
            digit = str(digit)
            if ord('0') <= ord(digit) <= ord('9'):
                res += (ord(digit) - ord('0')) * tmp
            else:
                res += (ord(digit) - ord('a') + 10) * tmp
            tmp *= base

        return res


parser = Lark(r"""
    ?toplevel : expr
              | expr "->" units -> convert
              | assign
              | unset -> unset
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

    args : expr ("," expr)*

    ?matrix : "[" expr+ "]"

    ?units_inner: NAME -> unit
                | units_inner "*" NAME -> unit_mul
                | units_inner "/" NAME -> unit_div
                | "(" units_inner ")"

    ?units: "{" units_inner "}" -> units

    ?number_base : "<" (DIGIT | LETTER)+ ">" INT

    ?atom : NUMBER -> num
          | NUMBER ("i" | "j") -> complex_num
          | NAME -> var
          | "-" atom -> neg
          | NAME "(" args? ")" -> func_call
          | matrix
          | atom units -> atom_units
          | number_base
          | "(" expr ")"

    %import common.CNAME -> NAME
    %import common.LCASE_LETTER -> LETTER
    %import common.NUMBER
    %import common.INT
    %import common.DIGIT
    %import common.WS_INLINE

    %ignore WS_INLINE
    """, start='toplevel')
transformer = TreeTransformer()


def parse(s):
    """String -> Labeled-value
    Парсинг строки в удобный для вычислений вид"""
    return transformer.transform(parser.parse(s))

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
    print(parse('x {(kg * m) / s}'))
    print(parse('[[1 2] [3 4]]'))
    print(parse('<ff>16 + <101>2'))
    print(parse('x {kg} -> {mg}'))
