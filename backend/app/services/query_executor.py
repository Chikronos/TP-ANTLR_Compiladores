import os
import sys
import pandas as pd

from ..config import GRAMMAR_DIR, DATA_DIR

if GRAMMAR_DIR not in sys.path:
    sys.path.insert(0, GRAMMAR_DIR)

try:
    from QueryBitVisitor import QueryBitVisitor

    class ExecutionVisitor(QueryBitVisitor):
        """Recorre el AST de QueryBit y ejecuta cada query contra su CSV con pandas."""

        def __init__(self, csv_base_dir: str = None):
            self.csv_base_dir = csv_base_dir or DATA_DIR
            self._resultados: list = []

        def ejecutar(self, tree) -> list:
            self._resultados = []
            self.visitProgram(tree)
            return self._resultados

        # ── traversal ─────────────────────────────────────────────────────────

        def visitProgram(self, ctx):
            self._run_query(ctx.query())
            self.visitQueryList(ctx.queryList())

        def visitQueryList(self, ctx):
            if ctx.query() is not None:
                self._run_query(ctx.query())
                self.visitQueryList(ctx.queryList())

        # ── ejecución de una sola query ────────────────────────────────────────

        def _run_query(self, ctx):
            # 1. Cargar CSV
            raw_path = ctx.source().STRING().getText()[1:-1]
            full_path = (
                raw_path
                if os.path.isabs(raw_path)
                else os.path.join(self.csv_base_dir, raw_path)
            )
            df = pd.read_csv(full_path)

            # 2. WHERE
            opt_where = ctx.optWhere()
            if opt_where.WHERE() is not None:
                mask = self._condition_mask(opt_where.condition(), df)
                df = df[mask].reset_index(drop=True)

            # 3. SELECT columnas
            col_list = ctx.columnList()
            if col_list.STAR() is None:
                cols = self._collect_select_cols(col_list)
                df = df[cols]

            # 4. ORDER BY
            opt_order = ctx.optOrder()
            if opt_order.ORDER() is not None:
                col_names, ascending = self._collect_order_info(opt_order.orderList())
                df = df.sort_values(by=col_names, ascending=ascending)

            # 5. LIMIT
            opt_limit = ctx.optLimit()
            if opt_limit.LIMIT() is not None:
                n = int(opt_limit.NUMBER().getText())
                df = df.head(n)

            self._resultados.append({
                "rows": len(df),
                "columns": list(df.columns),
                "data": df.to_dict(orient="records")
            })

        # ── helpers de columnas ────────────────────────────────────────────────

        def _collect_select_cols(self, ctx) -> list:
            cols = [ctx.column().ID().getText()]
            rest = ctx.columnRest()
            while rest is not None and rest.column() is not None:
                cols.append(rest.column().ID().getText())
                rest = rest.columnRest()
            return cols

        def _collect_order_info(self, ctx):
            col_names, ascending = [], []

            def _parse(item_ctx):
                col  = item_ctx.ID().getText()
                full = item_ctx.getText().upper()
                asc  = not full.endswith("DESC")
                return col, asc

            col, asc = _parse(ctx.orderItem())
            col_names.append(col); ascending.append(asc)
            rest = ctx.orderRest()
            while rest is not None and rest.orderItem() is not None:
                col, asc = _parse(rest.orderItem())
                col_names.append(col); ascending.append(asc)
                rest = rest.orderRest()
            return col_names, ascending

        # ── masks para WHERE ───────────────────────────────────────────────────

        def _condition_mask(self, ctx, df):
            return self._or_mask(ctx.orCondition(), df)

        def _or_mask(self, ctx, df):
            mask = self._and_mask(ctx.andCondition(), df)
            rest = ctx.orRest()
            while rest is not None and rest.OR() is not None:
                mask = mask | self._and_mask(rest.andCondition(), df)
                rest = rest.orRest()
            return mask

        def _and_mask(self, ctx, df):
            mask = self._primary_mask(ctx.primaryCondition(), df)
            rest = ctx.andRest()
            while rest is not None and rest.AND() is not None:
                mask = mask & self._primary_mask(rest.primaryCondition(), df)
                rest = rest.andRest()
            return mask

        def _primary_mask(self, ctx, df):
            if ctx.predicate() is not None:
                return self._predicate_mask(ctx.predicate(), df)
            return self._condition_mask(ctx.condition(), df)

        def _predicate_mask(self, ctx, df):
            col     = ctx.ID().getText()
            op      = ctx.compOp().getText()
            val_ctx = ctx.value()

            if val_ctx.STRING() is not None:
                val = val_ctx.STRING().getText()[1:-1]
            else:
                texto = val_ctx.NUMBER().getText()
                val   = float(texto) if "." in texto else int(texto)

            ops = {
                ">":  lambda s, v: s > v,
                "<":  lambda s, v: s < v,
                ">=": lambda s, v: s >= v,
                "<=": lambda s, v: s <= v,
                "==": lambda s, v: s == v,
                "=":  lambda s, v: s == v,
                "!=": lambda s, v: s != v,
                "<>": lambda s, v: s != v,
            }
            fn = ops.get(op)
            if fn is None:
                raise ValueError(f"Operador no soportado: '{op}'")
            return fn(df[col], val)

except ImportError:
    class ExecutionVisitor:
        def __init__(self, *args, **kwargs): pass
        def ejecutar(self, tree) -> list:
            raise RuntimeError(
                "QueryBitVisitor.py no encontrado. "
                "Ejecuta 'make' dentro de grammar/ para generar el parser."
            )