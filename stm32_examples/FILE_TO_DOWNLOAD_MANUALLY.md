# Files to be added manually

STM32 Projects are using STM32CubeH7 and STM32CubeL4
First you need to download:
- [STM32CubeH7](https://github.com/STMicroelectronics/STM32CubeH7/tree/v1.9.0)
- [STM32CubeL4](https://github.com/STMicroelectronics/STM32CubeL4/tree/v1.17.0)

Then dispatch files:
- Copy CMSIS Includes: *STM32CubeH7/Drivers/CMSIS/Include* to **Drivers/CMSIS/Include**
- Copy CMSIS specific to the board: *STM32CubeH7/Drivers/CMSIS/Device/ST/STM32H7xx* to **Drivers/CMSIS/Device/ST/STM32H7xx**
- Copy Board BSP: *STM32CubeH7/Drivers/BSP/STM32H747I-DISCO* to **Drivers/STM32H747I-DISCO**
- Copy HAL Driver: *STM32CubeH7/Drivers/STM32H7xx_HAL_Driver* to **Drivers/STM32H7xx_HAL_Driver**

- Copy CMSIS specific to the board: *STM32CubeL4/Drivers/CMSIS/Device/ST/STM32L4xx* to **Drivers/CMSIS/Device/ST/STM32L4xx**
- Copy Board BSP: *STM32CubeL4/Drivers/BSP/B-L475E-IOT01* to **Drivers/B-L475E-IOT01**
- Copy HAL Driver: *STM32CubeL4/Drivers/STM32L4xx_HAL_Driver* to **Drivers/STM32L4xx_HAL_Driver**
- Copy USB Middleware: *STM32CubeL4/Middlewares/ST/* to **Middlewares/ST**
