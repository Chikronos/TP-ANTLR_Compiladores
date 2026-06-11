from QueryBitVisitor import QueryBitVisitor


class SemanticVisitor(QueryBitVisitor):

    def __init__(self):
        self.errores = []

    def _error(self, linea, mensaje):
        self.errores.append(f"  Error semantico [linea {linea}]: {mensaje}")

    # ---------- helpers ----------

    def _recolectar_columnas_select(self, ctx):
        # ctx: columnList. Devuelve lista de (nombre, linea).
        nombres = []
        nombres.append((ctx.column().ID().getText(), ctx.column().start.line))
        rest = ctx.columnRest()
        while rest is not None and rest.column() is not None:
            nombres.append((rest.column().ID().getText(), rest.column().start.line))
            rest = rest.columnRest()
        return nombres

    def _recolectar_columnas_order(self, ctx):
        # ctx: orderList. Devuelve lista de (nombre, linea).
        nombres = []
        nombres.append((ctx.orderItem().ID().getText(), ctx.orderItem().start.line))
        rest = ctx.orderRest()
        while rest is not None and rest.orderItem() is not None:
            nombres.append((rest.orderItem().ID().getText(), rest.orderItem().start.line))
            rest = rest.orderRest()
        return nombres

    # ---------- program / queryList ----------

    def visitProgram(self, ctx):
        self.visit(ctx.query())
        self.visit(ctx.queryList())

    def visitQueryList(self, ctx):
        if ctx.query() is not None:
            self.visit(ctx.query())
            self.visit(ctx.queryList())

    # ---------- query ----------

    def visitQuery(self, ctx):
        self.visit(ctx.columnList())
        self.visit(ctx.source())
        self.visit(ctx.optWhere())
        self.visit(ctx.optOrder())
        self.visit(ctx.optLimit())

    # ---------- columnList ----------

    def visitColumnList(self, ctx):
        if ctx.STAR() is not None:
            return
        nombres = self._recolectar_columnas_select(ctx)
        vistos = set()
        for nombre, linea in nombres:
            if nombre in vistos:
                self._error(linea, f"columna duplicada en SELECT: '{nombre}'")
            vistos.add(nombre)

    def visitColumnRest(self, ctx):
        pass

    def visitColumn(self, ctx):
        pass

    # ---------- source ----------

    def visitSource(self, ctx):
        if ctx.STRING() is None:
            return
        texto   = ctx.STRING().getText()
        interior = texto[1:-1]
        if interior.strip() == '':
            self._error(ctx.start.line,
                "la ruta del archivo en FROM no puede estar vacia")

    # ---------- condiciones ----------

    def visitOptWhere(self, ctx):
        if ctx.WHERE() is not None:
            self.visit(ctx.condition())

    def visitCondition(self, ctx):
        self.visit(ctx.orCondition())

    def visitOrCondition(self, ctx):
        self.visit(ctx.andCondition())
        self.visit(ctx.orRest())

    def visitOrRest(self, ctx):
        if ctx.OR() is not None:
            self.visit(ctx.andCondition())
            self.visit(ctx.orRest())

    def visitAndCondition(self, ctx):
        self.visit(ctx.primaryCondition())
        self.visit(ctx.andRest())

    def visitAndRest(self, ctx):
        if ctx.AND() is not None:
            self.visit(ctx.primaryCondition())
            self.visit(ctx.andRest())

    def visitPrimaryCondition(self, ctx):
        if ctx.predicate() is not None:
            self.visit(ctx.predicate())
        else:
            self.visit(ctx.condition())

    def visitPredicate(self, ctx):
        op_ctx  = ctx.compOp()
        val_ctx = ctx.value()
        linea   = ctx.start.line

        op            = op_ctx.getText()
        es_relacional = op in ('>', '<', '>=', '<=')
        es_string     = val_ctx.STRING() is not None

        if es_relacional and es_string:
            col = ctx.ID().getText()
            self._error(linea,
                f"el operador '{op}' no es valido con STRING "
                f"en '{col} {op} {val_ctx.getText()}'")

    def visitCompOp(self, ctx):
        pass

    def visitValue(self, ctx):
        pass

    # ---------- ORDER BY ----------

    def visitOptOrder(self, ctx):
        if ctx.ORDER() is None:
            return
        nombres = self._recolectar_columnas_order(ctx.orderList())
        vistos  = set()
        for nombre, linea in nombres:
            if nombre in vistos:
                self._error(linea, f"columna duplicada en ORDER BY: '{nombre}'")
            vistos.add(nombre)

    def visitOrderList(self, ctx):
        pass

    def visitOrderRest(self, ctx):
        pass

    def visitOrderItem(self, ctx):
        pass

    def visitOrderDir(self, ctx):
        pass

    # ---------- LIMIT ----------

    def visitOptLimit(self, ctx):
        if ctx.LIMIT() is None:
            return

        texto = ctx.NUMBER().getText()
        linea = ctx.start.line

        if '.' in texto:
            self._error(linea,
                f"LIMIT debe ser un entero positivo, no decimal: '{texto}'")
        elif int(texto) <= 0:
            self._error(linea,
                f"LIMIT debe ser mayor a 0, se encontro: '{texto}'")

    # ---------- interfaz publica ----------

    def analizar(self, tree):
        self.visit(tree)
        return self.errores
