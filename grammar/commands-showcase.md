# QueryBit - Commands Showcase

Comandos para regenerar el lexer/parser desde la gramática y ejecutar las pruebas. Se recomienda ejecutarlos en Ubuntu via VM Oracle VirtualBox accediendo al proyecto desde la carpeta compartida.

---

## Ubuntu (VM Oracle VirtualBox)

### Si uv no está en PATH después de instalar

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Configuración del proyecto (una sola vez)

VBoxSF no soporta symlinks, el venv se crea en el home:

```bash
mkdir -p ~/envs
uv venv ~/envs/querybit --python 3.11
source ~/envs/querybit/bin/activate
uv pip install antlr4-python3-runtime==4.13.2 antlr4-tools==0.2.2
```

### Activar entorno virtual (cada nueva sesión)

```bash
source ~/envs/querybit/bin/activate
cd TP-ANTLR_Compiladores
```

### Regenerar lexer/parser

```bash
cd grammar
make
```

Invoca `java -jar /usr/local/lib/antlr-4.13.1-complete.jar` directamente. Si el jar no está en esa ruta, descargarlo con:

```bash
curl -o /usr/local/lib/antlr-4.13.1-complete.jar \
  https://www.antlr.org/download/antlr-4.13.1-complete.jar
```

Los archivos generados van a `grammar/gen/`.

### Configurar PYTHONPATH y ejecutar

```bash
cd grammar
export PYTHONPATH=gen
```

#### Entradas válidas

```bash
python3 main.py tests/entrada0.txt   # SELECT * minimo
python3 main.py tests/entrada1.txt   # WHERE con AND/OR, comentario --
python3 main.py tests/entrada2.txt   # precedencia AND > OR
python3 main.py tests/entrada3.txt   # ORDER BY multi-columna + LIMIT
python3 main.py tests/entrada4.txt   # multiples consultas, case insensitive
python3 main.py tests/entrada5.txt   # comentarios de bloque /* ... */
```

#### Errores sintácticos

```bash
python3 main.py tests/sint_error1.txt   # falta ';' al final
python3 main.py tests/sint_error2.txt   # operador '=' no soportado (usar '==')
python3 main.py tests/sint_error3.txt   # ORDER sin BY
python3 main.py tests/sint_error4.txt   # identificador comienza con dígito
python3 main.py tests/sint_error5.txt   # comentario de bloque sin cerrar
```

#### Errores semánticos

```bash
python3 main.py tests/sem_error1.txt    # columna duplicada en SELECT
python3 main.py tests/sem_error2.txt    # operador relacional con STRING
python3 main.py tests/sem_error3.txt    # LIMIT con valor decimal
python3 main.py tests/sem_error4.txt    # columna duplicada en ORDER BY
python3 main.py tests/sem_error5.txt    # ruta FROM vacia
```

#### Todos los casos de una vez

```bash
echo "━━━━━━━━━━ ENTRADAS VÁLIDAS ━━━━━━━━━━" && for f in tests/entrada*.txt; do echo "  ▒▒ $(basename $f)"; python3 main.py "$f"; echo; done && echo "━━━━━━━━━━ ERRORES SINTÁCTICOS ━━━━━━━━━━" && for f in tests/sint_error*.txt; do echo "  ▒▒ $(basename $f)"; python3 main.py "$f"; echo; done && echo "━━━━━━━━━━ ERRORES SEMÁNTICOS ━━━━━━━━━━" && for f in tests/sem_error*.txt; do echo "  ▒▒ $(basename $f)"; python3 main.py "$f"; echo; done
```

### Limpiar artefactos generados

```bash
make clean
```

Elimina `grammar/gen/` y `__pycache__/`.

---

## Windows (PowerShell)

### Activar entorno virtual (cada nueva sesión)

```powershell
cd TP-ANTLR_Compiladores
.\.venv\Scripts\Activate.ps1
```

### Regenerar lexer/parser

```powershell
cd grammar
java -jar C:\ruta\a\antlr-4.13.1-complete.jar -Dlanguage=Python3 -o gen QueryBit.g4
```

Si `antlr4` está en el PATH:

```powershell
antlr4 -Dlanguage=Python3 -o gen QueryBit.g4
```

### Configurar PYTHONPATH y ejecutar

```powershell
cd grammar
$env:PYTHONPATH = "gen"
```

#### Entradas válidas

```powershell
python main.py tests\entrada0.txt
python main.py tests\entrada1.txt
python main.py tests\entrada2.txt
python main.py tests\entrada3.txt
python main.py tests\entrada4.txt
python main.py tests\entrada5.txt
```

#### Errores sintácticos

```powershell
python main.py tests\sint_error1.txt
python main.py tests\sint_error2.txt
python main.py tests\sint_error3.txt
python main.py tests\sint_error4.txt
python main.py tests\sint_error5.txt
```

#### Errores semánticos

```powershell
python main.py tests\sem_error1.txt
python main.py tests\sem_error2.txt
python main.py tests\sem_error3.txt
python main.py tests\sem_error4.txt
python main.py tests\sem_error5.txt
```

#### Todos los casos de una vez

```powershell
Write-Host "━━━━━━━━━━ ENTRADAS VÁLIDAS ━━━━━━━━━━"; gci tests\entrada*.txt | % { Write-Host "  ▒▒ $($_.Name)"; python main.py $_.FullName; "" }; Write-Host "━━━━━━━━━━ ERRORES SINTÁCTICOS ━━━━━━━━━━"; gci tests\sint_error*.txt | % { Write-Host "  ▒▒ $($_.Name)"; python main.py $_.FullName; "" }; Write-Host "━━━━━━━━━━ ERRORES SEMÁNTICOS ━━━━━━━━━━"; gci tests\sem_error*.txt | % { Write-Host "  ▒▒ $($_.Name)"; python main.py $_.FullName; "" }
```

### Limpiar artefactos generados

```powershell
Remove-Item -Recurse -Force gen, __pycache__ -ErrorAction SilentlyContinue
```
