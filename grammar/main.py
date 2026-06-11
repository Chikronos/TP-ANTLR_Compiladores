import sys
from antlr4 import CommonTokenStream, FileStream, Token
from antlr4.error.ErrorListener import ErrorListener
from QueryBitLexer import QueryBitLexer
from QueryBitParser import QueryBitParser
from SemanticVisitor import SemanticVisitor


class _ErrorCollector(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errores.append((line, column, msg))


def contar_queries(program_ctx):
    if program_ctx is None:
        return 0
    count = 1
    lista = program_ctx.queryList()
    while lista is not None and lista.query() is not None:
        count += 1
        lista = lista.queryList()
    return count


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo.qb>")
        sys.exit(1)

    archivo = sys.argv[1]
    input_stream = FileStream(archivo, encoding='utf-8')

    collector = _ErrorCollector()

    # 1) Lexer: produce los tokens.
    lexer = QueryBitLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(collector)
    stream = CommonTokenStream(lexer)
    stream.fill()

    # 2) Parser: construye el arbol sintactico desde la regla 'program'.
    parser = QueryBitParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(collector)
    tree = parser.program()

    errores_sin = collector.errores
    n_queries   = contar_queries(tree) if tree is not None else 0

    # 3) Analisis semantico (solo si no hay errores sintacticos).
    errores_sem = []
    if not errores_sin and tree is not None:
        visitor = SemanticVisitor()
        errores_sem = visitor.analizar(tree)

    # 4) Output.
    if errores_sin:
        print(f"Errores sintácticos ({len(errores_sin)}):")
        for linea, col, msg in errores_sin:
            print(f"  [linea {linea}, col {col}] {msg}")
    else:
        print("Errores sintácticos:   ninguno")

    print()

    if errores_sem:
        print(f"Errores semánticos ({len(errores_sem)}):")
        for linea, msg in errores_sem:
            print(f"  [linea {linea}] {msg}")
    else:
        print("Errores semánticos:    ninguno")

    total = len(errores_sin) + len(errores_sem)
    ok    = total == 0
    print()
    print(f"Consultas: {n_queries}  |  Total errores: {total}  |  Estado: {'OK' if ok else 'con errores'}")

    if not ok:
        sys.exit(1)


main()
