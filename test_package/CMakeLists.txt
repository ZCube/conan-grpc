cmake_minimum_required(VERSION 3.0)
project(test_package CXX)

if(MSVC)
  add_definitions(-D_WIN32_WINNT=0x600)
endif()

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
conan_set_find_paths()

find_package(protobuf CONFIG REQUIRED)
find_package(gRPC CONFIG REQUIRED)

message(STATUS "Using gRPC ${gRPC_VERSION}")
message(STATUS "Using gRPC ${protobuf_VERSION}")

find_program(_GRPC_CPP_PLUGIN NAMES grpc_cpp_plugin)
mark_as_advanced(_GRPC_CPP_PLUGIN)

include_directories(${CMAKE_BINARY_DIR})

add_executable(greeter_client_server greeter_client_server.cc helloworld.proto)
target_link_libraries(greeter_client_server gRPC::grpc++_reflection gRPC::grpc++ protobuf::libprotobuf)

protobuf_generate(TARGET greeter_client_server LANGUAGE cpp)
protobuf_generate(TARGET greeter_client_server LANGUAGE grpc GENERATE_EXTENSIONS .grpc.pb.h .grpc.pb.cc PLUGIN "protoc-gen-grpc=${_GRPC_CPP_PLUGIN}")
