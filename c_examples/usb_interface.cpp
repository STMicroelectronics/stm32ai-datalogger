/**
  ******************************************************************************
  * @file           : usb_interface.cpp
  * @brief          : Implementation of USB interface wrapped around libusb 
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


#include "usb_interface.hpp"

using namespace std;

UsbDriver::UsbDriver()
{
	this->dev_handle = NULL;
	this->vid = -1;
	this->pid = -1;
	this->connected = false;
}

UsbDriver::UsbDriver(int vid, int pid)
{
	this->vid = vid;
	this->pid = pid;
	this->connected = false;
}

UsbDriver::~UsbDriver()
{
	libusb_exit(NULL);
	cout<<"Destroying object"<<endl;
}

int UsbDriver::connectTo(int vid, int pid)
{
	this->connected = false;

	int r = libusb_init(NULL);
	if (r < 0) 
	{
		cout<<"Error while initializing libusb"<<endl;
		return 1;
	}

	this->dev_handle = libusb_open_device_with_vid_pid(NULL,vid,pid);	
	if(dev_handle == NULL)
	{
		cout<<"Error while creating device handle"<<endl;
		return 1;
	}

	r = libusb_set_configuration(this->dev_handle, 1);
	if(r != 0)
	{
		cout<<"Error while setting configuration\n"<<endl;
		return r;
	}

	r = libusb_claim_interface(this->dev_handle, 0);
	if(r != 0)
	{
		cout<<"Error while caiming the interface\n"<<endl;
	}

	this->connected = true;
	return 0;
}

int UsbDriver::bulkTransfer(uint8_t endpoint, uint8_t *data, int size, int *transferred)
{
	if(!this->connected)
	{
		cout<<"API is not connected, please connect first";
		return -1;
	}

	if(this->dev_handle == NULL)
	{
		cout<<"Can't make bulk transfer because device if not initialized"<<endl;
		return -1;
	}

	int r = libusb_bulk_transfer(this->dev_handle, endpoint, data, size, transferred, 100);

	if(*transferred != size){
		cout<<"Warning: data transferred not equal to data to read/write ("<<*transferred<<"/"<<size<<")"<<endl;
	}

	if(r != 0 && r != LIBUSB_ERROR_TIMEOUT)
	{
		cout<<"Error while making bulk transfer : "<< r <<endl;
		if(r == LIBUSB_ERROR_TIMEOUT) {
			cout<<"Timeout error"<<endl;
		} else if(r == LIBUSB_ERROR_PIPE) {
			cout<<"Pipe error"<<endl;
		} else if(r == LIBUSB_ERROR_OVERFLOW) {
			cout<<"Overflow error"<<endl;
		} else if(r == LIBUSB_ERROR_NO_DEVICE) {
			cout<<"No device error"<<endl;
		} else if(r == LIBUSB_ERROR_BUSY){
			cout<<"Busy error"<<endl;
		} else if(r == LIBUSB_ERROR_IO) {
			cout<<"I/O standard error"<<endl;
		} else if(r == LIBUSB_ERROR_NOT_FOUND) {
			cout<<"Not found error"<<endl;
		} else {
			cout<<"Other error"<<endl;
		}
		
		return r;
	}

	return 0;
}

void UsbDriver::setEndpoint(int endpoint)
{
	this->selectedEndpoint = endpoint;
}


// Methods of the DriverInterface
uint8_t UsbDriver::connect()
{
	return connectTo(this->vid, this->pid);
}

uint8_t UsbDriver::disconnect()
{
	return 1; //TODO: To implement
}

uint32_t UsbDriver::write(uint8_t *data, uint32_t size)
{
	int transferred = 0;
	int ret = bulkTransfer(this->selectedEndpoint, data, size, &transferred);
	if(ret != 0)
	{
		cout<<"Error while writing to USB: "<<ret<<endl;
	}
	return transferred;
}

uint32_t UsbDriver::read(uint8_t *buffer, uint32_t size)
{
	int transferred = 0;
	int ret = bulkTransfer(this->selectedEndpoint, buffer, size, &transferred);
	
	//cout<<"Transferred: "<<transferred<<endl;
	
	if(ret != 0)
	{
		cout<<"Error while reading to USB: "<<ret<<endl;
	}
	if(transferred < 0)
	{
		transferred = 0;
	}
	return (uint32_t) transferred;
}

uint32_t UsbDriver::byteAvailable()
{
	return 64;
}
uint8_t UsbDriver::isConnected()
{
	return this->connected;
}