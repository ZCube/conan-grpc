cmake_minimum_required(VERSION 3.0)
project(test_package CXX)

if(MSVC)
  add_definitions(-D_WIN32_WINNT=0x600)
endif()

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(protobuf CONFIG REQUIRED)
find_package(gRPC CONFIG REQUIRED)

message(STATUS "Using gRPC ${gRPC_VERSION}")
message(STATUS "Using gRPC ${protobuf_VERSION}")

include_directories(${CMAKE_BINARY_DIR})

add_executable(greeter_client_server greeter_client_server.cc helloworld.proto)
target_link_libraries(greeter_client_server CONAN_PKG::grpc)
grpc_generate(TARGET greeter_client_server)
