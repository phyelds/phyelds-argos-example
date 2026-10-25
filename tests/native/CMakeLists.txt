cmake_minimum_required(VERSION 3.18)
project(phyelds_argos_observer CXX)
set(CMAKE_CXX_STANDARD 17)
# ARGoSConfig.cmake looks for the modules installed beside it only under the system
# prefixes: an ARGoS found through CMAKE_PREFIX_PATH would not find its own modules.
find_path(ARGOS_CMAKE_DIR FindARGoSQTOpenGL.cmake
    PATHS ${CMAKE_PREFIX_PATH} ENV CMAKE_PREFIX_PATH
    PATH_SUFFIXES share/argos3/cmake NO_DEFAULT_PATH)
find_package(ARGoS REQUIRED)
include_directories(${ARGOS_INCLUDE_DIRS})
link_directories(${ARGOS_LIBRARY_DIR})
add_executable(observer observer.cpp)
target_link_libraries(observer argos3core_simulator argos3plugin_simulator_entities
    ${ARGOS_LDFLAGS})
