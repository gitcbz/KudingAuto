QT += core gui network

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17

TARGET = KudingJudge
TEMPLATE = app

SOURCES += \
    src/main.cpp \
    src/mainwindow.cpp \
    src/backend_client.cpp \
    src/login_tab.cpp \
    src/test_tab.cpp \
    src/problem_tab.cpp \
    src/settings_tab.cpp \
    src/code_editor.cpp

HEADERS += \
    src/mainwindow.h \
    src/backend_client.h \
    src/login_tab.h \
    src/test_tab.h \
    src/problem_tab.h \
    src/settings_tab.h \
    src/code_editor.h

RESOURCES += resources.qrc

# 设置输出目录
CONFIG(debug, debug|release) {
    DESTDIR = $$PWD/build/debug
} else {
    DESTDIR = $$PWD/build/release
}

MOC_DIR = $$DESTDIR/moc
OBJECTS_DIR = $$DESTDIR/obj
RCC_DIR = $$DESTDIR/rcc
UI_DIR = $$DESTDIR/ui
