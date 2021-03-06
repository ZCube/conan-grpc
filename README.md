[![Download](https://api.bintray.com/packages/zcube/conan-public/grpc%3Azcube/images/download.svg) ](https://bintray.com/zcube/conan-public/grpc%3Azcube/_latestVersion)
[![Build Status Travis](https://travis-ci.org/ZCube/conan-grpc.svg?branch=stable%2F1.34.0)](https://travis-ci.org/zcube/conan-grpc)
[![Build Status AppVeyor](https://ci.appveyor.com/api/projects/status/jswwtxibxwtr1k0f/branch/stable/1.34.0?svg=true)](https://ci.appveyor.com/project/zcube/conan-grpc)
# conan-grpc
Conan package for gRPC framework with protobuf.

dynamic version check from github releases from https://api.github.com/repos/grpc/grpc/releases

version cache file: git.branch (generated)

The packages generated with this **conanfile** can be found on [Bintray](https://bintray.com/zcube/conan-public/grpc%3Azcube).


## Issues

If you wish to report an issue or make a request for a package, please do so here:

[Issues Tracker](https://github.com/zcube/conan-grpc/issues)


## For Users

### Basic setup

    $ conan install grpc/1.34.0@zcube/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    grpc/1.34.0@zcube/stable

    [generators]
    cmake

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.

#### CMake Setup Example

```
set(CMAKE_CXX_STANDARD 11)

# conan setup
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
include_directories(${CMAKE_BINARY_DIR})

# find packages
find_package(protobuf CONFIG REQUIRED)
find_package(gRPC CONFIG REQUIRED)

# project setting
add_executable(greeter_client_server greeter_client_server.cc helloworld.proto)
target_link_libraries(greeter_client_server gRPC::grpc++_reflection gRPC::grpc++ protobuf::libprotobuf)
grpc_generate(TARGET greeter_client_server)
```

#### CMake project example

https://github.com/ZCube/grpc-cmake-example


## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

    $ conan create . bincrafters/stable


### Available Options
| Option        | Default | Possible Values  |
| ------------- |:----------------- |:------------:|
| fPIC      | True |  [True, False] |
| build_codegen      | True |  [True, False] |
| build_csharp_ext      | False |  [True, False] |


## Add Remote

    $ conan remote add zcube "https://api.bintray.com/conan/zcube/conan-public"


## Using protoc

```
conan install grpc/1.34.0@zcube/stable -g virtualrunenv
activate_run.bat
protoc
```


## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package grpc and protobuf.
It does *not* in any way apply or is related to the actual software being packaged.

[MIT](https://github.com/zcube/conan-zcube/blob/stable/master/LICENSE.md)

## References

https://github.com/inexorgame/conan-grpc

https://github.com/0x8000-0000/conan-recipes/tree/master/recipes/grpc
