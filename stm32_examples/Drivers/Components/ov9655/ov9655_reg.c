/**
  ******************************************************************************
  * @file    ov9655_reg.c
  * @author  MCD Application Team
  * @brief   This file provides unitary register function to control the OV9655 
  *          Camera driver.   
  ******************************************************************************
  * @attention
  *
** Copyright (c) 2015 STMicroelectronics.
** All rights reserved.
** This software is licensed under terms that can be found in the LICENSE file in
** the root directory of this software component.
** If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "ov9655_reg.h"

/** @addtogroup BSP
  * @{
  */
  
/** @addtogroup Components
  * @{
  */ 

/** @addtogroup OV9655
  * @brief     This file provides a set of functions needed to drive the 
  *            OV9655 Camera codec.
  * @{
  */

/************** Generic Function  *******************/
/*******************************************************************************
* Function Name : ov9655_read_reg
* Description   : Generic Reading function. It must be fullfilled with either
*                 I2C or SPI reading functions
* Input         : Register Address, length of buffer
* Output        : Data Read
*******************************************************************************/
int32_t ov9655_read_reg(ov9655_ctx_t *ctx, uint16_t reg, uint8_t *pdata, uint16_t length)
{
  return ctx->ReadReg(ctx->handle, reg, pdata, length);
}

/*******************************************************************************
* Function Name : OV9655_Write_Reg
* Description   : Generic Writing function. It must be fullfilled with either
*                 I2C or SPI writing function
* Input         : Register Address, Data to be written, length of buffer
* Output        : None
*******************************************************************************/
int32_t ov9655_write_reg(ov9655_ctx_t *ctx, uint16_t reg, uint8_t *data, uint16_t length)
{
  return ctx->WriteReg(ctx->handle, reg, data, length);
}

/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
