# conan-grpc
Conan package for gRPC framework with protobuf.

The packages generated with this **conanfile** can be found on [Bintray](https://bintray.com/zcube/conan-public/grpc%3Azcube).


## Issues

If you wish to report an issue or make a request for a package, please do so here:

[Issues Tracker](https://github.com/zcube/conan-grpc/issues)


## For Users

### Basic setup

    $ conan install grpc/1.29.1@zcube/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    grpc/1.29.1@zcube/stable

    [generators]
    cmake

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.


## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

    $ conan create . bincrafters/stable


### Available Options
| Option        | Default | Possible Values  |
| ------------- |:----------------- |:------------:|
| shared      | False |  [True, False] |
| fPIC      | True |  [True, False] |
| build_codegen      | True |  [True, False] |
| build_csharp_ext      | False |  [True, False] |


## Add Remote

    $ conan remote add zcube "https://api.bintray.com/conan/zcube/conan-public"


## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package libjpeg.
It does *not* in any way apply or is related to the actual software being packaged.

[MIT](https://github.com/zcube/conan-zcube/blob/stable/1.29.1/LICENSE.md)

## References

https://github.com/inexorgame/conan-grpc
https://github.com/0x8000-0000/conan-recipes/tree/master/recipes/grpc
