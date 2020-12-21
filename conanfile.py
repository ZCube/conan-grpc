from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
import os.path

def latest(url):
    import urllib.request
    import json

    response = urllib.request.urlopen(url)
    data = response.read()
    releases = json.loads(data.decode('utf-8'))
    for release in releases:
        if release["draft"] == False and release["prerelease"] == False:
            return release["tag_name"]
    raise Exception('Unknown tags')

def latestWithCache(url):
    version = "master"
    try:
        with open("git.branch", "r") as version_file:
            version = version_file.readline().strip()
    except Exception as e:
        version = latest(url)
    with open("git.branch", "w") as version_file:
        version_file.write(version)
    return version


class grpcConan(ConanFile):
    name = "grpc"
    description = "gRPC framework with protobuf"
    topics = ("conan", "grpc", "rpc", "protobuf")
    url = "https://github.com/zcube/conan-grpc"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"
    author = "zcube <zcube@zcube.kr>"
    exports_sources = ["CMakeLists.txt", "grpc.cmake", "git.branch"]
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
        "c-ares/1.16.1",
        "abseil/20200923.2",
        "gflags/2.2.2",
        "re2/20201001",
    )
    
    def set_version(self):
        url = 'https://api.github.com/repos/grpc/grpc/releases'
        self.version = latestWithCache(url)[1:]

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            
    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        git.clone("https://github.com/grpc/grpc.git", "v" + self.version)
        self.run("cd {} && git submodule init && git submodule update third_party/protobuf".format(self._source_subfolder))
        self.run("cd {} && git submodule init && git submodule update third_party/googleapis".format(self._source_subfolder))

        cmake_path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        ssl_cmake_path = os.path.join(self._source_subfolder, "cmake", "ssl.cmake")
        cares_cmake_path = os.path.join(self._source_subfolder, "cmake", "cares.cmake")
        gflags_cmake_path = os.path.join(self._source_subfolder, "cmake", "gflags.cmake")
        re2_cmake_path = os.path.join(self._source_subfolder, "cmake", "re2.cmake")

        tools.replace_in_file(cmake_path, "target_include_directories(check_epollexclusive",
            '''set_source_files_properties(test/build/check_epollexclusive.c PROPERTIES LANGUAGE CXX)
target_include_directories(check_epollexclusive''')

        tools.replace_in_file(cmake_path, "set(CMAKE_CXX_STANDARD 11)", "")
        tools.replace_in_file(cmake_path, "absl::time", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::strings", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::str_format", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::memory", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::optional", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::base", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::status", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::flat_hash_set", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::synchronization", "CONAN_PKG::abseil")
        tools.replace_in_file(cmake_path, "absl::inlined_vector", "CONAN_PKG::abseil")
        tools.replace_in_file(ssl_cmake_path, "${OPENSSL_LIBRARIES}", "CONAN_PKG::openssl")
        tools.replace_in_file(ssl_cmake_path, "OpenSSL::SSL OpenSSL::Crypto", "CONAN_PKG::openssl")
        tools.replace_in_file(cares_cmake_path, "c-ares::cares", "CONAN_PKG::c-ares")
        if os.path.isfile(gflags_cmake_path):
            tools.replace_in_file(gflags_cmake_path, "gflags::gflags", "CONAN_PKG::gflags", strict=False)
        tools.replace_in_file(re2_cmake_path, "re2::re2", "CONAN_PKG::re2")

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
protobuf_generate(TARGET ${grpc_generate_TARGET} PLUGIN ${_GRPC_PLUGIN} LANGUAGE grpc GENERATE_EXTENSIONS .grpc.pb.h .grpc.pb.cc)

endfunction(grpc_generate)
''', append = True)

        tools.replace_in_file(protobuf_config_cmake_path,
            '''file(RELATIVE_PATH _rel_dir ${DIR} ${_abs_dir})''', '''string(FIND "${_rel_dir}" "../" _is_in_parent_folder)''')
        tools.replace_in_file(protobuf_config_cmake_path,
            '''if(NOT "${_rel_dir}" MATCHES "^\.\.[/\\\\].*")''', '''if (NOT ${_is_in_parent_folder} EQUAL 0)''')
            
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
        cmake.definitions['gRPC_RE2_PROVIDER'] = "package"
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

    @property
    def _cmake_install_base_path(self):
        return os.path.join("cmake")
    
    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses")
        self.copy('grpc.cmake', dst=self._cmake_install_base_path)
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
        
        #self.cpp_info.builddirs = [
        #    self._cmake_install_base_path,
        #]
        self.cpp_info.build_modules = [
            os.path.join(self._cmake_install_base_path, "grpc.cmake"),
        ]
