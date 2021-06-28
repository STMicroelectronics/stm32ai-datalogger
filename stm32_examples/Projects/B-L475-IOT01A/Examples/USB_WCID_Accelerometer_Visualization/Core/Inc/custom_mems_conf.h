/**
 ******************************************************************************
 * @file    custom_mems_conf.h
 * @author  MEMS Application Team
 * @version V7.0.0
 * @date    24-June-2019
 * @brief   This file contains definitions of the MEMS components bus interfaces for custom boards 
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
#ifndef __CUSTOM_MEMS_CONF_H__
#define __CUSTOM_MEMS_CONF_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32l4xx_hal.h"
#include "b_l475e_iot01a1_bus.h"
#include "b_l475e_iot01a1_errno.h"

/* USER CODE BEGIN 1 */

/* USER CODE END 1 */

#define USE_CUSTOM_MOTION_SENSOR_LSM6DSL_0        1U

#define CUSTOM_LSM6DSL_0_I2C_Init BSP_I2C2_Init
#define CUSTOM_LSM6DSL_0_I2C_DeInit BSP_I2C2_DeInit
#define CUSTOM_LSM6DSL_0_I2C_ReadReg BSP_I2C2_ReadReg
#define CUSTOM_LSM6DSL_0_I2C_WriteReg BSP_I2C2_WriteReg

#ifdef __cplusplus
}
#endif

#endif /* __CUSTOM_MEMS_CONF_H__*/

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
