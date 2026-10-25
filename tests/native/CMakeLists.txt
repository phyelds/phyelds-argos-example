cmake_minimum_required(VERSION 3.18)
project(phyelds_argos_observer CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(ARGoS REQUIRED)
include_directories(${ARGOS_INCLUDE_DIRS})
link_directories(${ARGOS_LIBRARY_DIR})
add_executable(observer observer.cpp)
target_link_libraries(observer argos3core_simulator argos3plugin_simulator_footbot
    argos3plugin_simulator_entities ${ARGOS_LDFLAGS})
