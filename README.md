# GenericDataLogger
GenericDataLogger is a project composed of tools that format and log data with ease, especially 
between a STM32 and a computer.

GenericDataLogger includes:
- A library written in C called *AILogging* which defines an API generic enough to log any kind of 
  data between an STM32 and a computer in both direction. This is the same library used on computer 
  and STM32 side.
- A *Python wrapper* written on top of the AILogging library to get a High Level and easy to use 
  API. This Python API is provided as standard Python module named *ai_logging*.
- An application called *GenericUI* written in Python providing features like data vizualisation 
  (text, image, graph plot), data recording and data injection.

GenericDataLogger **does not** includes:
- The interface to transmit data between host and STM32. You have to choose which interface you want
   to use. Examples are provided using USB CDC and USB WCID interfaces, but can be implemented using
    UART, Bluetooth, Ethernet,... 


The are multiple ways to use the tools contained in the GenericDataLogger project:
- If you have set up a STM32 to STM32 communication, you will only need the AILogging C API on both 
  STM32. The AILogging C API will format the data to send and decode the received data.
- If you have set up a STM32 to Computer communication, you will need the AILogging C API on STM32. 
  On the computer however, you have 3 solutions:
    - AILogging C API: Make your own C software by using the AILogging C API.
    - Python wrapper modules ai_logging: Make your own python software and access to AILogging C 
    functions with the python wrapper.
    - GenericUI: Use our user interface to interact with the STM32 and display, plot and save data. GenericUI can already connect to Serial and USB communication interface whereas the 2 other 
    solutions need you to transmit the data by yourself with the communication interface of your 
    choice. 


```
 ___Computer___________________________________         
|      |                   |              | In |        
| HOST <=>   GenericUI /  <=> C AILogging | ter| <===\ 
| App  <=> Py ai_logging  <=>             | fa |     ||   
|______|___________________|______________|_ce_|     || Data  
                                                     ||
                                                     || Transmission
 ___STM32______________________________              ||
|               |                | In  |             ||
| STM32 App    <=> C AILogging   | ter | <===========/
|               |                | fa  |
|______________ |_____________  _|_ce__|
```



## Setup
### Using the AILogging C API
- You can use directly the C sources provided in the **c_library** folder to communicate between 
STM32 and a computer
- You can also build the library into a shared library using the Makefile provided in 
**host_library**. You will need *gcc* and *make*  

#### How to use AILogging C API ?
- Global init: you have to perform data structures initialization. This includes initialization of: 
the device structure calld *ai_logging_device_t* which holds data about your communication devices 
and internal library variables. This is done through *ai_logging_init(...)* function.

- Send feature init: if you want to send data, you have to do this initialization step though 
*ai_logging_init_send(...)* function. You will need to specify buffer to use to send data and your
own function to send the data through the communication interface (USB CDC, USB WCID, UART,...).
Please refer to C examples located in *c_examples* and *stm32_examples*. When this is done you are
able to use function like *ai_logging_send_packet(...)* to send your data.

- Receive feature init: if you want to receive data, you have to do this initialization step using
*ai_logging_init_receive(...)* function. You will need to specify the reception buffer to use and 
the reception function to use. If you are using interrupts to receive your data (through USB for
example), you can ignore this parameter and pass NULL to *receive_fptr* and 0 to
 *receive_fptr_size_to_read* parameter. However you will need to inject the data directly into the
API using the *ai_logging_data_received_callback* function. When this is done you are able to use
functions like *ai_logging_check_for_received_packet(...)* (non blocking function) to check if a 
packet has been received or *ai_logging_wait_for_data(...)* (blocking function) to wait until packet
has been received.

- Extra: when sending/receiving data it is **strongly** recommended to use *ai_logging_clear_packet*
to reset the packet once used and before sending another new one. Unless you know what you are 
doing.


### Building STM32 examples
Due to licensing issues, you need to fetch files to be able to build STM32 examples. Please refer to
 the file *FILE_TO_DOWNLOAD_MANUALLY.md* file located in the stm32_examples folder

### Building C examples
Due to licensing issue, you need to manually fetch the libusb library in order to be able to build AILogging C examples. Here are the steps to follow to build C examples:
- We used libusb version 1.0.23 to build our projects. You can simply download libusb here pointing 
to the right version to be used.
- You have to uncompressed the zipped library and put the folder libusb-1.0.23 next to the Makefile 
to perform the build.
- Be sure you have gcc compiler on your machine
- Run 'make' to build all projects
- Built examples will be placed in 'out' folder

Note: If you want to use a earlier version of the libusb library, be sure to modify the libusb 
version (libusb-1.0.23) used in the Makefile by the new one.


### Using the Python wrapper
- The Python wrapper uses a shared library to get access to the functions provided by the C API. You
 can use the default libraries provided in the Python module or you can build the *host_library* 
 project using the Makefile provided in **host_library** folder. 
- You can use the Python interface to communicate with the STM32 by using the *ai_logging* Python 
modules located in the **python_wrapper** directory. 

Note: the Python wrapper will look for the DLL in the *core* folder of the module, in the current 
working directory and finally in ../host_library/out/


## Usage
*Note: To get detailled documentation on structures, functions,... Do not hesitate to read the 
Doxygen in documentation folder.*
### Python and C usage
You can refer to the various examples located in **c_examples** to have host examples of the API. 
You can also find STM32 examples in **stm32_examples** which work with the c_examples.
Finally you can find Python examples in the **python_wrapper** folder working also with some   stm32_examples.

You can find below an STM32 example (which can easily ported to computer) that is sending data from 
STM32
```c
ai_logging_device_t device;
ai_logging_init(&device);
ai_logging_init_send(&device, usb_cdc_send_function, send_buffer,SEND_BUFFER_MAX_SIZE);

...

ai_logging_buffer data_buffer; // The data
data_buffer.buffer = (uint8_t*)&acc_axes;
data_buffer.size = sizeof(acc_axes);

ai_logging_tensor data_info; // The metadata
ai_logging_shape shape = create_shape_1d(3); // Single dimension array of size 3
data_info.shape = &shape;
data_info.data_type = AI_INT32;

ai_logging_send_data(&device, data_buffer, data_info); // Sending data

```

You can find below a simple example using Python that read continuously data coming from the STM32
```python
from ai_logging import AILoggingAPI
from ai_logging.decoders.decoder import get_decoder_for_data

api = AILoggingAPI('serial', 'COM29', read_size=0)

while True:
    packet = api.wait_for_packet()
    if packet is not None:
        decoder = get_decoder_for_data(packet)
        decoded_data = decoder.decode(packet)
        print("Packet received: {}".format(decoded_data))

```

### GenericUI

GenericUI is a User Interface that makes it easy to interact with your device and perform data 
capture and labelling. The GenericUI application can be found in **generic_ui** directory.

GenericUI allows you to:
- Connect to a Serial or USB communication interface
- Write data to format and send to the STM32 through the chosen communication interface.
- Read the received data that is coming from the STM32 and plot it as text, image, graph.
- Record the received data that is coming from the STM32 and export it as csv, numpy or raw.

#### Requirements / Installation guide
In order to use GenericUI, you will need Python to run this application, thus you will need to `pip install -r requirements.txt` to install the dependencies needed. 
Once completed you can run `make update` to copy the files needed by the application (ai_logging 
modules, DLL) or simply `make` to build the complete Python application into an executable suitable 
for you environment (a complete C build environment is needed to perform this step)

You have also the possibility to start the application directly from python using: 
'*python main.py*' in the application's directory.


## Examples
### Simple live sensor plotting
This example show you how you can perform data transfer from STM32 sensors to data plotting and 
saving on computer side.   

Requirements:
- An STM32 IoTNode board with two USB cables
- The STM32 project **USB_WCID_Accelerometer_Visualization** located in *stm32_examples/Projects/B-L475-IOT01A/Applications/USB_WCID_Accelerometer_Visualization*
- **GenericUI** application (python or executable version)

Steps:
- Plug you IoTNode on your computer using USB cables, one for ST-Link and another for the USB 
transfer link
- Open the STM32 project depending on the IDE you are using
- Build and Flash and Run on STM32. (Your STM32 should be recognized by your computer  as custom USB device)
- Open GenericUI application
- Connect to the STM32 using the *Connection* window and click the USB tab. You need to fill the 
"Port" field with a USB connection string. By default the VID and PID identifier used are : *0x0483*
 and *0x5743*, the underlying driver need to know which endpoint you want to read on. In this 
 project we are using the first endpoint specify at address *0x81*. The connection string is built 
 as follow "VID:PID option1=value1". In our example the connection string to put in the "Port" field
  will be: "0x0483:0x5743 read_endpoint=0x81".
- You can Connect and click on *Add new Plot Widget* on the top bar to display a plotting window 
that should by default plot all 3 axis of the accelerometer.
- You can now try other capabilities like the *Recorder Widget* to record accelerometer data.

### Complete live sensor, array and text plotting
This example is a complete one that will show you how to use the GenericUI application to plot 
multiple type of data depending on their type and shape. In this example accelerometer data will be 
send to computer as well as a simple small "image" of size 5x5x3 and text message indicating the 
number of packet that have been sent.  

Requirements: 
- An STM32 IoTNode board with 2 USB cables
- The STM32 project **USB_CDC_Multiple_Data_Transmission** located in stm32_examples/Projects/B-L475-IOT01A/Applications/USB_CDC_Multiple_Data_Transmission
- **GenericUI** application (python or executable version)

Steps: 
- Plug you IoTNode on your computer using **2 USB cables**, one for ST-Link and another for the USB transfer link
- Open the STM32 project depending on the IDE you are using
- Build and Flash and Run on STM32. (Your STM32 should be recognized by your computer  as custom USB device)
- Open GenericUI application
- Because this is a USB CDC application the Com ports will be used. In the connection window of 
GenericUI, click on "Serial" tab, then choose you COM port (not the ST-Link one) and click "Connect".
- Once you are connected, there is 3 types of data to display: accelerometer values, the image representation and textual data.
- To plot the accelerometer data, choose "Add new Plot Widget" in the top bar and choose 
"ID:Accelero" in the Filter menu and Apply. This is the ID set on the STM32 side. In this case the 
ID is used to identify the data you want to plot.
- To plot the image data, choose "Add new Image Widget" in the top bar and choose "Dim:3" in the 
filter menu and Apply. There is no ID attached to the image so in this case, we are choosing data of Dimension of 3 that represent our image to make data selection.
- To plot textual data, choose "Add new Text Log Widget" in the top bar and choose 
"Type: AI_COMMAND" in the filter menu and Apply. Textual data are simple messages, AI_COMMAND is a 
data type used in AILogging and GenericUI to indicates that the data can be display as a string.


### Image transfer from computer to STM32
This example show you how you can inject images on STM32 to perform tasks such as neural network validation directly on target. In this example images are displayed on screen of the STM32H747 DISCO Board.   

Requirements:
- An STM32H747 DISCO Board
- The STM32 project **USB_WCID_ImageDisplay** located in stm32_examples/Projects/STM32H747I-DISCO/Applications/USB_WCID_ImageDisplay
- Python script **image_injection_demo.py**, located in python_wrapper/image_injection_demo.py

Steps:
- Plug you STM32H747 DISCO board on your computer using **2 USB cables**, the first one for the 
ST-Link and the second one for the USB transfer link
- Open the STM32 project depending on the IDE you are using
- Build and Flash and Run on STM32. The STM32 should be recognized as a custom device by your 
computer
- Run the Python script **image_injection_demo.py**
    - Be sure you are using a recent version of Python 3
    - Be sure you have dependencies installed you can run `pip install -r requirements.txt` of 
    Python wrapper directory
    - Run the script: `python image_injection_demo.py`
- If no errors occurs you should see the ST logo displayed on the screen of the STM32H747 DISCO 
Board
- Feel free to analyze, try and modify the code to suit your needs !


### Message transmission in both direction
This example shows you have you can transmit message between Host and STM32. 
This example allows you to Turn on and off LED on the board depending on the received command on 
STM32 and send back the status back to a Python example that is acting as a 'control' terminal.

Requirements:
- An STM32 IoTNode board with 2 USB cables
- The STM32 project **USB_CDC_Message_Transmission** located in 
stm32_examples/Projects/B-L475-IOT01A/Applications/USB_CDC_Message_Transmission
- The Python script **message_transmission_terminal.py** located in python_wrapper_message_transmission_terminal.py


Steps: 
- Plug you IoTNode on your computer using **2 USB cables**, one for ST-Link and another for the USB transfer link
- Open the STM32 project depending on the IDE you are using
- Build and Flash and Run on STM32. (Your STM32 should be recognized by your computer  as custom USB device)
- Run the Python script **message_transmission_terminal.py**
    - Be sure you are using a recent version of Python 3
    - Be sure you have dependencies installed you can run `pip install -r requirements.txt` of 
    Python wrapper directory
    - Run the script: `python message_transmission_terminal.py`
    - The application will ask you the COM port used by your application, enter it and press 
    'Enter'. (You can find it in the Windows Device Manager for example)
    - Now once connected, you can try typing "L1_ON" to turn on the Green LED on the board and 
    "L1_OFF" to turn it off. If the message is not recognized by the board it will send back a 
    message like "Unknow command".
- Feel free to analyze, try and modify the code to suit your needs !


## Version
Current AILogging C library version is: 0.4.2
