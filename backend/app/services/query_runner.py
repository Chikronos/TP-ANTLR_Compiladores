import os
import sys

from ..config import GRAMMAR_DIR, DATA_DIR

if GRAMMAR_DIR not in sys.path:
    sys.path.insert(0, GRAMMAR_DIR)

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

try:
    from QueryBitLexer   import QueryBitLexer
    from QueryBitParser  import QueryBitParser
    from SemanticVisitor import SemanticVisitor
    ANTLR_OK = True
except ImportError as _e:
    ANTLR_OK = False
    _ANTLR_ERR = str(_e)

from .query_executor import ExecutionVisitor


class _ErrorCollector(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errores.append((line, column, msg))


def _contar_queries(program_ctx) -> int:
    if program_ctx is None:
        return 0
    count = 1
    lista = program_ctx.queryList()
    while lista is not None and lista.query() is not None:
        count += 1
        lista = lista.queryList()
    return count


def run_single_query(query_text: str, csv_base_dir: str = None) -> dict:
    """
    Corre UNA query por las 3 etapas: léxica → sintáctica → semántica → ejecución.
    Siempre retorna un dict; nunca lanza excepción al caller.
    """
    if not ANTLR_OK:
        return _err_result(
            exec_error=f"Parser no disponible — corre 'make' en grammar/. Detalle: {_ANTLR_ERR}"
        )

    if not query_text.strip():
        return _err_result(syntactic_errors=["Query vacía."])

    # ── Léxico ────────────────────────────────────────────────────────────────
    collector    = _ErrorCollector()
    input_stream = InputStream(query_text)

    lexer = QueryBitLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(collector)
    stream = CommonTokenStream(lexer)
    stream.fill()

    # ── Sintáctico ────────────────────────────────────────────────────────────
    parser = QueryBitParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(collector)
    tree = parser.program()

    errores_sin = collector.errores
    n_queries   = _contar_queries(tree) if tree is not None else 0

    # ── Semántico ─────────────────────────────────────────────────────────────
    errores_sem = []
    if not errores_sin and tree is not None:
        visitor     = SemanticVisitor()
        errores_sem = visitor.analizar(tree)

    # ── Ejecución (solo si no hay errores) ───────────────────────────────────
    data       = None
    exec_error = None
    if not errores_sin and not errores_sem:
        try:
            base     = csv_base_dir or DATA_DIR
            executor = ExecutionVisitor(csv_base_dir=os.path.abspath(base))
            data     = executor.ejecutar(tree)
        except Exception as e:
            exec_error = str(e)

    total  = len(errores_sin) + len(errores_sem)
    status = "ok" if total == 0 and exec_error is None else "error"

    return {
        "status":            status,
        "n_queries_parsed":  n_queries,
        "syntactic_errors":  [f"[linea {l}, col {c}] {m}" for l, c, m in errores_sin],
        "semantic_errors":   [f"[linea {l}] {m}"          for l, m  in errores_sem],
        "total_errors":      total,
        "data":              data,
        "execution_error":   exec_error,
    }


def _err_result(**kwargs) -> dict:
    base = {
        "status": "error", "n_queries_parsed": 0,
        "syntactic_errors": [], "semantic_errors": [],
        "total_errors": 1, "data": None, "execution_error": None,
    }
    base.update(kwargs)
    if kwargs.get("syntactic_errors"):
        base["total_errors"] = len(kwargs["syntactic_errors"])
    return base