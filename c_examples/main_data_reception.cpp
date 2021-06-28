/**
  ******************************************************************************
  * @file           : main_data_reception.cpp
  * @brief          : Small example receiving data using AILogging C interfaces
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2020-2021 STMicroelectronics.
  * All rights reserved.
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */


#include <iostream>
#include <stdio.h>
#include <time.h>

#include "usb_interface.hpp"
#include "../c_library/ai_logging.h"

#define RECEPTION_BUFFER_SIZE 1000000
#define USB_READ_SIZE 512
#define USB_WRITE_SIZE 128
#define SEND_BUFFER_SIZE 64

using namespace std;


void generateBitmapImage(unsigned char *image, int height, int width, char* imageFileName);
unsigned char* createBitmapFileHeader(int height, int width, int paddingSize);
unsigned char* createBitmapInfoHeader(int height, int width);

UsbDriver *usb = new UsbDriver();


uint32_t send_data(uint8_t *data, uint32_t size)
{
	return usb->write(data, size);
}

uint32_t receive_data(uint8_t *data, uint32_t size)
{
	return usb->read(data, size);
}

int main(int argc, char* argv[])
{
	cout<<"Starting"<<endl;

	if(argc > 2){
		cout<<"Will connect to: "<<argv[1]<<":"<<argv[2]<<endl;
		int vid = atoi(argv[1]);
		int pid = atoi(argv[2]); //  0x0483 0x5743 default with USB WCID Examples

		usb->connectTo(vid, pid);
		usb->setEndpoint(0x81);

		uint8_t send_data_buffer[SEND_BUFFER_SIZE];
		uint8_t reception_buffer[RECEPTION_BUFFER_SIZE];
		uint8_t user_buffer[100];

		ai_logging_device_t device;
		ai_logging_init(&device);
		ai_logging_init_send(&device, send_data, send_data_buffer, SEND_BUFFER_SIZE);
		ai_logging_init_receive(&device, receive_data, USB_READ_SIZE, reception_buffer, RECEPTION_BUFFER_SIZE);
		ai_logging_init_raw_data_buffer(&device, user_buffer);

		uint8_t usb_data_chunk_buffer[USB_READ_SIZE];
		int transferred=0, nb_packet_received=0, nb_to_transfer = 100;
		uint32_t total_byte_transferred = 0;

		ai_logging_packet_t packet_received = {0};

		cout<<"Starting main loop"<<endl;
		clock_t start_time = clock();

		while(nb_packet_received < nb_to_transfer)
		{
			transferred = usb->read(usb_data_chunk_buffer, sizeof(usb_data_chunk_buffer));
			ai_logging_data_received_callback(&device, usb_data_chunk_buffer, transferred);

			if(transferred != sizeof(usb_data_chunk_buffer)){
				cout<<"Error transferred != usb_data_chunk_buffer"<<endl;
			}


			int ret = ai_logging_check_for_received_packet(&device, &packet_received);
			if(ret > 0)
			{
				cout<<"Packet received: "<<(nb_packet_received+1)<<" of type:"<<packet_received.payload_type<<", size:"<<packet_received.payload_size<<endl;
				cout<<"Shape: (";
				for(int i = 0; i < packet_received.shape.n_shape; i++){
					cout<<packet_received.shape.shapes[i]<<",";
				}
				cout<<")"<<endl;
				
				total_byte_transferred += packet_received.payload_size;

				ai_logging_prepare_next_packet(&device);
				nb_packet_received += 1;
			}
			else if(ret == -1) {
				cout<<"Error -1"<<endl;
				cout<<"buffer position: "<<device.receive_buffer_position<<"/"<<device.receive_buffer_max_size<<", read_from:"<<device.receive_buffer_read_from<<", read_buffer_position"<<device.receive_buffer_position<<endl;
			} else if(ret == -3) {
				cout<<"Error -3"<<endl;
			} else if(ret == -5) {
				cout<<"Error -5"<<endl;// Corrupted packet
			} else if(ret == -6 || ret == -7 || ret == -8 || ret == -9) {
				cout<<"Error -6,-7,-8,-9"<<endl;
			} else if(ret == -10){
				cout<<"Error -10: Missing byte to read header"<<endl;
			}
			// else
			// {
			// 	cout<<"Error:"<<ret<<endl;
			// }
			
			// cout<<"transferred: "<<transferred<<endl;
			// cout<<"buffer position: "<<device.receive_buffer_position<<"/"<<sizeof(device.receive_buffer)<<endl;

			// int ret = ai_logging_wait_for_data(&device, &packet_start_index, &packet_end_index, usb_data_chunk_buffer, USB_DATA_CHUNK);
			// if(ret > 0)
			// {
			// 	cout<<"Packet received: "<<(nb_packet_received+1)<<" from "<<packet_start_index<<" to "<<packet_end_index<<" (size:"<<(packet_end_index-packet_start_index)<<")"<<endl;
			// 	nb_packet_received += 1;
			// 	packet_start_index = 0;
			// 	packet_end_index = 0;
			// }
		}


		clock_t end_time = clock();
		cout<<"End of main loop in: "<<((double)(end_time - start_time) / CLOCKS_PER_SEC)<<", total byte transferred: "<<(double)total_byte_transferred/1024.0<<"KB"<<endl;
		
		return 0;
	} else {
		cout<<"Needing information: VID and PID"<<endl;
		return 1;
	}

	cout<<"Ending"<<endl;
	return 0;
}


void print_devs(libusb_device **devs)
{
	libusb_device *dev;
	int i = 0, j = 0;
	uint8_t path[8]; 

	while ((dev = devs[i++]) != NULL) {
		struct libusb_device_descriptor desc;
		int r = libusb_get_device_descriptor(dev, &desc);
		if (r < 0) {
			fprintf(stderr, "failed to get device descriptor");
			return;
		}

		printf("%04x:%04x (bus %d, device %d)",
			desc.idVendor, desc.idProduct,
			libusb_get_bus_number(dev), libusb_get_device_address(dev));

		r = libusb_get_port_numbers(dev, path, sizeof(path));
		if (r > 0) {
			printf(" path: %d", path[0]);
			for (j = 1; j < r; j++)
				printf(".%d", path[j]);
		}
		printf("\n");
	}
}

void print_endpoint_comp(const struct libusb_ss_endpoint_companion_descriptor *ep_comp)
{
	printf("      USB 3.0 Endpoint Companion:\n");
	printf("        bMaxBurst:           %u\n", ep_comp->bMaxBurst);
	printf("        bmAttributes:        %02xh\n", ep_comp->bmAttributes);
	printf("        wBytesPerInterval:   %u\n", ep_comp->wBytesPerInterval);
}


const int bytesPerPixel = 3; /// red, green, blue
const int fileHeaderSize = 14;
const int infoHeaderSize = 40;

void generateBitmapImage(unsigned char *image, int height, int width, char* imageFileName){
    unsigned char padding[3] = {0, 0, 0};
    int paddingSize = (4 - (width*bytesPerPixel) % 4) % 4;

    unsigned char* fileHeader = createBitmapFileHeader(height, width, paddingSize);
    unsigned char* infoHeader = createBitmapInfoHeader(height, width);

    FILE* imageFile = fopen(imageFileName, "wb");

    fwrite(fileHeader, 1, fileHeaderSize, imageFile);
    fwrite(infoHeader, 1, infoHeaderSize, imageFile);

    int i;
    for(i=0; i<height; i++){
        fwrite(image+(i*width*bytesPerPixel), bytesPerPixel, width, imageFile);
        fwrite(padding, 1, paddingSize, imageFile);
    }

    fclose(imageFile);
}

unsigned char* createBitmapFileHeader(int height, int width, int paddingSize){
    int fileSize = fileHeaderSize + infoHeaderSize + (bytesPerPixel*width+paddingSize) * height;

    static unsigned char fileHeader[] = {
        0,0, /// signature
        0,0,0,0, /// image file size in bytes
        0,0,0,0, /// reserved
        0,0,0,0, /// start of pixel array
    };

    fileHeader[ 0] = (unsigned char)('B');
    fileHeader[ 1] = (unsigned char)('M');
    fileHeader[ 2] = (unsigned char)(fileSize    );
    fileHeader[ 3] = (unsigned char)(fileSize>> 8);
    fileHeader[ 4] = (unsigned char)(fileSize>>16);
    fileHeader[ 5] = (unsigned char)(fileSize>>24);
    fileHeader[10] = (unsigned char)(fileHeaderSize + infoHeaderSize);

    return fileHeader;
}

unsigned char* createBitmapInfoHeader(int height, int width){
    static unsigned char infoHeader[] = {
        0,0,0,0, /// header size
        0,0,0,0, /// image width
        0,0,0,0, /// image height
        0,0, /// number of color planes
        0,0, /// bits per pixel
        0,0,0,0, /// compression
        0,0,0,0, /// image size
        0,0,0,0, /// horizontal resolution
        0,0,0,0, /// vertical resolution
        0,0,0,0, /// colors in color table
        0,0,0,0, /// important color count
    };

    infoHeader[ 0] = (unsigned char)(infoHeaderSize);
    infoHeader[ 4] = (unsigned char)(width    );
    infoHeader[ 5] = (unsigned char)(width>> 8);
    infoHeader[ 6] = (unsigned char)(width>>16);
    infoHeader[ 7] = (unsigned char)(width>>24);
    infoHeader[ 8] = (unsigned char)(height    );
    infoHeader[ 9] = (unsigned char)(height>> 8);
    infoHeader[10] = (unsigned char)(height>>16);
    infoHeader[11] = (unsigned char)(height>>24);
    infoHeader[12] = (unsigned char)(1);
    infoHeader[14] = (unsigned char)(bytesPerPixel*8);

    return infoHeader;
}