#include "log.h"
#include "renderer.h"

#include <iostream>

void Log::LogMessage(const char *message){
    std::cout << message << std::endl;
    Renderer r;
}

void Log::LogNumber(float number){
    std::cout << number << std::endl;
}
