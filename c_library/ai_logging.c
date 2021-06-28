/**
  ******************************************************************************
  * @file           : ai_logging.c
  * @brief          : AILogging C implementation 
  ******************************************************************************
  * Copyright (c) 2020-2021 STMicroelectronics.
  * All rights reserved.
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

#ifdef __cplusplus
extern "C" {
#endif

#include <string.h>
#include "ai_logging.h"


void ai_logging_init(ai_logging_device_t *device)
{
  device->send_fptr = NULL;
  device->send_buffer_position = 0;
  device->send_buffer = NULL;
  device->send_buffer_max_size = 0;
  device->send_all_buffer = 0;

  device->receive_fptr = NULL;
  device->receive_buffer = NULL;
  device->receive_buffer_max_size = 0;
  device->receive_buffer_position = 0;
  device->receive_buffer_read_from = 0;
  device->receive_fptr_size_to_read = 0;
  
  device->copy_next_byte_in_user_buffer = -1;
  device->user_raw_buffer = NULL;
  device->user_buffer_position = 0;

  device->send_function_ctx = NULL;
  device->receive_function_ctx = NULL;
  device->send_ctx_fptr = NULL;
  device->receive_ctx_fptr = NULL;

  device->error_callback = NULL;

  device->enable_auto_prepare_next_packet = 1; // If 0: disabled, if > 0: enabled => 1:enabled/default, 2:packet_received (set by reception function)
}

void ai_logging_init_send(ai_logging_device_t *device, uint32_t (*send_fptr)(uint8_t *data_ptr, uint32_t data_size), uint8_t *send_buffer, uint32_t send_buffer_max_size)
{
  device->send_fptr = send_fptr;
  device->send_buffer = send_buffer;
  device->send_buffer_max_size = send_buffer_max_size;
}

void AI_LOGGING_DLL ai_logging_init_send_ctx(ai_logging_device_t *device, uint32_t (*send_ctx_fptr)(void *ctx, uint8_t *data_ptr, uint32_t data_size), void *ctx, uint8_t *send_buffer, uint32_t send_buffer_max_size)
{
  device->send_ctx_fptr = send_ctx_fptr;
  device->send_function_ctx = ctx;
  device->send_buffer = send_buffer;
  device->send_buffer_max_size = send_buffer_max_size;
}

void ai_logging_init_receive(ai_logging_device_t *device, uint32_t (*receive_fptr)(uint8_t *data_ptr, uint32_t data_size), uint32_t receive_fptr_size_to_read, uint8_t *receive_buffer, uint32_t receive_buffer_max_size)
{
  device->receive_fptr = receive_fptr;
  device->receive_fptr_size_to_read = receive_fptr_size_to_read;
  device->receive_buffer = receive_buffer;
  device->receive_buffer_max_size = receive_buffer_max_size;
}

void AI_LOGGING_DLL ai_logging_init_receive_ctx(ai_logging_device_t *device, uint32_t (*receive_ctx_fptr)(void *ctx, uint8_t *data_ptr, uint32_t data_size), void *ctx, uint32_t receive_fptr_size_to_read, uint8_t *receive_buffer, uint32_t receive_buffer_max_size)
{
  device->receive_ctx_fptr = receive_ctx_fptr;
  device->receive_function_ctx = ctx;
  device->receive_fptr_size_to_read = receive_fptr_size_to_read;
  device->receive_buffer = receive_buffer;
  device->receive_buffer_max_size = receive_buffer_max_size;
}

void ai_logging_init_raw_data_buffer(ai_logging_device_t *device, uint8_t *user_raw_buffer)
{
  device->user_raw_buffer = user_raw_buffer;
}

void ai_logging_send_data(ai_logging_device_t *device, ai_logging_buffer data, ai_logging_tensor data_info)
{
  ai_logging_message msg = create_message(NULL,0); // TODO: To improve to avoid creating this in this function
  ai_logging_send_message_with_data(device, msg, data, data_info);
}

void AI_LOGGING_DLL ai_logging_send_message(ai_logging_device_t *device, ai_logging_message message)
{
  ai_logging_buffer data = create_buffer(NULL, 0);
  ai_logging_tensor data_info;
  data_info.data_type = AI_NONE;
  ai_logging_shape s;
  s.n_shape = 0;
  data_info.shape = &s;
  ai_logging_send_message_with_data(device, message, data, data_info);
}

void AI_LOGGING_DLL ai_logging_send_message_with_data(ai_logging_device_t *device, ai_logging_message message, ai_logging_buffer data, ai_logging_tensor data_info)
{
  uint32_t message_data_size = 0;
  if(message.size != 0){ // If we have a message
    message_data_size = AI_LOGGING_PAYLOAD_COMMAND_FIXED_SIZE + message.size;
  }

  uint16_t payload_shape_data_size = 0;
  uint32_t payload_shape_size = 0;
  if(data_info.shape->n_shape != 0){// If shape is not 0
    payload_shape_data_size = sizeof(uint16_t)*(data_info.shape->n_shape);
    payload_shape_size = AI_LOGGING_PAYLOAD_SHAPE_FIXED_SIZE + payload_shape_data_size;
  }
  
  uint32_t payload_data_size = 0;
  if(data.size != 0){ // If data_size is not 0
    payload_data_size = AI_LOGGING_PAYLOAD_DATA_FIXED_SIZE + data.size;
  }
  uint32_t total_payload_size = message_data_size + payload_shape_size + payload_data_size; 
  
  int8_t packet_have_been_sent = 0;
  uint8_t temp[1];
  temp[0] = AI_LOGGING_START_BYTE;
  add_data_to_buffer(device, temp, sizeof(uint8_t));
  temp[0] = AI_LOGGING_PACKET_TYPE_V1;
  add_data_to_buffer(device, temp, sizeof(uint8_t));
  add_data_to_buffer(device, (uint8_t*)&total_payload_size, sizeof(uint32_t));
  

  if(message.size != 0){
    temp[0] = AI_COMMAND;
    add_data_to_buffer(device, temp, sizeof(uint8_t));

    add_data_to_buffer(device, (uint8_t*)&message.size, sizeof(uint8_t)); // Size of command
    
    if(message.size + device->send_buffer_position > device->send_buffer_max_size)
    {
      while(1); // Error internal buffer must be at least 255 + 7 byte (Max uint8 + header size)
      //Improvement we can manage this case
    }
    else
    {
      add_data_to_buffer(device, message.buffer,message.size); // Sending command
    }
  }


  if(data_info.shape->n_shape != 0){ // If shape is not 0
    temp[0] = AI_SHAPE;
    add_data_to_buffer(device, temp, sizeof(uint8_t));
    add_data_to_buffer(device, (uint8_t*)&payload_shape_data_size, sizeof(payload_shape_data_size));
    int i = 0;
    for(i = 0; i < data_info.shape->n_shape; i++)
    {
      add_data_to_buffer(device, (uint8_t*)&(data_info.shape->shapes[i]), sizeof(uint16_t));  
    }
  }
  
  
  if(data.size != 0){ // If data_size is not 0
    add_data_to_buffer(device, (uint8_t*)&(data_info.data_type), sizeof(uint8_t));
    add_data_to_buffer(device, (uint8_t*)&(data.size), sizeof(uint32_t));

    if(data.size + device->send_buffer_position > device->send_buffer_max_size) // Decide weather to perform copy to buffer or not
    {
      // if(device->send_fptr != NULL) {
      //   device->send_fptr(device->send_buffer, device->send_buffer_position);
      // } else {
      //   _ai_logging_fire_error(device);
      // }
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);

      device->send_buffer_position = 0;
      
      // if(device->send_fptr != NULL){
      //   device->send_fptr(data.buffer, data.size);
      // } else {
      //   _ai_logging_fire_error(device);
      // }
      _ai_logging_call_send_fptr(device, data.buffer, data.size);
      
      packet_have_been_sent = 1;
    }
    else
    {
      add_data_to_buffer(device, data.buffer, data.size);
    }
  }
  
  if(packet_have_been_sent == 0){ // Either close packet with AI_LOGGING_END_BYTE or send + close packet
    temp[0] = AI_LOGGING_END_BYTE;
    add_data_to_buffer(device, temp, sizeof(uint8_t));
    if(device->send_all_buffer == 0x01)
    {
      // if(device->send_fptr != NULL) {
      //   device->send_fptr(device->send_buffer, device->send_buffer_max_size); // Sending the entire buffer
      // } else {
      //   _ai_logging_fire_error(device);
      // }
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_max_size);
    }
    else
    {
      // if(device->send_fptr != NULL) {
      //   device->send_fptr(device->send_buffer, device->send_buffer_position); // Sending just packets
      // } else {
      //   _ai_logging_fire_error(device);
      // }
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);
    }
    device->send_buffer_position = 0;    
  } else {
    temp[0] = AI_LOGGING_END_BYTE;
    add_data_to_buffer(device, temp, sizeof(uint8_t));

    // if(device->send_fptr != NULL){
    //   device->send_fptr(device->send_buffer, device->send_buffer_position);
    // } else {
    //   _ai_logging_fire_error(device);
    // }
    _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);

    device->send_buffer_position = 0;
  }
}

int _ai_logging_prepare_raw_header_in_buffer(uint8_t *buffer, uint8_t data_type, uint32_t total_data_length)
{
  buffer[0] = AI_LOGGING_START_BYTE;
  buffer[1] = AI_LOGGING_PACKET_TYPE_V2;
  uint32_t total_length = sizeof(data_type) + total_data_length;
  *(uint32_t*)&buffer[2] = total_length;
  buffer[6] = data_type;
  *(uint32_t*)&buffer[7] = total_data_length;
  return 11;
}

void ai_logging_send_header_for_raw_data(ai_logging_device_t *device, uint8_t data_type, uint32_t total_data_length)
{
  /*
    Structure: SB(1)+PacketTypeV2(1)+PacketLength(4)+PayloadType(1)+PayloadLength(4) = 11 bytes
  */
  device->send_buffer_position = 0;

  uint8_t temp[1];
  temp[0] = AI_LOGGING_START_BYTE;
  add_data_to_buffer(device, temp, sizeof(AI_LOGGING_START_BYTE));

  temp[0] = AI_LOGGING_PACKET_TYPE_V2;
  add_data_to_buffer(device, temp, sizeof(AI_LOGGING_PACKET_TYPE_V2));

  uint32_t total_length = sizeof(data_type) + total_data_length;
  add_data_to_buffer(device, (uint8_t*)&total_length, sizeof(total_length));

  temp[0] = data_type;
  add_data_to_buffer(device, &data_type, sizeof(data_type));

  add_data_to_buffer(device, (uint8_t*)&total_data_length, sizeof(total_data_length));
  
  _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);
  device->send_buffer_position = 0;
}

void ai_logging_send_raw_data(ai_logging_device_t *device, uint8_t *buffer, uint32_t buffer_length)
{
  _ai_logging_call_send_fptr(device, buffer, buffer_length);
}
/*
 Purge: allow to send "0" data to fill the reception buffer on the other side
*/
void ai_logging_purge(ai_logging_device_t *device, uint32_t size)
{
  uint32_t bytes_left_to_send = size;
  device->send_buffer_position = 0;
  uint8_t data = 0x00;
  
  while(bytes_left_to_send > 0)
  {
    if(bytes_left_to_send > device->send_buffer_max_size)
    {
      for(int i = 0; i < device->send_buffer_max_size; i++)
      {
        add_data_to_buffer(device, &data, sizeof(data));
      }
      // if(device->send_fptr != NULL) {
      //   device->send_fptr(device->send_buffer, device->send_buffer_position);
      // } else {
      //   _ai_logging_fire_error(device);
      // }
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);
      
      device->send_buffer_position = 0;
      bytes_left_to_send -= device->send_buffer_max_size;
    }
    else
    {
      for(int i = 0; i < bytes_left_to_send; i++)
      {
        add_data_to_buffer(device, &data, sizeof(data));
      }
      // if(device->send_fptr != NULL) {
      //   device->send_fptr(device->send_buffer, device->send_buffer_position);
      // } else {
      //   _ai_logging_fire_error(device);
      // }
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);
      
      device->send_buffer_position = 0;
      bytes_left_to_send = 0;
    }
    
  }
  device->send_buffer_position = 0;
}

void ai_logging_data_received_callback(ai_logging_device_t *device, uint8_t *data_ptr, uint32_t data_size)
{
  if(device->copy_next_byte_in_user_buffer > 0)
  {
    if(data_size < (uint32_t)device->copy_next_byte_in_user_buffer)
    {
      memcpy(device->user_raw_buffer+device->user_buffer_position, data_ptr, data_size);
      device->copy_next_byte_in_user_buffer -= data_size;
      device->user_buffer_position += data_size;
    }
    else
    {
      memcpy(device->user_raw_buffer+device->user_buffer_position, data_ptr, device->copy_next_byte_in_user_buffer);
      uint32_t bytes_left_to_copy = data_size - device->copy_next_byte_in_user_buffer;
      
      if(device->receive_buffer_position + bytes_left_to_copy > device->receive_buffer_max_size)
      {
        device->receive_buffer_read_from = 0;// In this case we reset position because old data will be overriden
        device->receive_buffer_position = 0;
      }
      memcpy(device->receive_buffer+device->receive_buffer_position, data_ptr+device->copy_next_byte_in_user_buffer, bytes_left_to_copy);
      device->receive_buffer_position += bytes_left_to_copy;
      device->user_buffer_position += device->copy_next_byte_in_user_buffer;
      device->copy_next_byte_in_user_buffer = 0;
    }
  }
  else
  {
    if(device->receive_buffer_position + data_size > device->receive_buffer_max_size)
    {
      device->receive_buffer_read_from = 0;// In this case we reset position because old data will be overriden
      device->receive_buffer_position = 0;
    }
    memcpy(device->receive_buffer+device->receive_buffer_position, data_ptr, data_size);
    device->receive_buffer_position += data_size;
  }
}


int ai_logging_wait_for_data(ai_logging_device_t *device, ai_logging_packet_t *packet)
{
  if(device->receive_fptr == NULL){
    if(device->receive_ctx_fptr == NULL){
      return -1;
    }
  }
  
  int ret = -1;
  while(ret < 0)
  {

    if(device->receive_buffer_position + device->receive_fptr_size_to_read > device->receive_buffer_max_size)
    {
      device->receive_buffer_read_from = 0; // In this case we reset position because old data will be overriden
      device->receive_buffer_position = 0; // We can eventually trigger an error here
    }
    
    if(device->receive_fptr != NULL){
      uint32_t transferred = device->receive_fptr(device->receive_buffer+device->receive_buffer_position, device->receive_fptr_size_to_read);
      device->receive_buffer_position += transferred;
    } else if(device->receive_ctx_fptr != NULL){
      uint32_t transferred = device->receive_ctx_fptr(device->receive_function_ctx, device->receive_buffer+device->receive_buffer_position, device->receive_fptr_size_to_read);
      device->receive_buffer_position += transferred;
    } else {
      _ai_logging_fire_error(device); // We should not go in there
    }
    
    ret = ai_logging_check_for_received_packet(device, packet);
  }
  return ret;
}


int ai_logging_check_for_received_packet(ai_logging_device_t *device, ai_logging_packet_t *packet)
{

  if(device->enable_auto_prepare_next_packet == 2) // Auto prepare next packet if enabled
  {
    ai_logging_prepare_next_packet(device);
    device->enable_auto_prepare_next_packet = 1;
  }

  while(device->receive_buffer_read_from <= device->receive_buffer_position){
    // if(device->receive_buffer_read_from == 1)
    // {
    //   device->receive_buffer_read_from = 0;
    // }
    if(device->receive_buffer_read_from == device->receive_buffer_position){
      return AI_NOT_ENOUGH_DATA_READ;
    }

    int32_t start_byte_index = ai_logging_find_start_byte(device, device->receive_buffer_read_from);
  
    if(start_byte_index < 0){
      return AI_NO_START_BYTE_FOUND;
    }

    if(device->receive_buffer_position - start_byte_index < 6){
      return AI_NOT_ENOUGH_DATA_READ; // Not enough byte to read header: we wait next round
    }

    if(ai_logging_is_there_packet_type_v1(device, start_byte_index + 1))
    {
      int ret = ai_logging_decode_v1_packet(device, packet, start_byte_index);
      
      if(ret > 0 && device->enable_auto_prepare_next_packet == 1)
      {
        device->enable_auto_prepare_next_packet = 2;
      }

      if(ret == AI_NO_END_BYTE_FOUND)
      {
        // This is not a condition to stop seeking for packet
      }
      else
      {
        return ret;
      }
      
    }
    else if(device->user_raw_buffer != NULL && ai_logging_is_there_packet_type_v2(device, start_byte_index + 1))
    {
      int ret = ai_logging_decode_v2_packet(device, packet, start_byte_index);

      if(ret > 0 && device->enable_auto_prepare_next_packet == 1)
      {
        device->enable_auto_prepare_next_packet = 2;
      }
      
      return ret;
    }
    else
    {
      device->receive_buffer_read_from = start_byte_index + 1; // We update because this is not a start of a packet
      //return -2; // We should do a retry here
    }
  }
  return 0;
}

int ai_logging_decode_v1_packet(ai_logging_device_t *device, ai_logging_packet_t *packet, int32_t start_byte_index)
{
  uint32_t current_index = start_byte_index + 1 + 1; //Placing after Start byte + packet type byte
  uint32_t packet_length = 0;
  current_index = read_uint32_from_buffer(device->receive_buffer, current_index, &packet_length);
  if(packet_length == 0){
      //Here we have a correct packet
    packet->packet_size = packet_length;
    packet->payload = NULL;
    packet->payload_size = 0;
    packet->payload_type = AI_NONE;
    packet->shape.n_shape = 0;
    packet->message = NULL;
    packet->message_size = 0;
    packet->timestamp = -1;
    device->receive_buffer_read_from = current_index;
    return AI_PACKET_OK; // No packet of size 0 : strange
  }
  if(device->receive_buffer_position < start_byte_index + packet_length + 1 + 4 + 1 + 1) {
    // StartByte(1) + PacketType(1) + PacketSize(4) + [PAYLOAD] + EndByte(1)
    // We haven't read enough data: we wait for next round
    return AI_NOT_ENOUGH_DATA_READ;
  }

  uint32_t end_byte_index = (start_byte_index + 1 + 4 +packet_length + 1) % device->receive_buffer_max_size;
  if(device->receive_buffer[end_byte_index] != AI_LOGGING_END_BYTE){
    // EndByteIndex = StartByteIndex + StartByte(1), PacketType(1) + PacketLength(4) + (PacketLength)
    // The start byte does not match with the end byte so: 
    // - this is not a packet or
    // - the packet is currupted
    // in both cases we update the read_from index
    
    device->receive_buffer_read_from = start_byte_index + 1; 
    return AI_NO_END_BYTE_FOUND;
  }

  //Here we have a correct packet
  packet->packet_size = packet_length;
  packet->payload = NULL;
  packet->payload_size = 0;
  packet->payload_type = AI_NONE;
  packet->shape.n_shape = 0;
  packet->message = NULL;
  packet->message_size = 0;
  packet->timestamp = -1;


  // Packet decoding
  uint32_t payloads_start_index = start_byte_index + 1 + 1 + 4;
  for(uint32_t i = payloads_start_index; i < payloads_start_index + packet_length; i++)
  {
    if(device->receive_buffer[i] == AI_COMMAND)
    {
      // Reminder: PayloadType(A byte) + PayloadLength(1 byte) + (PayloadLength)
      uint8_t command_length = 0;
      read_uint8_from_buffer(device->receive_buffer, i+1, &command_length);
      if(command_length == 0){
        device->receive_buffer_read_from = end_byte_index;
        return AI_COMMAND_ERROR; // Two choices: either critical error or wrong packet
      }
      
      //packet->payload_type = AI_COMMAND;
      packet->message_size = command_length;
      packet->message = device->receive_buffer+i+1+1;// Skipping payload type and payload length
      
      // if(packet->payload_type == AI_NONE) // Removed for consistency purpose
      // {
      //   // if only command, payload_type is AI_COMMAND, this may be overriden by non AI_COMMAND data
      //   packet->payload_type = AI_COMMAND; 
      // }
      
      i = i + 1 + 1 + command_length - 1; // /!\ IMPORTANT: Updating the 'i' to skip data to decode new payloads
    }
    else if(device->receive_buffer[i] == AI_TIMESTAMP)
    {
      // Reminder: PayloadType (1 byte) + Timestamp (4 byte)
      int32_t timestamp = -1;
      read_int32_from_buffer(device->receive_buffer, i+1, &timestamp);
      packet->timestamp = timestamp;

      i = i + 1 + 4 - 1;
    }
    else if(device->receive_buffer[i] == AI_SHAPE)
    {
      // Reminder: PayloadType(1 byte) + PayloadLength(2 bytes) + (PayloadLength)
      uint16_t shape_length = 0;
      read_uint16_from_buffer(device->receive_buffer, i + 1, &shape_length);
      if(shape_length == 0){
        device->receive_buffer_read_from = end_byte_index;
        return AI_SHAPE_ERROR;
      }

      uint16_t nb_shape = (int)shape_length/2; // We know that shape data are on 2 bytes each
      packet->shape.n_shape = nb_shape;
      
      if(nb_shape > AI_LOGGING_MAX_N_SHAPES){
        device->receive_buffer_read_from = end_byte_index;
        return AI_SHAPE_ERROR; // Error while reading shapes or error from the user who must increase AI_LOGGING_MAX_N_SHAPES
      }

      for(int k = 0; k<nb_shape; k++)
      {
        uint16_t shape_value = 0;
        read_uint16_from_buffer(device->receive_buffer, i + 1 + 2 + k*2, &shape_value);
        packet->shape.shapes[k] = shape_value;
      }

      i = i + 1 + 2 + shape_length - 1;
    }
    else
    {
      // Reminder: PacketType(1 byte) + PacketLength(4 bytes) + (PacketLength)
      uint32_t data_length = 0;
      read_uint32_from_buffer(device->receive_buffer, i + 1, &data_length);
      if(data_length == 0){
        device->receive_buffer_read_from = end_byte_index;
        return AI_CUSTOM_PAYLOAD_ERROR;
      }
      packet->payload_type = (ai_logging_payload_type)device->receive_buffer[i];
      packet->payload_size = data_length;
      packet->payload = device->receive_buffer + i + 1 + 4;
      i = i + 1 + 4 + data_length - 1;
    }
  }
  device->receive_buffer_read_from = end_byte_index; // We move to the following packet (if put +1 this crash the DLL)
  return AI_PACKET_OK;
}


int ai_logging_decode_v2_packet(ai_logging_device_t *device, ai_logging_packet_t *packet, int32_t start_byte_index)
{
  /*
   Packet of type v2 assume that user sends payload received in his custom defined buffer
  */

  if(device->user_raw_buffer == NULL){ // This functionnality is not initialized
    return AI_CONFIG_ERROR; 
  }

  uint32_t current_index = start_byte_index + 1 + 1; //Placing after Start byte + packet type byte
  uint32_t packet_length = 0;
  current_index = read_uint32_from_buffer(device->receive_buffer, current_index, &packet_length);
  if(packet_length == 0){
    device->receive_buffer_read_from = current_index; // Error so we move to read next packet
    return AI_PACKET_ERROR;
  }

  uint32_t header_end_position = (uint32_t)start_byte_index + 1 + 1 + 4 + 1 + 4; // Skipping SB(1),PType(1),PLength(4),PayloadType(1),PayloadLength(4)
  if(device->receive_buffer_position < header_end_position) {
    // We haven't read enough data: we wait for next round
    return AI_NOT_ENOUGH_DATA_READ;
  }
  //Assuming we have the complete header

  uint8_t payload_type = 0;
  current_index = read_uint8_from_buffer(device->receive_buffer, current_index, &payload_type);
  if(payload_type == 0){
    return AI_PACKET_ERROR_NO_PAYLOAD_TYPE;
  }

  uint32_t payload_length = 0;
  current_index = read_uint32_from_buffer(device->receive_buffer, current_index, &payload_length);
  if(payload_length == 0){
    return AI_PACKET_ERROR_NO_LENGTH;
  }
  

  packet->packet_size = packet_length;
  packet->payload = device->user_raw_buffer;
  packet->payload_size = payload_length;
  packet->payload_type = (ai_logging_payload_type)payload_type;
  packet->shape.n_shape = 0;

  if(device->copy_next_byte_in_user_buffer == 0)
  {
    // Packet reception is complete
    device->receive_buffer_read_from = header_end_position; // We move to the following packet
    device->copy_next_byte_in_user_buffer = -1;
    device->user_buffer_position = 0;
    return AI_PACKET_OK;
  }
  else if(device->copy_next_byte_in_user_buffer > 0)
  {
    // Wait for next data chunk to be received
    return AI_NOT_ENOUGH_DATA_READ;
  }
  else
  {
    // New packet to be managed
    int32_t byte_to_copy = device->receive_buffer_position - current_index;
    memcpy(device->user_raw_buffer, device->receive_buffer + current_index, byte_to_copy); // Moving byte from internal to user buffer
    device->user_buffer_position = byte_to_copy;
    device->receive_buffer_position -= byte_to_copy;// Repositioning receive buffer position cause previous bytes have been moved

    device->copy_next_byte_in_user_buffer = payload_length - byte_to_copy;
    return AI_NOT_ENOUGH_DATA_READ;
  }
}


void ai_logging_prepare_next_packet(ai_logging_device_t *device)
{
  uint32_t last_packet_end_index = device->receive_buffer_read_from;
  uint32_t size_to_copy = 0;
  if(device->receive_buffer_position > last_packet_end_index)
  {
    size_to_copy = device->receive_buffer_position - last_packet_end_index -1;
  }
  
  //memcpy(device->receive_buffer, device->receive_buffer+last_packet_end_index + 1, size_to_copy);
  memmove(device->receive_buffer, device->receive_buffer+last_packet_end_index + 1, size_to_copy);
  device->receive_buffer_read_from = 0;
  device->receive_buffer_position = size_to_copy;
}


void ai_logging_send_packet(ai_logging_device_t *device, ai_logging_packet_t* packet)
{
  uint32_t message_data_size = 0;
  if(packet->message_size != 0){ // If we have a message
    message_data_size = AI_LOGGING_PAYLOAD_COMMAND_FIXED_SIZE + packet->message_size;
  }

  uint16_t payload_shape_data_size = 0;
  uint32_t payload_shape_size = 0;
  
  if(packet->shape.n_shape != 0){// If shape is not 0
    payload_shape_data_size = sizeof(uint16_t)*(packet->shape.n_shape);
    payload_shape_size = AI_LOGGING_PAYLOAD_SHAPE_FIXED_SIZE + payload_shape_data_size;
  }

  uint32_t payload_data_size = 0;
  if(packet->payload_size != 0){ // If data_size is not 0
    payload_data_size = AI_LOGGING_PAYLOAD_DATA_FIXED_SIZE + packet->payload_size;
  }
  uint32_t total_payload_size = message_data_size + payload_shape_size + payload_data_size; 
  
  if(packet->timestamp >= 0){
      total_payload_size = total_payload_size + 1 + 4; // Adding size of timestamp
  }


  int8_t packet_have_been_sent = 0;
  uint8_t temp[1];
  temp[0] = AI_LOGGING_START_BYTE;
  add_data_to_buffer(device, temp, sizeof(uint8_t));
  temp[0] = AI_LOGGING_PACKET_TYPE_V1;
  add_data_to_buffer(device, temp, sizeof(uint8_t));
  add_data_to_buffer(device, (uint8_t*)&total_payload_size, sizeof(uint32_t));
  

  if(packet->message_size != 0){
    temp[0] = AI_COMMAND;
    add_data_to_buffer(device, temp, sizeof(uint8_t));

    add_data_to_buffer(device, (uint8_t*)&(packet->message_size), sizeof(uint8_t)); // Size of command
    
    if(packet->message_size + device->send_buffer_position > device->send_buffer_max_size)
    {
      while(1); // Error internal buffer must be at least 255 + 7 byte (Max uint8 + header size)
      //Improvement we can manage this case
    }
    else
    {
      add_data_to_buffer(device, packet->message,packet->message_size); // Sending command
    }
  }


  if(packet->shape.n_shape != 0){ // If shape is not 0
    temp[0] = AI_SHAPE;
    add_data_to_buffer(device, temp, sizeof(uint8_t));
    add_data_to_buffer(device, (uint8_t*)&payload_shape_data_size, sizeof(payload_shape_data_size));
    int i = 0;
    for(i = 0; i < packet->shape.n_shape; i++)
    {
      add_data_to_buffer(device, (uint8_t*)&(packet->shape.shapes[i]), sizeof(uint16_t));  
    }
  }

  if(packet->timestamp >= 0){
    temp[0] = AI_TIMESTAMP;
    add_data_to_buffer(device, temp, sizeof(uint8_t));
    add_data_to_buffer(device, (uint8_t*)&(packet->timestamp), sizeof(int32_t));
  }
  
  
  if(packet->payload_size != 0){ // If data_size is not 0
    add_data_to_buffer(device, (uint8_t*)&(packet->payload_type), sizeof(uint8_t));
    add_data_to_buffer(device, (uint8_t*)&(packet->payload_size), sizeof(uint32_t));

    if(packet->payload_size + device->send_buffer_position > device->send_buffer_max_size) // Decide weather to perform copy to buffer or not
    {
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);
     
      device->send_buffer_position = 0;
      _ai_logging_call_send_fptr(device, packet->payload, packet->payload_size);

      packet_have_been_sent = 1;
    }
    else
    {
      add_data_to_buffer(device, packet->payload, packet->payload_size);
    }
  }
  
  if(packet_have_been_sent == 0){ // Either close packet with AI_LOGGING_END_BYTE or send + close packet
    temp[0] = AI_LOGGING_END_BYTE;
    add_data_to_buffer(device, temp, sizeof(uint8_t));
    if(device->send_all_buffer == 0x01)
    {
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_max_size);
    }
    else
    {
      _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);
    }
    device->send_buffer_position = 0;    
  } else {
    temp[0] = AI_LOGGING_END_BYTE;
    add_data_to_buffer(device, temp, sizeof(uint8_t));
    _ai_logging_call_send_fptr(device, device->send_buffer, device->send_buffer_position);
    
    device->send_buffer_position = 0;
  }
}

void ai_logging_clear_packet(ai_logging_packet_t *packet)
{
  packet->packet_size = 0;
  packet->payload_type = AI_NONE;
  packet->payload = NULL;
  packet->payload_size = 0;
  packet->shape.n_shape = 0;
  packet->message = NULL;
  packet->message_size = 0;
  packet->timestamp = -1;
}


// AILogging helpers
int32_t ai_logging_find_start_byte(ai_logging_device_t *device, uint32_t from)
{
  for(uint32_t i = from; i < device->receive_buffer_position; i++)
  {
    if(device->receive_buffer[i] == AI_LOGGING_START_BYTE)
    {
      return i;
    }
  }

  return -1;
}

uint8_t ai_logging_is_there_packet_type_v1(ai_logging_device_t *device, uint32_t at)
{
  if(device->receive_buffer[at] == AI_LOGGING_PACKET_TYPE_V1)
  {
    return 1;
  }
  else
  {
    return 0;
  }
}

uint8_t ai_logging_is_there_packet_type_v2(ai_logging_device_t *device, uint32_t at)
{
  if(device->receive_buffer[at] == AI_LOGGING_PACKET_TYPE_V2)
  {
    return 1;
  }
  else
  {
    return 0;
  }
}

// Global Helpers
uint32_t read_uint32_from_buffer(uint8_t *buffer, uint32_t shift, uint32_t *data_out)
{
  memcpy(data_out, buffer+shift, 4);
  return shift + 4;
}

int32_t read_int32_from_buffer(uint8_t *buffer, uint32_t shift, int32_t *data_out)
{
  memcpy(data_out, buffer+shift, 4);
  return shift + 4;
}

uint32_t read_uint16_from_buffer(uint8_t *buffer, uint32_t shift, uint16_t *data_out)
{
  memcpy(data_out, buffer+shift, 2);
  return shift + 2;
}

uint32_t read_uint8_from_buffer(uint8_t *buffer, uint32_t shift, uint8_t *data_out)
{
  memcpy(data_out, buffer+shift, 1);
  return shift + 1;
}

void _ai_logging_fire_error(ai_logging_device_t * device)
{
  if(device->error_callback != NULL)
  {
    device->error_callback();
  }
}

void _ai_logging_call_send_fptr(ai_logging_device_t *device, uint8_t *data_ptr, uint32_t data_size)
{
  if(device->send_function_ctx == NULL)
  {
    if(device->send_fptr != NULL)
    {
      device->send_fptr(data_ptr, data_size);
    }
    else
    {
      _ai_logging_fire_error(device);
    }
  }
  else
  {
    if(device->send_ctx_fptr != NULL)
    {
      device->send_ctx_fptr(device->send_function_ctx, data_ptr, data_size);
    }
    else
    {
      _ai_logging_fire_error(device); 
    }
  }
}

void add_data_to_buffer(ai_logging_device_t *device, uint8_t *data_ptr, uint16_t size)
{
  if(device->send_buffer_position + size > device->send_buffer_max_size)
  {
    _ai_logging_fire_error(device);
  }
  else
  {
    memcpy(device->send_buffer+device->send_buffer_position, data_ptr, size);
    device->send_buffer_position += size;
  }
}

void ai_logging_create_shape_0d(ai_logging_shape *shape)
{
  shape->n_shape = 0;
}
void ai_logging_create_shape_1d(ai_logging_shape *shape, uint16_t dim_x)
{
  shape->n_shape = 1;
  shape->shapes[0] = dim_x;
}
void ai_logging_create_shape_2d(ai_logging_shape *shape, uint16_t dim_x, uint16_t dim_y)
{
  shape->n_shape = 2;
  shape->shapes[0] = dim_x;
  shape->shapes[1] = dim_y;
}
void ai_logging_create_shape_3d(ai_logging_shape *shape, uint16_t dim_x, uint16_t dim_y, uint16_t dim_z)
{
  shape->n_shape = 3;
  shape->shapes[0] = dim_x;
  shape->shapes[1] = dim_y;
  shape->shapes[2] = dim_z;
}

ai_logging_message create_message(uint8_t *message_buffer, uint8_t message_size)
{
  ai_logging_message message;
  message.buffer = message_buffer;
  message.size = message_size;
  return message;
}

ai_logging_buffer create_buffer(uint8_t *buffer, uint32_t buffer_size)
{
  ai_logging_buffer buffer_out;
  buffer_out.buffer = buffer;
  buffer_out.size =  buffer_size;
  return buffer_out;
}

#ifdef __cplusplus
}
#endif
