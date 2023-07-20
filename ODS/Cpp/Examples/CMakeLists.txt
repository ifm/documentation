cmake_minimum_required(VERSION 3.11)

project(ods_examples CXX)

#Global compiler flags
set(CMAKE_BUILD_TYPE Release) # Release or Debug
set(CMAKE_CXX_EXTENSIONS OFF) # OFF -> -std=c++14, ON -> -std=gnu++14
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED true)

#find ifm3d on the system
find_package(ifm3d 1.2.6 CONFIG
  REQUIRED COMPONENTS device framegrabber deserialize
  )

#Optional json validator package:
find_package(nlohmann_json_schema_validator)
if (NlohmannJsonSchemaValidator_FOUND)
  set(ENV{NlohmannJsonSchemaValidator_FOUND} TRUE)
else()
  set(ENV{NlohmannJsonSchemaValidator_FOUND} FALSE)
endif()
message("Variable is $ENV{NlohmannJsonSchemaValidator_FOUND}")

# Configuration example
add_executable(ods_config ods_config.cpp)
target_link_libraries(ods_config
                      nlohmann_json_schema_validator
                      ifm3d::device
                      )

## Getting data example
add_executable(ods_get_data ods_get_data.cpp)
target_link_libraries(ods_get_data
                      nlohmann_json_schema_validator
                      ifm3d::device
                      ifm3d::framegrabber
                      ifm3d::deserialize
                      )            
                      
add_executable(diagnostic diagnostic.cpp)
target_link_libraries(diagnostic
                      ifm3d::device
                      ifm3d::framegrabber
                      )            

add_executable(ods_demo ods_demo.cpp)
target_link_libraries(ods_demo
                      nlohmann_json_schema_validator
                      ifm3d::device
                      ifm3d::framegrabber
                      ) 

add_executable(bootup_monitor bootup_monitor.cpp)
target_link_libraries(bootup_monitor
                      ifm3d::device
                      ) 