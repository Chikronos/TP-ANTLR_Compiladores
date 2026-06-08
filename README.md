# TP-ANTLR\_Compiladores: QueryBit

Repositorio del Trabajo Parcial y Final del curso **Teoría de Compiladores (1ACC0236)**, UPC, ciclo 2026-1. Contiene el diseño y la implementación progresiva de **QueryBit**, un lenguaje de dominio específico (DSL) inspirado en SQL para consultar y filtrar archivos estructurados (`.csv`).

## 1. Contexto del proyecto

El proyecto se entrega en tres hitos. Este repositorio cubre actualmente el **Hito 1: Trabajo Parcial**.

| Hito | Semana | Alcance |
|------|--------|---------|
| Hito 1: Trabajo Parcial | 7 | Gramática en ANTLR4, archivos `.g4`, driver mínimo, demo de la gramática. |
| Hito 2: Segundo Avance | 12 | Arquitectura del compilador, plan de validación, ~50% de la implementación. |
| Hito 3: Trabajo Final | 15 | Front end y back end completos, generación de código intermedio con LLVM, validación y conclusiones. |


## 2. Problemática y motivación

Muchas tareas de análisis de datos requieren filtrar y proyectar columnas sobre archivos `.csv`. Las herramientas actuales (motores SQL, hojas de cálculo o lenguajes de propósito general) introducen una sobrecarga innecesaria cuando el caso de uso es realmente simple. **QueryBit** propone un DSL declarativo, mínimo y autoejecutable, con una sintaxis cercana a SQL (`SELECT ... FROM ... WHERE ...`), pensado específicamente para ese escenario.

## 3. Objetivos

### 3.1. Objetivo general
Diseñar e implementar QueryBit, un DSL para consultas y filtrado condicional sobre archivos estructurados, aplicando un flujo de compilación que incluya gramática en ANTLR4, análisis sintáctico, validación semántica mediante tabla de símbolos y generación de código intermedio con LLVM.

### 3.2. Objetivos específicos
- Definir una sintaxis declarativa inspirada en SQL para operaciones `FROM`, `SELECT`, `WHERE`, `ORDER BY` y `LIMIT`.
- Construir una gramática en ANTLR4 que reconozca correctamente las consultas válidas de QueryBit y reporte errores en las inválidas.
- Implementar, en hitos posteriores, una tabla de símbolos para validar el uso de columnas y la generación de código intermedio mediante LLVM.

## 4. Estructura del repositorio

```text
TP-ANTLR_Compiladores/
├── README.md                       # este archivo
├── .gitignore                      # excluye artefactos generados por ANTLR
├── grammar/                        # entregables de Hito 1
│   ├── QueryBit.g4                 # gramática combinada (lexer + parser)
│   ├── Makefile                    # genera el lexer y el parser en Python3
│   ├── main.py                     # driver: tokens + árbol sintáctico + resumen
│   ├── commands-showcase.md        # comandos para reproducir las pruebas
│   └── tests/
│       ├── entrada0.txt             # consulta verbatim  fuente
│       ├── entrada1.txt ... entrada4.txt   # consultas válidas adicionales
        └── error1.txt   ... error4.txt     # consultas inválidas

```

## 5. Gramática (Hito 1)

`grammar/QueryBit.g4` es una gramática combinada (lexer + parser). Reconoce:

- Selección de columnas: `SELECT * | col1, col2, ...`.
- Origen de datos: ruta entre comillas (`"clientes.csv"`) o identificador.
- Filtros booleanos con paréntesis y operadores `AND`/`OR`, con **precedencia AND > OR** (estratificación explícita en `orCondition` / `andCondition`).
- Predicados de comparación con `>`, `<`, `==`, `!=`, `>=`, `<=`.
- `ORDER BY col [ASC|DESC] (, col [ASC|DESC])*`.
- `LIMIT n` con literal numérico.
- Palabras clave **insensibles a mayúsculas** (estilo SQL).
- Comentarios de una línea con `--` y de bloque con `/* ... */` (multi-línea).

### Ejemplo de consulta válida

```sql
SELECT nombre, edad
FROM "clientes.csv"
WHERE edad >= 18 AND pais == "Peru"
ORDER BY edad DESC, nombre ASC
LIMIT 10;
```

## 6. Cómo ejecutar

### 6.1. Requisitos
- **Java** (para ejecutar `antlr-4.13.1-complete.jar`).
- **Python 3** y el runtime `antlr4-python3-runtime`; Se utiliza Python 3.11 para mayor compatibilidad.
- **ANTLR 4.13.1** (`antlr-4.13.1-complete.jar`). El `Makefile` detecta automáticamente si existe un ejecutable `antlr4` en el `PATH` (típicamente un script o symlink) y, si no, cae al invocador `java -jar $(ANTLR_JAR)`. Por defecto `ANTLR_JAR=/usr/local/lib/antlr-4.13.1-complete.jar`; se puede sobrescribir desde la línea de comandos. *Aviso*: los aliases de shell (`alias antlr4='...'`) no se propagan a las sub-shells de `make`; para que `make` los use, deben estar instalados como ejecutables en el `PATH`.

#### Para Linux


##### Prerrequisitos del sistema (ejecutar solo una vez)

##### Ubuntu / Debian

```bash
sudo apt update

sudo apt install -y \
    python3.11 \
    python3.11-venv \
    openjdk-17-jdk \
    curl
```

Instalar `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reiniciar shell o ejecutar:

```bash
source $HOME/.local/bin/env
```

##### `requirements.txt`

```text
antlr4-python3-runtime==4.13.2
antlr4-tools==0.2.2
```

##### Configuración inicial del proyecto (ejecutar solo una vez)

Ejecutar todo en la raíz del proyecto:

```bash
echo "3.11" > .python-version

uv venv --python 3.11
source .venv/bin/activate

uv pip install -r requirements.txt
```

##### Activar entorno virtual (ejecutar en cada nueva sesión)

```bash
source .venv/bin/activate
```

##### Regenerar lexer/parser ANTLR

Ejecutar cada vez que se modifique `QueryBit.g4`:

```bash
cd grammar
antlr4 -Dlanguage=Python3 QueryBit.g4
```

##### Ejecutar pruebas

```bash
cd grammar

for f in tests/entrada*.txt tests/error*.txt; do
    echo "===== $(basename "$f") ====="
    python3 main.py "$f"
done
```

#### Para Windows


##### Prerrequisitos del sistema (ejecutar solo una vez)

```powershell
winget install Python.Python.3.11
winget install EclipseAdoptium.Temurin.17.JDK
winget install astral-sh.uv
```

##### `requirements.txt`

```text
antlr4-python3-runtime==4.13.2
antlr4-tools==0.2.2
```

##### Configuración inicial del proyecto (ejecutar solo una vez)

Ejecutar todo en la raíz del proyecto:

```powershell
'3.11' | Out-File .python-version

uv venv --python 3.11
.\.venv\Scripts\Activate.ps1

uv pip install -r requirements.txt
```

##### Activar entorno virtual (ejecutar en cada nueva sesión de shell)

```powershell
.\.venv\Scripts\Activate.ps1
```

##### Regenerar lexer/parser ANTLR

Ejecutar cada vez que se modifique `QueryBit.g4`:

```powershell
cd grammar
antlr4 -Dlanguage=Python3 QueryBit.g4
```

##### Ejecutar pruebas

```powershell
cd grammar

gci tests\entrada*.txt, tests\error*.txt | % {
    Write-Host "===== $($_.Name) ====="
    python3 main.py $_.FullName
}
```



### 6.2. Generar lexer y parser

En Linux/macOS:

```bash
cd grammar
make
```

En Windows (PowerShell):

```powershell
cd grammar
java -jar C:\ruta\a\antlr-4.13.1-complete.jar -Dlanguage=Python3 QueryBit.g4
```

### 6.3. Ejecutar el driver

```bash
python3 main.py tests/entrada1.txt    # consulta válida; imprime tokens, árbol y resumen
python3 main.py tests/error1.txt      # consulta inválida; el resumen reporta errores
```

Por cada archivo procesado, el driver emite tres bloques:

1. **Tokens**: tabla `TIPO | TEXTO` con cada token producido por el lexer (omite `EOF`).
2. **Arbol sintactico**: representación textual del árbol mediante `toStringTree`.
3. **Resumen**: número de consultas reconocidas (`tree.query()`), número de errores sintácticos (`parser.getNumberOfSyntaxErrors()`) y un estado `OK` o `con errores`.

## 7. Casos de prueba

Los casos de prueba viven en `grammar/tests/`. Cada archivo cubre una característica distinta de la gramática. Los `entradaN.txt` deben parsear correctamente; los `errorN.txt` deben fallar de manera predecible.

### 7.1. Resumen de cada caso

| Archivo | Tipo | Característica que valida |
|---------|------|---------------------------|
| `tests/entrada1.txt` | válido | Forma mínima: `SELECT * FROM "ruta.csv";` y comentario de línea con `--`. |
| `tests/entrada2.txt` | válido | `WHERE` con combinación `AND`/`OR`; ejercita la precedencia AND > OR. |
| `tests/entrada3.txt` | válido | `WHERE` + `ORDER BY` multi-columna con `ASC`/`DESC` + `LIMIT`. |
| `tests/entrada4.txt` | válido | Múltiples consultas en un mismo archivo, paréntesis en `WHERE`, palabras clave mezcladas en mayúsculas/minúsculas, número decimal. |
| `tests/error1.txt`   | inválido | Falta el `;` final; el parser exige `SEMI` para cerrar la consulta. |
| `tests/error2.txt`   | inválido | Operador `=` no soportado; la gramática usa `==` para igualdad. |
| `tests/error3.txt`   | inválido | `ORDER` sin `BY`; la gramática exige la pareja `ORDER BY`. |
| `tests/error4.txt`   | inválido | Identificador inválido (`1columna`); los `ID` no pueden iniciar con dígito. |

### 7.2. Comandos

Ejecutar primero la generación del lexer y parser (sección 6.2), luego, desde subcarpeta `grammar/`:

```bash
# ----- entradas válidas -----

# entrada0: consulta verbatim del informe fuente
python3 main.py tests/entrada0.txt

# entrada1: SELECT * mínimo + comentario '--'
python3 main.py tests/entrada1.txt

# entrada2: WHERE con AND/OR (precedencia AND > OR)
python3 main.py tests/entrada2.txt

# entrada3: ORDER BY multi-columna + LIMIT
python3 main.py tests/entrada3.txt

# entrada4: múltiples consultas, paréntesis, mayúsculas/minúsculas mezcladas
python3 main.py tests/entrada4.txt


# ----- entradas inválidas (deben reportar error de parseo) -----

# error1: falta ';' al cierre
python3 main.py tests/error1.txt

# error2: operador '=' no aceptado (la gramática exige '==')
python3 main.py tests/error2.txt

# error3: 'ORDER' sin 'BY'
python3 main.py tests/error3.txt

# error4: identificador que comienza con dígito
python3 main.py tests/error4.txt

```

Para una ejecución secuencial de todos los casos:

```bash
# Linux / macOS / Git Bash
for f in tests/entrada*.txt tests/error*.txt; do
  echo "===== $f ====="
  python3 main.py "$f"
done
```

```powershell
# PowerShell
gci tests\entrada*.txt, tests\error*.txt | % {
  Write-Host "===== $($_.Name) ====="
  python3 main.py $_.FullName
}
```

El mismo listado, con explicaciones detalladas, está en [`grammar/commands-showcase.md`](grammar/commands-showcase.md).
