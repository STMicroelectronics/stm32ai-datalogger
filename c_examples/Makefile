CC=g++
CFLAGS=-Wall -g
LDFLAGS=-Ilibusb-1.0.23/include/libusb-1.0 -I../target_api -Llibusb-1.0.23/MinGW64/static -lusb-1.0
OBJ_DIR = build-objects
OUT_DIR = out
C_LIBRARY_PATH = ../c_library

OBJ_NAME := $(patsubst %.cpp,%.o, $(wildcard *.cpp))
OBJ_LOCATION := $(wildcard $(OBJ_DIR)/*.o)

TARGET_NAME_1=usb_wcid_data_receiver.exe
TARGET_NAME_2=image_ping_pong_usb_wcid.exe

all: target_1 target_2
	@echo "Building all"
	@echo OBJ_NAME: $(OBJ_NAME)
	@echo OBJ_LOCATION: $(OBJ_LOCATION)
	@echo "Be sure to flash the correct sotfware on STM32 to make the connection !"

target_1:$(OBJ_NAME) ai_logging.o
	@echo OBJ_NAME: $(OBJ_NAME)
	@echo OBJ_LOCATION: $(OBJ_LOCATION)
	mkdir -p $(OUT_DIR)
	mkdir -p $(OBJ_DIR)
	$(CC) -g -o $(OUT_DIR)/$(TARGET_NAME_1) $(OBJ_DIR)/*.o main_data_reception.o $(LDFLAGS) $(CFLAGS)

target_2:$(OBJ_NAME) ai_logging.o
	mkdir -p $(OUT_DIR)
	mkdir -p $(OBJ_DIR)
	$(CC) -g -o $(OUT_DIR)/$(TARGET_NAME_2) $(OBJ_DIR)/*.o main_image_ping_pong_usb_wcid.o $(LDFLAGS) $(CFLAGS)

main_data_reception.o: main_data_reception.cpp
	@echo "Building main"
	$(CC) -c -o $@ main_data_reception.cpp $(LDFLAGS) $(CFLAGS)

main_image_ping_pong_usb_wcid.o: main_image_ping_pong_usb_wcid.cpp
	@echo "Building main_image_ping_pong_usb_wcid"
	$(CC) -c -o $@ main_image_ping_pong_usb_wcid.cpp $(LDFLAGS) $(CFLAGS)

usb_interface.o: usb_interface.cpp
	@echo "Building usb_interface"
	mkdir -p $(OUT_DIR)
	mkdir -p $(OBJ_DIR)
	$(CC) -c -g -o $(OBJ_DIR)/$@ usb_interface.cpp $(LDFLAGS) $(CFLAGS)

usb_async_interface.o: usb_async_interface.cpp
	@echo "Building usb_async_interface"
	mkdir -p $(OUT_DIR)
	mkdir -p $(OBJ_DIR)
	$(CC) -c -g -o $(OBJ_DIR)/$@ usb_async_interface.cpp $(LDFLAGS) $(CFLAGS)


ai_logging.o: $(C_LIBRARY_PATH)/ai_logging.c
	@echo "Building ai_logging"
	mkdir -p $(OUT_DIR)
	mkdir -p $(OBJ_DIR)
	$(CC) -c -o $(OBJ_DIR)/$@ $(C_LIBRARY_PATH)/ai_logging.c $(LDFLAGS) $(CFLAGS)

clean:
	rm -f $(OBJ_DIR)/*.o
	rm -f $(OBJ_DIR)/dll/*.o
	rm -f *.o
	rm -f $(OUT_DIR)/*.exe
	rm -f $(OUT_DIR)/*.dll
	rm -f $(OUT_DIR)/*.a

