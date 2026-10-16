cmake_minimum_required(VERSION 3.16)
project(VocaLauncher VERSION 1.0.3 LANGUAGES C)
add_executable(Voca WIN32 voca_launcher.c)
target_link_libraries(Voca shell32 kernel32)
