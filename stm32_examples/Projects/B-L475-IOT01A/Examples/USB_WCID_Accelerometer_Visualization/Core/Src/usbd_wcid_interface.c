/**
******************************************************************************
* @file    usbd_wcid_interface.c
* @author  SRA - Central Labs
* @version v2.1.1
* @date    26-Feb-2020
* @brief   Source file for USBD WCID interface
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

/* Includes ------------------------------------------------------------------*/
#include "usbd_wcid_interface.h"
#include "usbd_wcid_streaming.h"
#include "main.h"
#include "ai_logging.h"

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/


#define MAX_SEND_PACKET_SIZE 1024 //Size in which the data will be splitted to be sent via "FillTxDataBuffer", also defines the internal USB buffers

extern ai_logging_device_t device;
extern USBD_HandleTypeDef  USBD_Device;
volatile uint8_t streaming_started = 0;
volatile uint8_t usb_connected = 0;


uint8_t  USB_RxBuffer[APP_RX_DATA_SIZE];
uint8_t *TxBuffer[N_IN_ENDPOINTS]; // "lines" that are used for data on IN endpoints


/* Private function prototypes -----------------------------------------------*/
static int8_t WCID_STREAMING_Itf_Init     (void);
static int8_t WCID_STREAMING_Itf_DeInit   (void);
static int8_t WCID_STREAMING_Itf_Control (uint8_t isHostToDevice, uint8_t cmd, uint16_t wValue, uint16_t wIndex, uint8_t* pbuf, uint16_t length);
static int8_t WCID_STREAMING_Itf_Receive  (uint8_t* pbuf, uint32_t Len);

static void _Error_Handler( void );

int channel = 0;// chanel 0:0x81, 1:0x82,...
int endpoint = 0x81;

USBD_WCID_STREAMING_ItfTypeDef USBD_WCID_STREAMING_fops = 
{
  WCID_STREAMING_Itf_Init,
  WCID_STREAMING_Itf_DeInit,
  WCID_STREAMING_Itf_Control,
  WCID_STREAMING_Itf_Receive
};

/* Private functions ---------------------------------------------------------*/

/**
* @brief  WCID_STREAMING_Itf_Init
*         Initializes the WCID media low layer
* @param  None
* @retval Result of the operation: USBD_OK if all operations are OK else USBD_FAIL
*/
static int8_t WCID_STREAMING_Itf_Init(void)
{
  USBD_WCID_STREAMING_SetRxDataBuffer(&USBD_Device, (uint8_t *)USB_RxBuffer);
  
  usb_connected = 1;
  return (USBD_OK);
}

/**
* @brief  WCID_STREAMING_Itf_DeInit
*         DeInitializes the WCID media low layer
* @param  None
* @retval Result of the operation: USBD_OK if all operations are OK else USBD_FAIL
*/
static int8_t WCID_STREAMING_Itf_DeInit(void)
{
  return (USBD_OK);
}


/**
* @brief  WCID_STREAMING_Itf_Control
*         Manage the WCID class requests
* @param  Cmd: Command code            
* @param  Buf: Buffer containing command data (request parameters)
* @param  Len: Number of data to be sent (in bytes)
* @retval Result of the operation: USBD_OK if all operations are OK else USBD_FAIL
*/
static int8_t WCID_STREAMING_Itf_Control (uint8_t isHostToDevice, uint8_t cmd, uint16_t wValue, uint16_t wIndex, uint8_t* pbuf, uint16_t length)
{ 
  return (USBD_OK);
}

/**
* @brief  SS_WCID_Itf_DataRx
*         Data received over USB OUT endpoint are sent over WCID interface 
*         through this function.
* @param  Buf: Buffer of data to be transmitted
* @param  Len: Number of data received (in bytes)
* @retval Result of the operation: USBD_OK if all operations are OK else USBD_FAIL
*/
static int8_t WCID_STREAMING_Itf_Receive(uint8_t* Buf, uint32_t Len)
{
  ai_logging_data_received_callback(&device, Buf, Len);
  return (USBD_OK);
}

void start_streaming()
{
  if(streaming_started != 1)
  {
    for(int i = 0; i < N_IN_ENDPOINTS; i++)
    {
      TxBuffer[i] = NULL;
      TxBuffer[i] = (uint8_t*)calloc(MAX_SEND_PACKET_SIZE*2 +2, sizeof(uint8_t)); // USB Needs a buffer of size 2*MAX_SEND_PACKET + 2
      if(TxBuffer[i] == NULL)
      {
        _Error_Handler();
      }
      USBD_WCID_STREAMING_SetTxDataBuffer(&USBD_Device, i, TxBuffer[i], MAX_SEND_PACKET_SIZE);
      USBD_WCID_STREAMING_CleanTxDataBuffer(&USBD_Device, i);
    }
    USBD_WCID_STREAMING_StartStreaming(&USBD_Device);
    streaming_started = 1;
  } 
}

uint32_t usb_wcid_send_function(uint8_t *data_ptr, uint32_t data_size)
{
  int32_t bytesLeft = data_size;
  USBD_WCID_STREAMING_HandleTypeDef   *hwcid = (USBD_WCID_STREAMING_HandleTypeDef*) USBD_Device.pClassData;
  __IO uint32_t * TX_States = hwcid->TXStates;
  __IO uint8_t * TxBuffStatus = hwcid->TxBuffStatus;
  
  while(bytesLeft > 0)
  {
    if(bytesLeft - MAX_SEND_PACKET_SIZE <= 0)
    {
      // If device is ready      
      if(TX_States[channel] == 0 && TxBuffStatus[channel] == 0)
      {
        USBD_WCID_STREAMING_FillTxDataBuffer(&USBD_Device, channel, (uint8_t*)data_ptr+(data_size - bytesLeft), bytesLeft);
        bytesLeft = 0;
      }
    }
    else
    {
      // If device is ready
      if(TX_States[channel] == 0 && TxBuffStatus[channel] == 0)
      {
        USBD_WCID_STREAMING_FillTxDataBuffer(&USBD_Device, channel, (uint8_t*)data_ptr+(data_size - bytesLeft), MAX_SEND_PACKET_SIZE);     
        bytesLeft = bytesLeft - MAX_SEND_PACKET_SIZE; 
      }
    }
  }
  
  return data_size;
}

/**
* @brief  This function is executed in case of error occurrence
* @param  None
* @retval None
*/
static void _Error_Handler( void )
{
  while (1)
  {}
}





/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
