/**
  ******************************************************************************
  * @file           : main_serial_read.cpp
  * @brief          : Simple example acting as a serial reader 
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


#include <stdio.h>
#include <errno.h>
#include <fcntl.h> 
#include <string.h>
#include <unistd.h>

#include "../c_library/ai_logging.h"

#define RECEPTION_BUFFER_SIZE 100000
#define SERIAL_READ_SIZE 16


int comPortHandle = -1;

uint32_t send_data(uint8_t *data, uint32_t size)
{
    return write(comPortHandle, data, size);
}

uint32_t receive_data(uint8_t *data, uint32_t size)
{
    return read(comPortHandle, data, size);
}

int main(int argc, char* argv[])
{
	printf("Starting\n");

	if(argc > 1){
		printf("Will connect to: %s\n", argv[1]);

        comPortHandle = open(argv[1], O_RDONLY);
        if(comPortHandle < 0)
        {
            printf("Error while opening port\n");
            return -1;
        }

		uint8_t reception_buffer[RECEPTION_BUFFER_SIZE];

		ai_logging_device_t device;
		ai_logging_init(&device);
		ai_logging_init_receive(&device, receive_data, SERIAL_READ_SIZE, reception_buffer, RECEPTION_BUFFER_SIZE);

		ai_logging_packet_t packet_received = {0};

		printf("Starting main loop\n");
		while(1)
		{
            int ret = ai_logging_wait_for_data(&device, &packet_received);
            printf("Packet received\n");
        }
		return 0;
	} else {
		printf("Needing information: COMPORT\n");
		return 1;
	}

	printf("Ending");
	return 0;
}
