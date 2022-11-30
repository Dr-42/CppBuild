#pragma once
#include <string>

#ifdef _WIN32
#define LAPI __declspec(dllexport)
#endif

#ifdef __linux__
#define LAPI __attribute__((visibility("default")))
#endif

class LAPI Library{
public:
    Library();
    ~Library();
    void print(std::string message);
};