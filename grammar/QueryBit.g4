grammar QueryBit;

// ========== REGLAS DEL PARSER ==========

// ---------- PUNTO DE ENTRADA
//  queryList reemplaza query+ con recursión explícita + ε
program   : query queryList EOF ;
queryList : query queryList | ;

// ---------- CONSULTA
//  SELECT <columnas> FROM <tabla>
//    [ WHERE   <condicion>      ]
//    [ ORDER BY <lista_orden>   ]
//    [ LIMIT   <numero>         ] ;
//
//  Las cláusulas opcionales se expresan como producciones ε
//  (optWhere, optOrder, optLimit) en lugar del operador '?'
//  de EBNF, para quedar alineadas con la teoría de CFGs.
query
    : SELECT columnList
      FROM source
      optWhere
      optOrder
      optLimit
      SEMI
    ;

// ---------- CLÁUSULAS OPCIONALES (producciones ε)
//  Cada regla tiene dos alternativas: la cláusula presente o vacía (ε).
//  Esto es la representación directa en CFG de un elemento opcional.
optWhere : WHERE condition | ;
optOrder : ORDER BY orderList | ;
optLimit : LIMIT NUMBER       | ;

// ---------- COLUMNAS
//  '*'  o  col1, col2, ...
//  columnRest reemplaza (COMMA column)* con recursión explícita + ε
columnList
    : STAR
    | column columnRest
    ;
columnRest : COMMA column columnRest | ;

column : ID ;

// ---------- ORIGEN DE DATOS
//  ruta entre comillas ("clientes.csv") o identificador
source : STRING | ID ;

// ---------- CONDICIONES
//  Precedencia (de menor a mayor):
//    1. OR
//    2. AND
//    3. paréntesis y predicados primarios
//
//  La estratificación garantiza que 'a AND b OR c' se interprete
//  como '(a AND b) OR c', alineado con la semántica de SQL.
condition : orCondition ;

//  orRest  reemplaza (OR  andCondition)*  con recursión explícita + ε
//  andRest reemplaza (AND primaryCondition)* con recursión explícita + ε
orCondition  : andCondition orRest ;
orRest       : OR andCondition orRest | ;

andCondition : primaryCondition andRest ;
andRest      : AND primaryCondition andRest | ;

primaryCondition
    : LPAREN condition RPAREN
    | predicate
    ;

// ---------- PREDICADO
//  columna  <op>  valor   (ej. edad >= 18)
predicate : ID compOp value ;

compOp : GT | LT | EQ | NEQ | GTE | LTE ;

value : NUMBER | STRING ;

// ---------- ORDEN
//  ORDER BY col1 ASC, col2 DESC
//  orderRest reemplaza (COMMA orderItem)* con recursión explícita + ε
orderList : orderItem orderRest ;
orderRest : COMMA orderItem orderRest | ;

//  La dirección es opcional: se expresa con producción ε
//  en lugar de (ASC | DESC)?
orderItem : ID orderDir ;
orderDir  : ASC | DESC | ;


// ========== REGLAS DEL LEXER ==========

// ---------- PALABRAS CLAVE
//  Insensibles a mayúsculas (estilo SQL).
//  Deben ir ANTES que ID para tener mayor prioridad.
SELECT  : [sS][eE][lL][eE][cC][tT] ;
FROM    : [fF][rR][oO][mM] ;
WHERE   : [wW][hH][eE][rR][eE] ;
ORDER   : [oO][rR][dD][eE][rR] ;
BY      : [bB][yY] ;
LIMIT   : [lL][iI][mM][iI][tT] ;
AND     : [aA][nN][dD] ;
OR      : [oO][rR] ;
ASC     : [aA][sS][cC] ;
DESC    : [dD][eE][sS][cC] ;

// ---------- OPERADORES RELACIONALES
//  >= y <= van ANTES que > y < para que '<=' no se
//  tokenice como '<' seguido de '='.
GTE : '>=' ;
LTE : '<=' ;
NEQ : '!=' ;
EQ  : '==' ;
GT  : '>'  ;
LT  : '<'  ;

// ---------- DELIMITADORES
SEMI    : ';' ;
COMMA   : ',' ;
STAR    : '*' ;
LPAREN  : '(' ;
RPAREN  : ')' ;

// ---------- LITERALES
//  NUMBER con dos alternativas explícitas en lugar de ('.' [0-9]+)?
//  DECIMAL va ANTES que ENTERO para que '3.14' no se tokenice como '3'
fragment DIGITOS : [0-9]+ ;
NUMBER  : DIGITOS '.' DIGITOS
        | DIGITOS
        ;
STRING  : '"' ~["\r\n]* '"' ;

// ---------- IDENTIFICADORES
//  Va al final para no capturar palabras clave.
ID : [a-zA-Z_] [a-zA-Z_0-9]* ;

// ---------- COMENTARIOS
//  -- comentario de una línea (estilo SQL)
LINE_COMMENT : '--' ~[\r\n]* -> skip ;

//  /* ... */ comentario de bloque (puede abarcar varias líneas).
//  BLOCK_CHAR define qué carácter es válido dentro del comentario:
//    - cualquier carácter que no sea '*'
//    - o un '*' seguido de algo que no sea '/' (permite asteriscos
//      dentro del cuerpo sin cerrar el comentario prematuramente).
fragment BLOCK_CHAR : ~[*] | '*' ~[/] ;
BLOCK_COMMENT : '/*' BLOCK_CHAR* '*/' -> skip ;

// ---------- IGNORADOS: espacios en blanco
WS : [ \t\r\n]+ -> skip ;
