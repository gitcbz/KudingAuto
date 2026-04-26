cmake_minimum_required(VERSION 3.16)
project(KudingJudge)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 COMPONENTS Core Gui Widgets Network REQUIRED)

set(PROJECT_SOURCES
    src/main.cpp
    src/mainwindow.h src/mainwindow.cpp
    src/backend_client.h src/backend_client.cpp
    src/code_editor.h src/code_editor.cpp
    src/login_tab.h src/login_tab.cpp
    src/test_tab.h src/test_tab.cpp
    src/problem_tab.h src/problem_tab.cpp
    src/settings_tab.h src/settings_tab.cpp
)

add_executable(KudingJudge ${PROJECT_SOURCES})

target_link_libraries(KudingJudge
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::Network
)

# 设置输出目录
set_target_properties(KudingJudge PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
