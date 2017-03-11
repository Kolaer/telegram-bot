# Парсрер выражений вида: 1, 1+2, 1 + 2, 13e3, -23.5, 10+2j, sin(2)**2 + cos(3)^3, x = 3, def f(x,y,z) = x+y*z,f(x,2,1)

import token
from io import StringIO
from tokenize import generate_tokens

from funcparserlib.lexer import *
from funcparserlib.parser import *
from funcparserlib.parser import with_forward_decls


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


def tokenize(s):
    """str -> [Token]"""
    return list(Token(t.type, t.string) for t in generate_tokens(StringIO(s).readline))


def parse(tokens):
    """Sequence(Token) -> AST (abstract syntax tree)"""

    def make_number(s):
        """Возвращает число из строки"""
        return complex(s)

    # Token -> Token.value
    tokval = lambda tok: tok.value

    # Парсинг чисел
    number = (
        some(lambda tok: tok.code == token.NUMBER)
        >> tokval
        >> make_number)

    # Парсинг конкретной операции (+, -, *, /, ",", ...)
    op = lambda s: a(Token(token.OP, s)) >> tokval
    # То же самое, но не записывая
    op_ = lambda s: skip(op(s))

    # Парсинг названий переменных, функций, ключевых слов
    name = (
        some(lambda tok: tok.code == token.NAME)
        >> tokval)

    # Парсинг ключевых слов (скипая), по сути просто заданное имя
    keyword = lambda s: skip(a(Token(token.NAME, s)))

    add = op('+')
    sub = op('-')
    mul = op('*')
    div = op('/')

    pow1 = op('**')
    pow2 = op('^')
    power = pow1 | pow2

    mul_op = mul | div
    add_op = add | sub

    # Приведение к единому формату вызова функций
    def make_apply(f, f_args):
        if f_args is None or f_args == []:
            return ["apply", f, []]

        tmp = []

        for arg in f_args:
            tmp.append(arg)

        return ["apply", f, tmp]

    # Приведение к единому формату вычисления выражений
    def make_expr(s):
        (x, rest) = s

        if rest is None or rest == []:
            return x

        (operator, y) = rest[0]

        nxt = (y, rest[1:])
        f_args = [x, make_expr(nxt)]

        return make_apply(operator, f_args)

    # Приведение к единому формату вызова функций
    def make_function_call(s):
        if s[1] is None or s[1] == []:
            return make_apply(s[0], [])

        (x, rest) = s[1]

        f_args = [x]

        for arg in rest:
            f_args.append(arg)

        return make_apply(s[0], f_args)

    # Парсинг выражений по грамматикам
    @with_forward_decls
    def primary():
        expr_args = expr + many(op_(',') + expr)
        function_call = name + op_('(') + maybe(expr_args) + op_(')') >> make_function_call
        return function_call | name | number | (op_('(') + expr + op_(')'))

    # Парсинг выражений по грамматикам
    factor = primary + many(power + primary) >> make_expr
    term = factor + many(mul_op + factor) >> make_expr
    expr = term + many(add_op + term) >> make_expr

    def make_set(s):
        return ["set", s[0], s[1]]

    # Парсинг присвоений
    set_var = name + op_('=') + expr >> make_set

    def make_unset(s):
        return ["unset", s[0]]

    # Парсинг удаления переменных
    unset_var = keyword('unset') + name >> make_unset

    # Парсинг аргументов
    args = name + many(op_(',') + name)

    # Приведение определений функций к единому виду
    def make_def(s):
        if s[1] is None or s[1] == []:
            return ["def", s[0], [], s[2]]

        (x, rest) = s[1]
        f_args = [x]

        for arg in rest:
            f_args.append(arg)

        return ["def", s[0], f_args, s[2]]

    # Парсинг определения функций
    def_fn = keyword('def') + name + op_('(') + maybe(args) + op_(')') + op_('=') + expr >> make_def

    def make_undef(s):
        return ["undef", s[0]]

    # Парсинг удаления функций
    undef_fn = keyword('undef') + name >> make_undef

    # Парсеры конца ввода
    endmark = a(Token(token.ENDMARKER, ''))
    end = skip(endmark + finished)

    # Основной парсер
    toplevel = maybe(set_var | unset_var | def_fn | undef_fn | expr) + end

    return toplevel.parse(tokens)


# Примеры
print(parse(tokenize('1')))
print(parse(tokenize('1j')))
print(parse(tokenize('2 - 1j')))
print(parse(tokenize('sin(2)')))
print(parse(tokenize('(1 + 2) * 3')))
print(parse(tokenize('x = y')))
print(parse(tokenize('z = x + y^3')))
print(parse(tokenize('unset x')))
print(parse(tokenize('def f(x, y) = (2 + x) * y')))
print(parse(tokenize('undef f')))
