# Nombre de los ejecutables
TARGET1 = Rsa
TARGET2 = Rsa_native

# Archivos fuente
SRC1 = Rsa.c
SRC2 = Rsa_native.c 

# Flags del compilador
CFLAGS = -Wall
CFLAGS2 = -Wall -O3 -march=native -mtune=native
LDFLAGS = -lcrypto -lm

# Regla predeterminada: compilar ambos ejecutables
all: $(TARGET1) $(TARGET2)

# Regla para compilar el primer ejecutable
$(TARGET1): $(SRC1)
	$(CC) $(CFLAGS) -o $(TARGET1) $(SRC1) $(LDFLAGS)

# Regla para compilar el segundo ejecutable
$(TARGET2): $(SRC2)
	$(CC) $(CFLAGS2) -o $(TARGET2) $(SRC2) $(LDFLAGS)

# Regla para limpiar archivos generados 	*.csv
clean:
	rm -f $(TARGET1) $(TARGET2) *.o  


# Regla para ejecutar el primer ejecutable
run1: $(TARGET1)
	./$(TARGET1)

# Regla para ejecutar el segundo ejecutable
run2: $(TARGET2)
	./$(TARGET2)