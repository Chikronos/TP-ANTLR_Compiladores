FILENAME = QueryBit.g4
PREFIX   = $(basename $(FILENAME))

# Ruta al jar de ANTLR4. Se puede sobrescribir desde la linea de comandos:
#   make ANTLR_JAR=/ruta/a/antlr-4.13.1-complete.jar
ANTLR_JAR ?= /usr/local/lib/antlr-4.13.1-complete.jar

all:
	java -jar $(ANTLR_JAR) -Dlanguage=Python3 -o gen $(FILENAME)

clean:
	rm -rf gen __pycache__
