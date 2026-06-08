import sys
from antlr4 import CommonTokenStream, FileStream, Token
from QueryBitLexer import QueryBitLexer
from QueryBitParser import QueryBitParser


def imprimir_tokens(stream):
    print("Tokens:")
    print(f"  {'TIPO':<14} TEXTO")
    print(f"  {'-'*14} {'-'*30}")
    for token in stream.tokens:
        if token.type == Token.EOF:
            continue
        nombre = QueryBitLexer.symbolicNames[token.type]
        print(f"  {nombre:<14} {repr(token.text)}")
    print()


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo.qb>")
        sys.exit(1)

    archivo = sys.argv[1]
    input_stream = FileStream(archivo, encoding='utf-8')

    # 1) Lexer: produce los tokens.
    lexer  = QueryBitLexer(input_stream)
    stream = CommonTokenStream(lexer)
    stream.fill()
    ##imprimir_tokens(stream)

    # 2) Parser: construye el arbol sintactico desde la regla 'program'.
    parser = QueryBitParser(stream)
    tree   = parser.program()

    ##print("Arbol sintactico:")
    ##print(f"  {tree.toStringTree(recog=parser)}")
    ##print()

    # 3) Resumen: numero de consultas reconocidas y de errores sintacticos.
    n_errors  = parser.getNumberOfSyntaxErrors()
    n_queries = len(tree.query()) if tree is not None else 0
    print("Resumen:")
    print(f"  Consultas reconocidas: {n_queries}")
    print(f"  Errores sintacticos:   {n_errors}")
    print(f"  Estado:                {'OK' if n_errors == 0 else 'con errores'}")


main()
