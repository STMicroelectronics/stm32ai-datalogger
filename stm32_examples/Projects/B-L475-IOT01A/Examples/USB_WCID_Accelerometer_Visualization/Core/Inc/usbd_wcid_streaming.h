/**
******************************************************************************
* @file    usbd_wcid_streaming.h
* @author  SRA
* @version v1.1.1
* @date    17-Jan-2020
* @brief   header file for usbd wcid streaming class 
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
 
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __USBD_WCID_SREAMING_H
#define __USBD_WCID_SREAMING_H

#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include  "usbd_ioreq.h"

/** @addtogroup STM32_USB_DEVICE_LIBRARY
  * @{
  */
  
/** @defgroup USBD_WCID_STREAMING
  * @brief This file is the Header file for usbd_wcid_streaming.c
  * @{
  */ 


/** @defgroup USBD_WCID_STREAMING_Exported_Defines
  * @{
  */ 
#define N_CHANNELS_MAX                                9

#define N_IN_ENDPOINTS                                2     
#define DATA_IN_EP1                                   0x81  /* EP1 for data IN */
#define DATA_IN_EP2                                   0x82  /* EP2 for data IN */
#define DATA_IN_EP3                                   0x83  /* EP3 for data IN */
#define DATA_IN_EP4                                   0x84  /* EP4 for data IN */
#define DATA_IN_EP5                                   0x85  /* EP5 for data IN */
#define DATA_OUT_EP1                                  0x01  /* EP1 for data OUT */

#define SS_WCID_DATA_FS_MAX_PACKET_SIZE               64  /* Endpoint IN & OUT Packet size */

#define USB_SS_WCID_CONFIG_DESC_SIZ                   (25 + 7 * N_IN_ENDPOINTS)
#define SS_WCID_DATA_HS_IN_PACKET_SIZE                SS_WCID_DATA_HS_MAX_PACKET_SIZE
#define SS_WCID_DATA_HS_OUT_PACKET_SIZE               SS_WCID_DATA_HS_MAX_PACKET_SIZE

#define SS_WCID_DATA_FS_IN_PACKET_SIZE                SS_WCID_DATA_FS_MAX_PACKET_SIZE
#define SS_WCID_DATA_FS_OUT_PACKET_SIZE               SS_WCID_DATA_FS_MAX_PACKET_SIZE
    
#define  USB_DESC_TYPE_OS_FEATURE_EXT_PROPERTIES      4
#define  USB_DESC_TYPE_OS_FEATURE_EXT_COMPAT_ID       5   
#define  USB_DESC_TYPE_CUSTOM_IN_EP_DESCRIPTION       7
#define  USB_DESC_TYPE_USER_CONTROL_ID                0
    
#define STREAMING_STATUS_IDLE                          0x00
#define STREAMING_STATUS_STARTED                       0x01
#define STREAMING_STATUS_STOPPING                      0x02

/**
  * @}
  */ 


/** @defgroup USBD_WCID_STREAMING_Exported_TypesDefinitions
  * @{
  */

/**
  * @}
  */ 

typedef struct _USBD_WCID_STREAMING_Itf
{
  int8_t (* Init)          (void);
  int8_t (* DeInit)        (void);
  int8_t (* Control)       (uint8_t, uint8_t, uint16_t, uint16_t, uint8_t * , uint16_t);   
  int8_t (* Receive)       (uint8_t *, uint32_t);  

}USBD_WCID_STREAMING_ItfTypeDef;


typedef struct
{
  uint32_t data[SS_WCID_DATA_FS_MAX_PACKET_SIZE];      /* Force 32bits alignment */
  uint8_t  CmdOpCode;
  uint16_t  CmdLength;    
  uint16_t  wValue;    
  uint16_t  wIndex;    
  uint8_t  *RxBuffer;  
  uint8_t  *CurrentTxBuffer;   
  uint32_t RxLength;
  uint32_t TxLength; 
  __IO uint32_t TXStates[N_IN_ENDPOINTS];
  __IO uint8_t lastPacketSent[N_IN_ENDPOINTS];
  __IO uint32_t RxState;   
  uint32_t TxBuffIdx[N_CHANNELS_MAX];
  __IO uint8_t TxBuffStatus[N_CHANNELS_MAX];
  __IO uint8_t TxBuffReset[N_CHANNELS_MAX];
  uint16_t USB_DataSizePerEp[N_CHANNELS_MAX];
  uint8_t * TxBuffer[N_CHANNELS_MAX]; 
  uint8_t streamingStatus;
}
USBD_WCID_STREAMING_HandleTypeDef; 



/** @defgroup USBD_WCID_STREAMING_Exported_Macros
  * @{
  */ 
  
/**
  * @}
  */ 

/** @defgroup USBD_WCID_STREAMING_Exported_Variables
  * @{
  */ 

extern USBD_ClassTypeDef  USBD_WCID_STREAMING;
#define USBD_WCID_STREAMING_CLASS    &USBD_WCID_STREAMING
/**
  * @}
  */ 

/** @defgroup USBD_WCID_STREAMING_Exported_Functions
  * @{
  */
uint8_t USBD_WCID_STREAMING_RegisterInterface        (USBD_HandleTypeDef *pdev, USBD_WCID_STREAMING_ItfTypeDef *fops);
uint8_t USBD_WCID_STREAMING_SetRxDataBuffer          (USBD_HandleTypeDef *pdev, uint8_t  *ptr);  
uint8_t USBD_WCID_STREAMING_SetTxDataBuffer          (USBD_HandleTypeDef *pdev, uint8_t ch_number, uint8_t * ptr, uint16_t size);
uint8_t USBD_WCID_STREAMING_CleanTxDataBuffer        (USBD_HandleTypeDef *pdev, uint8_t ch_number);
uint8_t USBD_WCID_STREAMING_FillTxDataBuffer         (USBD_HandleTypeDef *pdev, uint8_t ch_number, uint8_t * buf, uint32_t size);
uint8_t USBD_WCID_STREAMING_StartStreaming           (USBD_HandleTypeDef *pdev);
uint8_t USBD_WCID_STREAMING_StopStreaming            (USBD_HandleTypeDef *pdev);

uint8_t USBD_WCID_STREAMING_TransmitPacket(USBD_HandleTypeDef *pdev, uint8_t epNumber);

/**
  * @}
  */ 

#ifdef __cplusplus
}
#endif

#endif  /* __USBD_WCID_SREAMING_H */
/**
  * @}
  */ 

/**
  * @}
  */ 
  
/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
