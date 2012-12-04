# -*- coding: utf-8 -*-
#
# Adapted from ML type inference algorithms. See:
#    "Types and Programming Languages", Benjamin C. Pierce (2012)

from numpy import dtype
from string import letters

#------------------------------------------------------------------------
# Syntax
#------------------------------------------------------------------------

class Atom(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Lambda(object):

    def __init__(self, v, body):
        self.v = v
        self.body = body

    def __str__(self):
        return "(\%s -> %s)" % (self.v, self.body)

class App(object):

    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def __str__(self):
        return "%s(%s)" % (self.fn, self.arg)

class TypeVar(object):

    def __init__(self):
        self.id = 0
        self.ty = None
        self.__name = None

    def _unify(self, other):
        new = TypeVar()
        new.id = self.id
        new.ty = other
        new.__name = self.__name
        return new

    @property
    def free(self):
        return self.ty is None

    @property
    def bound(self):
        return not self.free

    def __str__(self):
        if self.bound:
            return str(self.ty)
        else:
            return str(hex(id(self)))

    def pprint(self, freev):
        if self.bound:
            return self.ty.pprint(freev)
        if self.free:
            return freev.get(id(self))

class TypeCon(object):

    def __init__(self, cons, types):
        self.cons = cons
        self.types = types
        self.arity = len(self.types)

    def __str__(self):
        if self.arity == 0:
            return self.cons

        elif self.arity == 2:
            return "(%s %s %s)" % (
                str(self.types[0]),
                self.cons,
                str(self.types[1])
            )

        else:
            return "%s %s" % (self.cons, ' '.join(self.types))

    def pprint(self, freev):
        if self.arity == 0:
            return self.cons

        elif self.arity == 2:
            return "(%s %s %s)" % (
                (self.types[0]).pprint(freev),
                self.cons,
                (self.types[1]).pprint(freev)
            )

        else:
            reprs = [t.pprint(freev) for t in self.types]
            return "%s %s" % (self.cons, ' '.join(reprs))


#------------------------------------------------------------------------
# Unit Types
#------------------------------------------------------------------------

# -----------
# Γ ⊢ x : int

# ------------
# Γ ⊢ x : bool

Bool = TypeCon("bool", [])
Integer = TypeCon("int", [])

#------------------------------------------------------------------------
# Function Types
#------------------------------------------------------------------------

# Γ ⊢ α   Γ ⊢ β
# -------------
# Γ ⊢ (α -> β)

Function = lambda dom, cod: TypeCon('->', (dom, cod))

def tyeval(node, env, ctx=None):
    ctx = ctx or set()
    assert isinstance(ctx, set)

    if isinstance(node, Atom):
        return typeof(node.name, env, ctx)

    elif isinstance(node, App):
        fn = tyeval(node.fn, env, ctx)
        arg = tyeval(node.arg, env, ctx)

        out = TypeVar()
        unify(env, Function(arg, out), fn)
        return out

    elif isinstance(node, Lambda):
        dom = TypeVar()

        scope = dict(env)
        scope[node.v] = dom

        bindings = set(ctx)
        bindings.add(dom)

        cod = tyeval(node.body, scope, bindings)
        return Function(dom, cod)

    raise Exception("Not in scope: type constructor or variable %s"
        % (node))

def typeof(term, env, bindings):
    if term in env:
        return constraints(env[term], bindings)
    elif isnumericval(term):
        return Integer
    elif isboolval(term):
        return Bool
    else:
        raise NameError("Unknown symbol %s" % term)

#------------------------------------------------------------------------
# Constraint Generation
#------------------------------------------------------------------------

def gen(ty, constrs, bindings):
    t = simplifyty(ty)

    if isinstance(t, TypeVar):
        if isbound(t, bindings):
            if t not in constrs:
                constrs[t] = TypeVar()
            return constrs[t]
        else:
            return t

    elif isinstance(t, TypeCon):
        conargs = [gen(x, constrs, bindings) for x in t.types]
        return TypeCon(t.cons, conargs)

def constraints(t, bindings):
    constrs = {}
    return gen(t, constrs, bindings)

#------------------------------------------------------------------------
# Unifiers
#------------------------------------------------------------------------

def unify(env, t1, t2):
    ctx = dict(env)

    a = simplifyty(t1)
    b = simplifyty(t2)

    if isinstance(a, TypeVar):
        if a != b:
            if occur1(a, b):
                raise TypeError("Recursive types are not supported")
            #x = TypeVar()
            #x = a._unify(b)
            a.ty = b
            return {a: b}

    elif isinstance(a, TypeCon) and isinstance(b, TypeVar):
        return unify(ctx, b, a)

    elif isinstance(a, TypeCon) and isinstance(b, TypeCon):
        if (a.cons != b.cons):
            raise TypeError("Type mismatch: %s != %s" %
                (str(a), str(b))
            )

        if len(a.types) != len(b.types):
            raise ValueError("Wrong number of arguments: %s != %s" %
                (len(a.types), len(b.types))
            )

        for p, q in zip(a.types, b.types):
            locals = unify(ctx, p, q)
            ctx.update(locals)

        return ctx

    else:
        raise Exception("Could not unify")

def simplifyty(t):
    if isinstance(t, TypeVar):
        if t.ty is not None:
            t.ty = simplifyty(t.ty)
            return t.ty
        else:
            return t
    else:
        return t

def isbound(v, bindings):
    return not occurs(v, bindings)

def occur1(var, ty):
    sty = simplifyty(ty)
    if sty == var:
        return True
    elif isinstance(sty, TypeCon):
        return occurs(var, sty.types)
    return False

def occurs(t, types):
    return any(occur1(t, t2) for t2 in types)

#------------------------------------------------------------------------
# Term Deconstructors
#------------------------------------------------------------------------

def isnumericval(name):
    try:
        int(name)
        return True
    except ValueError:
        return False

def isboolval(term):
    return isinstance(term, bool)

def isdynamic(term):
    return term == '?'

def isnumpy(term):
    try:
        dtype(term)
        return True
    except TypeError:
        return False

#------------------------------------------------------------------------
# Printing
#------------------------------------------------------------------------

class Fountain(object):
    def __init__(self, it):
        self.it = iter(it)
        self._map = {}

    def get(self, item):
        if item in self._map:
            return self._map[item]
        else:
            v = next(self.it)
            self._map[item] = v
            return v

    def __contains__(self, key):
        return key in self._map

def pprint(ty):
    freev = Fountain(letters)
    return ty.pprint(freev)

#------------------------------------------------------------------------
# Toplevel
#------------------------------------------------------------------------

def atnf(self):
    """ algebraic type normal form """
    pass

def infer(env, term):
    t = tyeval(term, env)
    print ('%s : %s' % (str(term), pprint(t)))

#------------------------------------------------------------------------
# Syntax Buidlers
#------------------------------------------------------------------------

def app(expr, vars):
    expr = expr
    for v in vars:
        expr = App(expr, v)
    return expr

def lam(vars, body):
    body = body
    for v in vars:
        body = Lambda(v, body)
    return body

sumt = lambda x,y: App(App(Atom("sum"), x), y)

# disjoint unions
def union(*xs):
    return reduce(sumt, xs)

# product types
def product(x,y):
    return App(App(Atom("product"), x), y)
