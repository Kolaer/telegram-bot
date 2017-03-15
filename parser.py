# Парсрер выражений вида: 1, 1+2, 1 + 2, 13e3, -23.5, 10+2j, sin(2)**2 + cos(3)^3, x = 3, def f(x,y,z) = x+y*z,f(x,2,1)

import token

from lark import Lark

# Класс-обёртка для токенов
class Token(object):
    def __init__(self, code, value):
        self.code = code
        self.value = value

    @property
    def type(self):
        return token.tok_name[self.code]

    def __repr__(self):
        return 'Token({}, \'{}\')'.format(self.type, self.value)

    def __eq__(self, other):
        return (self.code, self.value) == (other.code, other.value)


def parse(s):
    parser = Lark(r"""
    ?toplevel : sum meta
              | NAME "=" sum -> set
              | "unset" NAME  -> unset
              | def
              | "undef" NAME  -> undef

    ?meta     : ("{" units "}")? -> meta

    ?sum      : term
              | sum "+" term -> add
              | sum "-" term -> sub

    ?term     : fact
              | term "*" fact -> mul
              | term "/" fact -> div

    ?fact     : atom
              | fact ("**" | "^") atom -> pow

    ?args_val : sum ("," sum)*

    ?number_string : "\"" (/[0-9a-zA-Z]/)+ "\""

    ?atom     : NUMBER -> number
              | number_string "_" NATURAL -> number_base
              | "-" atom -> neg
              | atom ("i" | "j") -> imaginary
              | NAME "(" args_val? ")" -> call
              | NAME -> var
              | "(" sum ")"
              | "[" sum+ "]" -> matrix

    ?units    : NAME
              | units "*" NAME -> units_mul
              | units "/" NAME -> units_div
              | "(" units ")"

    ?args     : NAME ("," NAME)*

    ?def      : "def" NAME "(" args? ")" "=" sum

    NATURAL: /[1-9]/ (/[0-9]/)*

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
    """, start='toplevel')

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
    print(parse('x {(kg*m)/s}'))
    print(parse('"1010" _ 21 {(kg*m)/s}'))
    print(parse('[[1 2 3] [1+2 3+4 5+6]] {kg}').pretty())
