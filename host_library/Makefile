CC=g++
CFLAGS=-Wall -g
LDFLAGS=-I../c_library
OBJ_DIR = build-objects
OUT_DIR = out
 
OBJ_LOCATION := $(wildcard $(OBJ_DIR)/*.o)

ifeq ($(OS),Windows_NT)
	DLL_NAME=libai_logging.dll
	LIB_DEFINES = -DUSING_AI_LOGGING_DLL -DBUILDING_AI_LOGGING_DLL
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		DLL_NAME=libai_logging.so
	endif
	ifeq ($(UNAME_S),Darwin)
		DLL_NAME=libai_logging.dylib
	endif
	CFLAGS += -fPIC
endif
 
all: dll target_dll export_to_wrapper
	@echo "Building all"
	@echo OBJ_LOCATION: $(OBJ_LOCATION)

target_dll:dll main_dll.c
	mkdir -p $(OUT_DIR)
	$(CC) -c main_dll.c $(LIB_DEFINES) -I../c_library $(CFLAGS)
	$(CC) -o $(OUT_DIR)/main_dll main_dll.o -Lout -lai_logging

dll:
	@echo "Building $(DLL_NAME)"
	mkdir -p $(OBJ_DIR)
	mkdir -p $(OUT_DIR)

	$(CC) -c $(LIB_DEFINES) -o $(OBJ_DIR)/$(DLL_NAME).o ../c_library/ai_logging.c $(LDFLAGS) $(CFLAGS)
	$(CC) -shared -o $(OUT_DIR)/$(DLL_NAME) $(OBJ_DIR)/$(DLL_NAME).o 
	# -Wl,--out-implib,out/ai_logging.a old option used while building old library


ai_logging.o: ../c_library/ai_logging.c
	@echo "Building ai_logging"
	mkdir -p $(OBJ_DIR)
	$(CC) -c -o $(OBJ_DIR)/$@ ../c_library/ai_logging.c $(LDFLAGS) $(CFLAGS)

export_to_wrapper:$(OUT_DIR)/$(DLL_NAME)
	@echo "Copying library to Python wrapper folder"
	cp $(OUT_DIR)/$(DLL_NAME) ../python_wrapper/ai_logging/core

clean:
	rm -f $(OBJ_DIR)/*.o
	rm -f $(OBJ_DIR)/dll/*.o
	rm -f *.o
	rm -f out/*.exe
	rm -f out/*.dll
	rm -f out/*.a
	rm -f out/*dylib
