/** \file
  * @author Romain LE DONGE
  * @brief Simple example using the AILogging shared library to check that everything is linking fine
  * Copyright (c) 2020-2021 STMicroelectronics.
  * All rights reserved.
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
*/

#include <stdio.h>
#include <stdlib.h>

#include "../c_library/ai_logging.h"

#define SEND_BUFFER_SIZE 64

uint32_t send_function(uint8_t *buf, uint32_t len)
{
    printf("Fake sending data (%ld):\n", len);
    for(int i = 0; i < len; i++){printf("%x ",buf[i]);}
    printf("\n");
    return len;
}


int main()
{
    printf("Start\n");
    ai_logging_device_t dev;
    uint8_t send_buffer[SEND_BUFFER_SIZE];
    uint16_t data[] = {1,2,3,4,5};

    ai_logging_init(&dev);
    ai_logging_init_send(&dev, send_function, send_buffer, SEND_BUFFER_SIZE);
    
    ai_logging_buffer data_buffer;
    data_buffer.buffer = (uint8_t*)data;
    data_buffer.size = sizeof(data);

    ai_logging_tensor data_info;
    data_info.data_type = AI_UINT16;
    ai_logging_shape s;
    ai_logging_create_shape_1d(&s, 5);
    data_info.shape = &s;

    ai_logging_send_data(&dev, data_buffer, data_info);

    printf("End\n");
    return 0;
}
