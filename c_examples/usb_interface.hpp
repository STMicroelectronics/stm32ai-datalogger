/**
  ******************************************************************************
  * @file           : usb_interface.hpp
  * @brief          : Definition of USB interface wrapped around libusb 
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


#ifndef USB_INTERFACE_HPP
#define USB_INTERFACE_HPP

#include <iostream>
#include "interfaces.hpp"
#include "libusb.h"

//#define USB_DATA_CHUNK 128

class UsbDriver : public DriverInterface {
public:
	UsbDriver();
	UsbDriver(int vid, int pid);
	~UsbDriver();
	
	int connectTo(int vid, int pid);
	int bulkTransfer(uint8_t endpoint, uint8_t *data, int size, int *transferred);
	void setEndpoint(int endpoint);

	// Methods of the DriverInterface
	uint8_t connect();
	uint8_t disconnect();
	uint32_t write(uint8_t *data, uint32_t size);
	uint32_t read(uint8_t *buffer, uint32_t size);
	uint32_t byteAvailable();
	uint8_t isConnected();

private:
	libusb_device_handle *dev_handle;
	bool connected;
	int selectedEndpoint;
	int vid;
	int pid;
};

#endif
	