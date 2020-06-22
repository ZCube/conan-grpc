from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class grpcConan(ConanFile):
    name = "grpc"
    version = "1.29.1"
    description = "gRPC framework with protobuf"
    topics = ("conan", "grpc", "rpc", "protobuf")
    url = "https://github.com/zcube/conan-grpc"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"
    author = "zcube <zcube@zcube.kr>"
    exports_sources = ["CMakeLists.txt", "grpc.cmake"]
    generators = "cmake", "cmake_find_package_multi"
    short_paths = True

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "build_codegen": [True, False],
        "build_csharp_ext": [True, False]
    }
    
    default_options = {
        "fPIC": True,
        "build_codegen": True,
        "build_csharp_ext": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "zlib/1.2.11",
        "openssl/1.1.1g",
        "c-ares/1.15.0",
        "abseil/20200225.2",
        "gflags/2.2.2",
    )
    
    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            
    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        git.clone("https://github.com/grpc/grpc.git", "v1.29.1")
        self.run("cd {} && git submodule init && git submodule update third_party/protobuf".format(self._source_subfolder))
        self.run("cd {} && git submodule init && git submodule update third_party/googleapis".format(self._source_subfolder))

        cmake_path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        ssl_cmake_path = os.path.join(self._source_subfolder, "cmake", "ssl.cmake")
        cares_cmake_path = os.path.join(self._source_subfolder, "cmake", "cares.cmake")
        gflags_cmake_path = os.path.join(self._source_subfolder, "cmake", "gflags.cmake")

        tools.replace_in_file(cmake_path, "target_include_directories(check_epollexclusive",
            '''set_source_files_properties(test/build/check_epollexclusive.c PROPERTIES LANGUAGE CXX)
target_include_directories(check_epollexclusive''')

        tools.replace_in_file(cmake_path, "set(CMAKE_CXX_STANDARD 11)", "")
        tools.replace_in_file(cmake_path, "absl::time", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::strings", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::str_format", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::memory", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::optional", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::inlined_vector", "CONAN_PKG::abseil")
        tools.replace_in_file(ssl_cmake_path, "${OPENSSL_LIBRARIES}", "CONAN_PKG::openssl")
        tools.replace_in_file(ssl_cmake_path, "OpenSSL::SSL OpenSSL::Crypto", "CONAN_PKG::openssl")
        tools.replace_in_file(cares_cmake_path, "c-ares::cares", "CONAN_PKG::c-ares")
        tools.replace_in_file(gflags_cmake_path, "gflags::gflags", "CONAN_PKG::gflags")

        protobuf_cmake_path = os.path.join(self._source_subfolder, "third_party", "protobuf", "cmake")
        protobuf_config_cmake_path = os.path.join(protobuf_cmake_path, "protobuf-config.cmake.in")

        tools.replace_in_file("{}/CMakeLists.txt".format(protobuf_cmake_path),
            "set(LIB_PREFIX lib)", "set(LIB_PREFIX)")

        tools.replace_in_file("{}/CMakeLists.txt".format(protobuf_cmake_path),
            "set(CMAKE_CXX_STANDARD 11)", "")

        tools.replace_in_file("{}/install.cmake".format(protobuf_cmake_path),
            '''set(CMAKE_INSTALL_CMAKEDIR "cmake" CACHE STRING "${_cmakedir_desc}")''',
            '''set(CMAKE_INSTALL_CMAKEDIR "${CMAKE_INSTALL_LIBDIR}/cmake/protobuf" CACHE STRING "${_cmakedir_desc}")''')

        tools.replace_in_file("{}/install.cmake".format(protobuf_cmake_path),
            "CMAKE_INSTALL_CMAKEDIR", "PROTOBUF_CMAKE_INSTALL_CMAKEDIR")

        grpcconfig_cmake_path = os.path.join(self._source_subfolder, "cmake", "gRPCConfig.cmake.in")
        tools.save(grpcconfig_cmake_path, '''
function(grpc_generate)
include(CMakeParseArguments)

set(_options APPEND_PATH)
set(_singleargs LANGUAGE OUT_VAR EXPORT_MACRO PROTOC_OUT_DIR)
if(COMMAND target_sources)
  list(APPEND _singleargs TARGET)
endif()
set(_multiargs PROTOS IMPORT_DIRS GENERATE_EXTENSIONS)

cmake_parse_arguments(grpc_generate "${_options}" "${_singleargs}" "${_multiargs}" "${ARGN}")

if(NOT grpc_generate_TARGET)
message(SEND_ERROR "Error: grpc_generate called without any targets or source files")
return()
endif()

find_program(_GRPC_CPP_PLUGIN NAMES grpc_cpp_plugin)
mark_as_advanced(_GRPC_CPP_PLUGIN)

protobuf_generate(TARGET ${grpc_generate_TARGET} LANGUAGE cpp)
set(_GRPC_PLUGIN "protoc-gen-grpc=${_GRPC_CPP_PLUGIN}")
protobuf_generate(TARGET ${grpc_generate_TARGET} LANGUAGE grpc GENERATE_EXTENSIONS .grpc.pb.h .grpc.pb.cc)

endfunction(grpc_generate)
''', append = True)

        # until grpc 1.30
        if Version(self.version) < "1.30.0":
            tools.replace_in_file(protobuf_config_cmake_path,
                "ARGS --${protobuf_generate_LANGUAGE}_out ${_dll_export_decl}${protobuf_generate_PROTOC_OUT_DIR} ${_protobuf_include_path} ${_abs_file}",
                "ARGS --${protobuf_generate_LANGUAGE}_out ${_dll_export_decl}${protobuf_generate_PROTOC_OUT_DIR} --plugin=${_GRPC_PLUGIN} ${_protobuf_include_path} ${_abs_file}")

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions['gRPC_BUILD_CODEGEN'] = "ON" if self.options.build_codegen else "OFF"
        cmake.definitions['gRPC_BUILD_CSHARP_EXT'] = "ON" if self.options.build_csharp_ext else "OFF"
        cmake.definitions['gRPC_BUILD_TESTS'] = "OFF"
        cmake.definitions['gRPC_INSTALL'] = "ON"
        cmake.definitions['gRPC_USE_PROTO_LITE'] = "OFF"
        
        cmake.definitions['gRPC_ABSL_PROVIDER'] = "package"
        cmake.definitions['gRPC_CARES_PROVIDER'] = "package"
        cmake.definitions['gRPC_ZLIB_PROVIDER'] = "package"
        cmake.definitions['gRPC_SSL_PROVIDER'] = "package"
        cmake.definitions['gRPC_GFLAGS_PROVIDER'] = "package"
        cmake.definitions['gRPC_PROTOBUF_PROVIDER'] = "module"
        cmake.definitions['gRPC_INSTALL_CMAKEDIR'] = "lib/cmake/gRPC"

        cmake.definitions['protobuf_BUILD_SHARED_LIBS'] = "OFF"
        cmake.definitions['gRPC_BUILD_SHARED_LIBS'] = "OFF"

        cmake.definitions['protobuf_DEBUG_POSTFIX'] = ""

        cmake.definitions['protobuf_INSTALL'] = "ON"
        cmake.definitions["protobuf_BUILD_TESTS"] = "OFF"
        cmake.definitions["protobuf_WITH_ZLIB"] = "ON"
        cmake.definitions["protobuf_BUILD_PROTOC_BINARIES"] = "ON" if self.options.build_codegen else "OFF"
        cmake.definitions["protobuf_BUILD_PROTOBUF_LITE"] = "OFF"
        
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
            cmake.definitions["gRPC_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses")
        self.copy('grpc.cmake', dst='cmake')
        self.copy('*', dst='include', src='{}/third_party/googleapis'.format(self._source_subfolder), keep_path=True)
        self.copy('*', dst='include', src='{}/include'.format(self._source_subfolder))
        self.copy('*.cmake', dst='lib', src='{}/lib'.format(self._build_subfolder), keep_path=True)
        self.copy("*.lib", dst="lib", src="", keep_path=False)
        self.copy("*.a", dst="lib", src="", keep_path=False)
        self.copy("*", dst="bin", src="bin")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.libs = [
            "grpc++_alts",
            "grpc++_unsecure",
            "grpc++_reflection",
            "grpc++_error_details",
            "grpc++",
            "grpc_unsecure",
        ]
        if self.options.build_codegen:
            self.cpp_info.libs += [
                "grpc_plugin_support",
            ]
        self.cpp_info.libs += [
            "grpcpp_channelz",
            "grpc",
            "gpr",
            "address_sorting",
            "upb",
            "protobuf-lite",
            "protobuf",
        ]
        if self.options.build_codegen:
            self.cpp_info.libs += [
                "protoc",
            ]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
