# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tasks.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0btasks.proto\x12\x05tasks\"7\n\x0eRentGPURequest\x12\x0e\n\x06gpu_id\x18\x01 \x01(\x05\x12\x15\n\rcompute_units\x18\x02 \x01(\x05\"A\n\x1bStartTrainingSessionRequest\x12\x0e\n\x06gpu_id\x18\x01 \x01(\x05\x12\x12\n\nmodel_data\x18\x02 \x01(\x0c\"#\n\x11ReleaseGPURequest\x12\x0e\n\x06gpu_id\x18\x01 \x01(\x05\"%\n\x0fSessionResponse\x12\x12\n\nsession_id\x18\x01 \x01(\x05\"!\n\x0fGenericResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"L\n\x1cUpdateModelParametersRequest\x12\x12\n\nsession_id\x18\x01 \x01(\x05\x12\x18\n\x10model_parameters\x18\x02 \x01(\x0c\"/\n\x1dUpdateModelParametersResponse\x12\x0e\n\x06status\x18\x01 \x01(\t2\xbf\x02\n\x0bTaskService\x12\x38\n\x07RentGPU\x12\x15.tasks.RentGPURequest\x1a\x16.tasks.GenericResponse\x12>\n\nReleaseGPU\x12\x18.tasks.ReleaseGPURequest\x1a\x16.tasks.GenericResponse\x12R\n\x14StartTrainingSession\x12\".tasks.StartTrainingSessionRequest\x1a\x16.tasks.SessionResponse\x12\x62\n\x15UpdateModelParameters\x12#.tasks.UpdateModelParametersRequest\x1a$.tasks.UpdateModelParametersResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tasks_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_RENTGPUREQUEST']._serialized_start=22
  _globals['_RENTGPUREQUEST']._serialized_end=77
  _globals['_STARTTRAININGSESSIONREQUEST']._serialized_start=79
  _globals['_STARTTRAININGSESSIONREQUEST']._serialized_end=144
  _globals['_RELEASEGPUREQUEST']._serialized_start=146
  _globals['_RELEASEGPUREQUEST']._serialized_end=181
  _globals['_SESSIONRESPONSE']._serialized_start=183
  _globals['_SESSIONRESPONSE']._serialized_end=220
  _globals['_GENERICRESPONSE']._serialized_start=222
  _globals['_GENERICRESPONSE']._serialized_end=255
  _globals['_UPDATEMODELPARAMETERSREQUEST']._serialized_start=257
  _globals['_UPDATEMODELPARAMETERSREQUEST']._serialized_end=333
  _globals['_UPDATEMODELPARAMETERSRESPONSE']._serialized_start=335
  _globals['_UPDATEMODELPARAMETERSRESPONSE']._serialized_end=382
  _globals['_TASKSERVICE']._serialized_start=385
  _globals['_TASKSERVICE']._serialized_end=704
# @@protoc_insertion_point(module_scope)
