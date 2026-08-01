cmake_minimum_required(VERSION 3.16)
project(dsc12a_clang_facts LANGUAGES C CXX)

find_package(LLVM CONFIG REQUIRED)
find_package(Clang CONFIG REQUIRED)
include(AddLLVM)

add_executable(dsc-clang-facts clang_facts.cpp)
target_compile_features(dsc-clang-facts PRIVATE cxx_std_17)
target_include_directories(dsc-clang-facts PRIVATE ${LLVM_INCLUDE_DIRS} ${CLANG_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

add_executable(dsc-clang-rewrite clang_rewrite_overlay.cpp)
target_compile_features(dsc-clang-rewrite PRIVATE cxx_std_17)
target_include_directories(dsc-clang-rewrite PRIVATE ${LLVM_INCLUDE_DIRS} ${CLANG_INCLUDE_DIRS})

if(TARGET clang-cpp)
  target_link_libraries(dsc-clang-facts PRIVATE clang-cpp)
  target_link_libraries(dsc-clang-rewrite PRIVATE clang-cpp)
  if(TARGET LLVM)
    target_link_libraries(dsc-clang-facts PRIVATE LLVM)
    target_link_libraries(dsc-clang-rewrite PRIVATE LLVM)
  endif()
else()
  llvm_map_components_to_libnames(LLVM_LIBS support)
  target_link_libraries(
    dsc-clang-facts
    PRIVATE
      clangTooling
      clangFrontend
      clangSerialization
      clangDriver
      clangParse
      clangSema
      clangAnalysis
      clangEdit
      clangASTMatchers
      clangAST
      clangLex
      clangBasic
      clangIndex
      ${LLVM_LIBS}
  )
  target_link_libraries(
    dsc-clang-rewrite
    PRIVATE
      clangTooling
      clangFrontend
      clangSerialization
      clangDriver
      clangParse
      clangSema
      clangAnalysis
      clangEdit
      clangASTMatchers
      clangAST
      clangLex
      clangBasic
      clangIndex
      ${LLVM_LIBS}
  )
endif()
