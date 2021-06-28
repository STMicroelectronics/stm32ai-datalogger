/** \file
  * @brief AILogging library prototypes.
  * AILogging is used to send and received data between STM32 and Computer in Machine Learning projects.
  * @author Romain LE DONGE
  * @date March 2021
  * @version 0.4.2
  *  
  * Copyright (c) 2020-2021 STMicroelectronics.
  * All rights reserved.
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
*/

#ifndef AI_LOGGING_H
#define AI_LOGGING_H


#ifdef __cplusplus
extern "C" {
#endif

#ifdef USING_AI_LOGGING_DLL
#warning "USING AI LOGGING DLL"
#ifdef BUILDING_AI_LOGGING_DLL
#warning "BUILDING as DLL EXPORT"
#define AI_LOGGING_DLL __declspec(dllexport)
#else
#warning "BUILDING as DLL IMPORT"
#define AI_LOGGING_DLL __declspec(dllimport)
#endif
#else
//#warning "BUILDING without DLL"
#define AI_LOGGING_DLL
#endif

#include "stdint.h"


#ifndef AI_LOGGING_MAX_N_SHAPES 
#define AI_LOGGING_MAX_N_SHAPES 8
#endif

// Constants
#define AI_LOGGING_START_BYTE (uint8_t)0xFE 
#define AI_LOGGING_END_BYTE (uint8_t)0xFF
#define AI_LOGGING_PACKET_TYPE_V1 (uint8_t)0x01
#define AI_LOGGING_PACKET_TYPE_V2 (uint8_t)0x02

// Pre-computed sizes of fixed part of different payloads
#define AI_LOGGING_PAYLOAD_DATA_FIXED_SIZE 5 // 1 byte type + 4 bytes size
#define AI_LOGGING_PAYLOAD_COMMAND_FIXED_SIZE 2 // 1 byte type + 1 byte size
#define AI_LOGGING_PAYLOAD_SHAPE_FIXED_SIZE 3 // 1 byte type + 2 bytes size

typedef struct {
  uint8_t *send_buffer;
  uint32_t send_buffer_max_size;
  uint32_t send_buffer_position;
  uint8_t send_all_buffer; // Send the entire send buffer each time (can be useful in USB usecase), Warning send buffer size must be large enough to fit header + user data
  
  uint8_t *receive_buffer; // Reception buffer defined by user
  uint32_t receive_buffer_position;
  uint32_t receive_buffer_read_from;
  uint32_t receive_buffer_max_size; // Maximum size of reception buffer
  uint32_t receive_fptr_size_to_read; // Size to read when calling for user's receive_fptr
  
  uint32_t (*send_fptr)(uint8_t *data_ptr, uint32_t data_size); // Pointer to user's send function
  uint32_t (*receive_fptr)(uint8_t *data_ptr, uint32_t data_size); // Pointer to user's receive function

  int32_t copy_next_byte_in_user_buffer; // Handle type V2 packets
  uint8_t *user_raw_buffer; // Pointer to user's defined buffer
  uint32_t user_buffer_position;


  // New functions to manage custom user's workspace to call with each send and receive function
  void *send_function_ctx;
  void *receive_function_ctx;
  uint32_t (*send_ctx_fptr)(void *ctx, uint8_t *data_ptr, uint32_t data_size);
  uint32_t (*receive_ctx_fptr)(void *ctx, uint8_t *data_ptr, uint32_t data_size);

  void (*error_callback)();

  uint8_t enable_auto_prepare_next_packet;

} ai_logging_device_t;


typedef enum {
  AI_RET_OK = (int8_t) 0,
  AI_PACKET_OK = (int8_t)1,
  AI_PACKET_ERROR = (int8_t) -3,
  AI_NOT_ENOUGH_DATA_READ = (int8_t)-4,
  AI_NO_END_BYTE_FOUND = (int8_t)-5,
  AI_COMMAND_ERROR = (int8_t)-6,
  AI_SHAPE_ERROR = (int8_t)-7,
  AI_CUSTOM_PAYLOAD_ERROR = (int8_t)-9,
  AI_CONFIG_ERROR = (int8_t)-10,
  AI_PACKET_ERROR_NO_PAYLOAD_TYPE = (int8_t) -11,
  AI_PACKET_ERROR_NO_LENGTH = (int8_t) -12,
  AI_NO_START_BYTE_FOUND = (int8_t) -13

} ai_logging_error;

typedef enum {//This has to be aligned with Python constants
  // "System constants"
  AI_NONE = (uint8_t)0x00,
  AI_COMMAND=(uint8_t)0x01,
  AI_SHAPE=(uint8_t)0x02,
  AI_TIMESTAMP=(uint8_t)0x03,

  // Data type constants
  AI_INT16=(uint8_t)0x5,
  AI_UINT16=(uint8_t)0x6,
  AI_INT32=(uint8_t) 0x7,
  AI_UINT32=(uint8_t) 0x8,
  AI_STR=(uint8_t)0x9,
  AI_INT8=(uint8_t)0xA,
  AI_UINT8=(uint8_t)0xB,
  AI_FLOAT=(uint8_t)0xC // This is an example of a Custom data type that can be defined by user
} ai_logging_payload_type;


typedef struct {
  uint16_t n_shape;
  uint16_t shapes[AI_LOGGING_MAX_N_SHAPES];
} ai_logging_shape;

typedef struct {
  uint32_t packet_size;
  ai_logging_payload_type payload_type;
  uint8_t *payload;
  uint32_t payload_size;

  ai_logging_shape shape;
  
  uint8_t *message;
  uint8_t message_size;

  int32_t timestamp;

} ai_logging_packet_t;

typedef struct {
  uint32_t size;
  uint8_t *buffer;
} ai_logging_buffer;

typedef struct {
  uint8_t size;
  uint8_t *buffer;
} ai_logging_message;

typedef struct {
  ai_logging_payload_type data_type;
  ai_logging_shape *shape;
} ai_logging_tensor;


/**
 * Initialize ai_logging_device_t instances with default (resetted) values
 * 
 * @param device a pointer to an ai_logging_device_t structure
 */
void AI_LOGGING_DLL ai_logging_init(ai_logging_device_t *device);

/**
 * Initializer to be used after the first initialize function to initialize the send capability 
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param send_fptr a pointer to a function that will be used to send data through the communication interface. 
 * Prototype of the function must respect the required prototype.
 * @param send_buffer a byte buffer that will be used by the API to store data before they are sent. The buffer 
 * size should be greater than the size of the packet's header you want to send. Data itself will be send separatly
 *  if buffer is too small .
 * @param send_buffer_max_size the maximum size of the send_buffer buffer.
 */
void AI_LOGGING_DLL ai_logging_init_send(ai_logging_device_t *device, uint32_t (*send_fptr)(uint8_t *data_ptr, uint32_t data_size), uint8_t *send_buffer, uint32_t send_buffer_max_size);

/**
 * Initializer to be used after the first initialize function to initialize the send capability that is supporting custom user context pointer.
 * The context will be passed to the send and receive function when user wants to send or receive packets
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param send_ctx_fptr a pointer to a function that will be used to send data through the communication interface. The context
 * of the user is added to this function to be able retrive data when send function is called
 * @param ctx the context to be used when calling the send function. Can be anything the user wants to have when the send function is called
 * @param send_buffer a byte buffer that will be used by the API to store data before they are sent. The buffer 
 * size should be greater than the size of the packet's header you want to send. Data itself will be send separatly
 * if buffer is too small .
 * @param send_buffer_max_size the maximum size of the send_buffer buffer.
 */
void AI_LOGGING_DLL ai_logging_init_send_ctx(ai_logging_device_t *device, uint32_t (*send_ctx_fptr)(void *ctx, uint8_t *data_ptr, uint32_t data_size), void *ctx, uint8_t *send_buffer, uint32_t send_buffer_max_size);

/**
 * Initializer to be used after the first initialize function to initialize the receive capability. This is used when user want to do 
 * synchronous API calls like ai_logging_wait_for_data that will try to read data from the user read function.
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param receive_fptr a pointer to a function that will be used to receive data. This is used when calling the blocking API like the
 * ai_logging_wait_for_data function. If you are not using blocking API, you can pass NULL to this parameter.
 * @param receive_fptr_size_to_read if receive_fptr is used, this parameter indicates the size that will be used to call the receive_fpt function.
 * @param receive_buffer the buffer that will be used internally to store and parse received data to decode packets. This buffer should be as big
 * as the maximum data you want to receive + header size (usually 11 bytes are sufficient).
 * @param receive_buffer_max_size the size of the receive_buffer
 */
void AI_LOGGING_DLL ai_logging_init_receive(ai_logging_device_t *device, uint32_t (*receive_fptr)(uint8_t *data_ptr, uint32_t data_size), uint32_t receive_fptr_size_to_read, uint8_t *receive_buffer, uint32_t receive_buffer_max_size);

/**
 * Initializer to be used after the first initialize function to initialize the receive capability. This is used when user want to do 
 * synchronous API calls like ai_logging_wait_for_data that will try to read data from the user read function.
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param receive_ctx_fptr a pointer to a function that will be used to receive data. This is used when calling the blocking API like the
 * ai_logging_wait_for_data function. If you are not using blocking API, you can pass NULL to this parameter. The function prototype should 
 * also have the ctx parameter which is the context the user want to use. 
 * @param ctx the context to be used when calling the receive function. Can be anything the user wants to have when the receive function is called
 * @param receive_fptr_size_to_read if receive_fptr is used, this parameter indicates the size that will be used to call the receive_fpt function.
 * @param receive_buffer the buffer that will be used internally to store and parse received data to decode packets. This buffer should be as big
 * as the maximum data you want to receive + header size (usually 11 bytes are sufficient).
 * @param receive_buffer_max_size the size of the receive_buffer
 */
void AI_LOGGING_DLL ai_logging_init_receive_ctx(ai_logging_device_t *device, uint32_t (*receive_ctx_fptr)(void *ctx, uint8_t *data_ptr, uint32_t data_size), void *ctx, uint32_t receive_fptr_size_to_read, uint8_t *receive_buffer, uint32_t receive_buffer_max_size);

/**
 * Initializer to be used after the first initialize function to initialize the low level reception capabilities.
 * This is used to receive "raw" data without using the standard packet formatting (packet corruption checks are also disabled)
 * Thanks to this function the receive data will directly be put at the address you specify.
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param user_raw_buffer a pointer to the buffer where you want to receive the data. The buffer size should be large enough. No check are 
 * performed when receiving data which can result in memory corruption. 
 */
void AI_LOGGING_DLL ai_logging_init_raw_data_buffer(ai_logging_device_t *device, uint8_t *user_raw_buffer);

/**
 * Send a simple data buffer with its associated ai_logging_tensor specified which includes shape and type
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param data an ai_logging_buffer structure which includes the buffer and its size
 * @param data_info an ai_logging_tensor structure which includes the data type and the data shape
 */
void AI_LOGGING_DLL ai_logging_send_data(ai_logging_device_t *device, ai_logging_buffer data, ai_logging_tensor data_info);

/**
 * Send a simple message (maximum 255 bytes) 
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param message an ai_logging_message containing the message and its length
 */
void AI_LOGGING_DLL ai_logging_send_message(ai_logging_device_t *device, ai_logging_message message);

/**
 * Send a message next to data. Message can be used to identify data (string description, channel,...) and transmitted in one packet. 
 * This will be received as a single packet with message and data.
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param message an ai_logging_message containing the message and its length
 * @param data an ai_logging_buffer structure which includes the buffer and its size
 * @param data_info an ai_logging_tensor structure which includes the data type and the data shape
 */
void AI_LOGGING_DLL ai_logging_send_message_with_data(ai_logging_device_t *device, ai_logging_message message, ai_logging_buffer data, ai_logging_tensor data_info);

/**
 * Useful function that put data into library internal buffers. If user manage himself the data reception, this function should be used to add
 * data into internal buffers. If not using blocking API (ai_logging_wait_for_data), you should use this function. If you use a reception loop
 * and ai_logging_check_for_received_packet, you should use this function. If you are receiving your data through interrupt, you should also
 * you this function.
 * An internal copy of the received data will be done except if using raw api.
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param data_ptr a pointer to the received data to should be put into the internal buffers
 * @param data_size the size of the received data
 */
void AI_LOGGING_DLL ai_logging_data_received_callback(ai_logging_device_t *device, uint8_t *data_ptr, uint32_t data_size);

/**
 * This function is used to check if a packet has been received. A return value > 0 indicates that a packet is present, other values 
 * can indicates an error that you can check using the ai_logging_error enum. If receiving standard packet sent through the standard 
 * API, the data received will be located into the library internal buffer, otherwise if using the raw API, the received data will 
 * be available into the user reception buffer.
 * 
 * @param device a pointer to an ai_logging_device_t stucture
 * @param packet a pointer to an ai_logging_packet_t structure that will hold the data received. Values are set only if packet is found.
 * @return return the status of the search. ret > 0 indicates that a packet has been found, ret = 0 indicates no packet, ret < 0 indicates an error
 * has been detected. The error can be critical or not. Check the ai_logging_error enum to get more info on errors.
 */
int AI_LOGGING_DLL ai_logging_check_for_received_packet(ai_logging_device_t *device, ai_logging_packet_t *packet);

/**
 * This function will wait until a packet is received and will try to read new data thanks to the receive_function (the associated init should be done)
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param packet a pointer to an ai_logging_packet_t structure that will hold the data received.
 * @return will return the same output as ai_logging_check_for_received_packet.
 */
int AI_LOGGING_DLL ai_logging_wait_for_data(ai_logging_device_t *device, ai_logging_packet_t *packet);

/**
 * This function prepare the internal library states to receive a new packet, this function should be called when you no longer need to use the 
 * received data. This function should be called before receiving new packets, otherwise buffer overflow could occurs.
 * @param device a pointer to an ai_logging_device_t structure
 */
void AI_LOGGING_DLL ai_logging_prepare_next_packet(ai_logging_device_t *device);

/**
 * This function is part of the new API that is able to send directly ai_logging_packet_t data. User has to set the data/message/shape/type/... 
 * directly in the structure fields and then call ai_logging_send_packet to send the data.
 * 
 * @param device a pointerto an ai_logging_device_t structure
 * @param packet a pointer to the packet to be sent with the fiels set. 
 */
void AI_LOGGING_DLL ai_logging_send_packet(ai_logging_device_t *device, ai_logging_packet_t* packet);

/**
 * This function is used to reset/initialize a packet with a default state. This should be used in first phase to initialize ai_logging_packet_t fields.
 * Then it can be used when calling ai_logging_prepare_next_packet to be sure the fields are resetting into the structure.
 * 
 * @param packet a pointer to the ai_logging_packet_t  
 */
void AI_LOGGING_DLL ai_logging_clear_packet(ai_logging_packet_t *packet);

/**
 * This function with ai_logging_send_raw_data is used to send raw data without packet control when receiving. The data type and size
 * must be sent at the beginning with ai_logging_send_header_for_raw_data, then data are sent with ai_logging_send_raw_data. The advantage 
 * is that you can send your data piece by piece. You have a low level control on the data. On the reception side, you can directly put the
 * received data into a user buffer (received by the same function as standard packets).
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param data_type a byte, from 0x00 to 0xC for known types (see ai_logging_payload_type enum) and greater than 0xC for custom data types
 * @param total_data_length the total length of the data you will send
 */
void AI_LOGGING_DLL ai_logging_send_header_for_raw_data(ai_logging_device_t *device, uint8_t data_type, uint32_t total_data_length);


/**
 * This function with ai_logging_send_header_for_raw_data is used to send raw data without packet control when receiving.
 * You can call this function as many times as you want to send the data of size total_data_length you specified when calling 
 * ai_logging_send_header_for_raw_data. On the reception side, you can directly put the received data into a user buffer (received by the
 * same function as standard packets).
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param buffer a buffer of data to send
 * @param buffer_length the size of the buffer you want to send
 */
void AI_LOGGING_DLL ai_logging_send_raw_data(ai_logging_device_t *device, uint8_t *buffer, uint32_t buffer_length);

/**
 * This function can be called when transmission problem occurs. If either the data are not sent due to lack of data (waiting data to be filled 
 * into buffer), or data are not received due to blocking API  (waiting for N bytes to read and unblock). You can call this function to 
 * send garbage data to force data transfer.
 * 
 * @param device a pointer to an ai_logging_device_t structure
 * @param size the size of the garbage data you want to send
 */
void AI_LOGGING_DLL ai_logging_purge(ai_logging_device_t *device, uint32_t size);

/// @private this function put the header of a raw packet at the specified buffer
int _ai_logging_prepare_raw_header_in_buffer(uint8_t *buffer, uint8_t data_type, uint32_t total_data_length);


// AI_Logging Helpers
/// @private 
int32_t ai_logging_find_start_byte(ai_logging_device_t *device, uint32_t from);
/// @private
uint8_t ai_logging_is_there_packet_type_v1(ai_logging_device_t *device, uint32_t at);
/// @private
uint8_t ai_logging_is_there_packet_type_v2(ai_logging_device_t *device, uint32_t at);
/// @private
int ai_logging_decode_v1_packet(ai_logging_device_t *device, ai_logging_packet_t *packet, int32_t start_byte_index);
/// @private
int ai_logging_decode_v2_packet(ai_logging_device_t *device, ai_logging_packet_t *packet, int32_t start_byte_index);
/// @private
void add_data_to_buffer(ai_logging_device_t *device, uint8_t *data_ptr, uint16_t size);
/// @private
uint32_t read_uint32_from_buffer(uint8_t *buffer, uint32_t shift, uint32_t *data_out);
/// @private
int32_t read_int32_from_buffer(uint8_t *buffer, uint32_t shift, int32_t *data_out);
/// @private
uint32_t read_uint16_from_buffer(uint8_t *buffer, uint32_t shift, uint16_t *data_out);
/// @private
uint32_t read_uint8_from_buffer(uint8_t *buffer, uint32_t shift, uint8_t *data_out);

/// @private
void _ai_logging_fire_error(ai_logging_device_t * device);

/// @private
void _ai_logging_call_send_fptr(ai_logging_device_t *device, uint8_t *data_ptr, uint32_t data_size);


// External Helpers
/**
 * Helpers function that helps you to fill your shape data into ai_logging_shape.
 */
/// @{
void AI_LOGGING_DLL ai_logging_create_shape_0d(ai_logging_shape *shape);
void AI_LOGGING_DLL ai_logging_create_shape_1d(ai_logging_shape *shape, uint16_t dim_x);
void AI_LOGGING_DLL ai_logging_create_shape_2d(ai_logging_shape *shape, uint16_t dim_x, uint16_t dim_y);
void AI_LOGGING_DLL ai_logging_create_shape_3d(ai_logging_shape *shape, uint16_t dim_x, uint16_t dim_y, uint16_t dim_z);
/// @}

/**
 * Helper function creating an ai_logging_message structure from the parameters specified.
 * You can use this function to help you create needed structure for ai_logging_send_message_with_data function for example.
 * 
 * @param message the message buffer you want to send
 * @param message_size the site of the message you want to send (up to 255 byte)
 * @return return a structure initialized with the message and message_size specified
 */
ai_logging_message create_message(uint8_t *message, uint8_t message_size);

/**
 * Helper function creating an ai_logging_buffer structure from the parameters specified.
 * You can use this function to help you create needed structure for ai_logging_send_message_with_data function for example.
 * 
 * @param buffer the buffer you wantm to use
 * @param buffer_size the buffer size you want to use
 * @return return a structure initialized with the buffer and buffer_size specified
 */
ai_logging_buffer create_buffer(uint8_t *buffer, uint32_t buffer_size);


#ifdef __cplusplus
}
#endif

#endif
