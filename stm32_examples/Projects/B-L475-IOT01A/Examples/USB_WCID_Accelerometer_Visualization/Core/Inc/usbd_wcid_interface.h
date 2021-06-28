/**
  ******************************************************************************
  * @file    usbd_wcid_interface.h
  * @author  SRA - Central Labs
  * @version v2.1.1
  * @date    26-Feb-2020
  * @brief   Header file for USBD WCID interface
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2019 STMicroelectronics.
  * All rights reserved.
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __USBD_WCID_STREAMING_IF_H
#define __USBD_WCID_STREAMING_IF_H

/* Includes ------------------------------------------------------------------*/
#include "usbd_wcid_streaming.h"
//#include "com_manager.h"

#define USB_PACKET_SIZE         MAX_SEND_PACKET_SIZE//4096*2
#define APP_TX_DATA_SIZE        (USB_PACKET_SIZE*2)
#define APP_RX_DATA_SIZE        512

#define STATE_WAITING           (uint8_t)(0x00)
#define STATE_REQUEST_SET       (uint8_t)(0x01)
#define STATE_SIZE_SENT         (uint8_t)(0x02)
#define STATE_DATA_GET          (uint8_t)(0x03)
#define STATE_DATA_SET          (uint8_t)(0x04)
#define STATE_SIZE_RCVD         (uint8_t)(0x05)



#define CMD_SET_REQ           (uint8_t)(0x00)
#define CMD_SIZE_GET          (uint8_t)(0x01)
#define CMD_DATA_GET          (uint8_t)(0x02)
#define CMD_SIZE_SET          (uint8_t)(0x03)
#define CMD_DATA_SET          (uint8_t)(0x04)

extern USBD_WCID_STREAMING_ItfTypeDef  USBD_WCID_STREAMING_fops;
uint32_t usb_wcid_send_function(uint8_t *data_ptr, uint32_t data_size);
void start_streaming();

/* Exported macro ------------------------------------------------------------*/
/* Exported functions ------------------------------------------------------- */




#endif /* __USBD_WCID_STREAMING_IF_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
