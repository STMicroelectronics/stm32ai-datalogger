/**
  ******************************************************************************
  * @file           : main_image_ping_pong_usb_wcid.cpp
  * @brief          : Example using AILogging 'RAW' api to send/receive images
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2020-2021 STMicroelectronics.
  * All rights reserved.
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  *
  ******************************************************************************
  */


#include <iostream>
#include <stdio.h>
#include <fstream>

#include "usb_interface.hpp"
#include "../c_library/ai_logging.h"

#define USB_READ_SIZE 1000
#define USB_WRITE_SIZE 128
#define RECEIVE_BUFFER_MAX_SIZE 100000
#define SEND_BUFFER_MAX_SIZE 1024

using namespace std;

UsbDriver *usb = new UsbDriver();

int allocFileContentInBuffer(string filename, uint8_t **buffer, uint32_t *size)
{
    uint32_t fileSize = 0;
    ifstream file (filename, ios::in|ios::binary|ios::ate);
    if (file.is_open())
    {
        fileSize = file.tellg();
        *buffer = new uint8_t[fileSize];
        file.seekg (0, ios::beg);
        file.read((char*)(*buffer), fileSize);
        *size = fileSize;
        file.close();
        return 1;
    }
    else return 0;
}

int writeDataToFile(string filename, uint8_t *buffer, uint32_t size)
{
    ofstream file(filename, ios::out|ios::binary);
    if(file.is_open())
    {
        file.write((const char*)buffer, size);
        file.close();
        return 1;
    }
    else
    {
        cout<<"Error while trying to write file"<<endl;
        return 0;
    }
    
}

int areBufferIdentical(uint8_t *buf1, uint32_t buf1_size, uint8_t *buf2, uint32_t buf2_size)
{
    if(buf1_size != buf2_size)
    {
        cout<<"Buffer length are not identical"<<endl;
        return -1;
    }

    for(int i = 0; i < buf1_size; i++)
    {
        if(buf1[i] != buf2[i])
        {
            cout<<"Buffer mismatch found at: "<<i<<endl;
            return 0;
        }
    }
    return 1;
}

uint32_t send_data(uint8_t *data, uint32_t size)
{
    usb->setEndpoint(0x01);
	return usb->write(data, size);
}

uint32_t receive_data(uint8_t *data, uint32_t size)
{
    usb->setEndpoint(0x81);
	return usb->read(data, size);
}

// Image injection from Host to STM32
int main(int argc, char* argv[])
{
	cout<<"Starting"<<endl;

    usb->connectTo(0x0483, 0x5743);

    uint8_t *fileBuffer;
    uint32_t fileSize;
    cout<<"Example sending / receiving images using 'RAW' AILogging API"<<endl;

    if(argc > 1)
    {
        if(!allocFileContentInBuffer(argv[1], &fileBuffer, &fileSize))
        {
            cout<<"Error while reading file, file not found";
            return 1;
        }
    }
    else 
    {
        cout<<"Missing image file to be sent"<<endl;
        return -1;
    }


    // allocating the image based on a file of 30KB
    
    cout<<"File loaded of size: "<<fileSize<<endl;
    writeDataToFile("sent_image.png", fileBuffer, fileSize);

    uint8_t send_data_buffer[SEND_BUFFER_MAX_SIZE];
    uint8_t working_buffer[RECEIVE_BUFFER_MAX_SIZE];

    ai_logging_device_t device;
    ai_logging_init(&device);
    ai_logging_init_send(&device, send_data, send_data_buffer, SEND_BUFFER_MAX_SIZE);
    ai_logging_init_receive(&device, receive_data, USB_READ_SIZE, working_buffer, RECEIVE_BUFFER_MAX_SIZE);
     
    uint8_t usb_reception_buffer[USB_READ_SIZE];
    ai_logging_packet_t packet = {0};
    int transferred = 0;

    cout<<"Starting main loop"<<endl;

    // Data injection (Ping...)
    ai_logging_send_header_for_raw_data(&device, 0x99, fileSize);
    for(uint32_t i = 0; i < fileSize; i += USB_WRITE_SIZE)
    {
        if(i + USB_WRITE_SIZE <= fileSize)
        {
            ai_logging_send_raw_data(&device, fileBuffer+i, USB_WRITE_SIZE);
        }
        else
        {
            ai_logging_send_raw_data(&device, fileBuffer+i, fileSize-i);   
        }
    }
    cout<<"File is sent"<<endl;

    cout<<"Receiving..."<<endl;
    // Data reception (... Pong)
    usb->setEndpoint(0x81);
    while(1)
    {
        transferred = usb->read(usb_reception_buffer, sizeof(usb_reception_buffer));
        ai_logging_data_received_callback(&device, usb_reception_buffer, transferred);

        /*if(transferred != sizeof(usb_reception_buffer)){
            cout<<"Error transferred("<<transferred<<") != usb_data_chunk_buffer("<<sizeof(usb_reception_buffer)<<")"<<endl;
        }*/

        int ret = ai_logging_check_for_received_packet(&device, &packet);
        if(ret > 0)
        {
            cout<<"Packet received"<<endl;
            writeDataToFile("received_file.png", packet.payload, packet.payload_size);
            if(areBufferIdentical(fileBuffer, fileSize, packet.payload, packet.payload_size))
            {
                cout<<"Packet correctly received"<<endl;
            }
            else
            {
                cout<<"Packet received is currupted"<<endl;
            }
            
            ai_logging_prepare_next_packet(&device);
            break;
        }
        else if(/*ret==-1 || */ret==-3 || ret==-5 || ret==-6 || ret==-7 || ret==-8 || ret==-9 /*|| ret==-10*/) {
            // -1: no start byte found in actual data
            // -10: not enough data in actual buffer 
            cout<<"Error "<<ret<<endl;
        } 
    }
    

    // Emptying USB Buffers to be sure no data left
    usb->read(usb_reception_buffer, sizeof(usb_reception_buffer));
    usb->read(usb_reception_buffer, sizeof(usb_reception_buffer));
    usb->read(usb_reception_buffer, sizeof(usb_reception_buffer));


	cout<<"Ending"<<endl;
	return 0;
}