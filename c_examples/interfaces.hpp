/**
  ******************************************************************************
  * @file           : interfaces.hpp
  * @brief          : Define a common interface to be used to write/read data 
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

#ifndef INTERFACES_H
#define INTERFACES_H

#include <stdint.h>

class DriverInterface
{
public:
	virtual uint8_t connect()=0;
	virtual uint8_t disconnect()=0;
	virtual uint32_t write(uint8_t *data, uint32_t size)=0;
	virtual uint32_t read(uint8_t *buffer, uint32_t size)=0;
	virtual uint32_t byteAvailable()=0;
	virtual uint8_t isConnected()=0;
};

#endif
