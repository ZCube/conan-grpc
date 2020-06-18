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
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"
    short_paths = True

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_codegen": [True, False],
        "build_csharp_ext": [True, False]
    }
    
    default_options = {
        "shared": False,
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

        cmake_path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        ssl_cmake_path = os.path.join(self._source_subfolder, "cmake", "ssl.cmake")
        cares_cmake_path = os.path.join(self._source_subfolder, "cmake", "cares.cmake")
        gflags_cmake_path = os.path.join(self._source_subfolder, "cmake", "gflags.cmake")

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
        tools.replace_in_file("{}/CMakeLists.txt".format(protobuf_cmake_path),
            "project(protobuf C CXX)", "#project(protobuf C CXX)")

        tools.replace_in_file("{}/CMakeLists.txt".format(protobuf_cmake_path),
            "${protobuf_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")

        tools.replace_in_file("{}/CMakeLists.txt".format(protobuf_cmake_path),
            "${protobuf_BINARY_DIR}", "${CMAKE_CURRENT_BINARY_DIR}")

        for cmake_file in ["libprotobuf-lite.cmake", "libprotobuf.cmake", "libprotoc.cmake"]:
            if tools.is_apple_os(self.settings.os):
                tools.replace_in_file("{}/{}".format(protobuf_cmake_path, cmake_file),
                    "VERSION ${protobuf_VERSION}",
                    "#VERSION ${protobuf_VERSION} SOVERSION ${protobuf_VERSION}")
            else:
                tools.replace_in_file("{}/{}".format(protobuf_cmake_path, cmake_file),
                    "VERSION ${protobuf_VERSION}",
                    "VERSION ${protobuf_VERSION} SOVERSION ${protobuf_VERSION}")

        for cmake_file in ["protoc.cmake"]:
            if tools.is_apple_os(self.settings.os):
                tools.replace_in_file("{}/{}".format(protobuf_cmake_path, cmake_file),
                    "VERSION ${protobuf_VERSION})",
                    "#VERSION ${protobuf_VERSION} SOVERSION ${protobuf_VERSION})")
            else:
                tools.replace_in_file("{}/{}".format(protobuf_cmake_path, cmake_file),
                    "VERSION ${protobuf_VERSION})",
                    "VERSION ${protobuf_VERSION} SOVERSION ${protobuf_VERSION})")

        tools.replace_in_file("{}/install.cmake".format(protobuf_cmake_path),
            '''set(CMAKE_INSTALL_CMAKEDIR "cmake" CACHE STRING "${_cmakedir_desc}")''',
            '''set(CMAKE_INSTALL_CMAKEDIR "${CMAKE_INSTALL_LIBDIR}/cmake/protobuf" CACHE STRING "${_cmakedir_desc}")''')

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

        cmake.definitions['protobuf_BUILD_SHARED_LIBS'] = "ON" if self.options.shared else "OFF"
        cmake.definitions['gRPC_BUILD_SHARED_LIBS'] = "ON" if self.options.shared else "OFF"

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
        self.copy('*', dst='include', src='{}/include'.format(self._source_subfolder))
        self.copy('*.cmake', dst='lib', src='{}/lib'.format(self._build_subfolder), keep_path=True)
        self.copy("*.lib", dst="lib", src="", keep_path=False)
        self.copy("*.a", dst="lib", src="", keep_path=False)
        self.copy("*", dst="bin", src="bin")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.libs = tools.collect_libs(self)

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        protoc = "protoc.exe" if self.settings.os == "Windows" else "protoc"
        self.env_info.PROTOC_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", protoc))
