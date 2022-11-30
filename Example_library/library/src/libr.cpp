#include "libr.h"
#include <iostream>

Library::Library()
{
    std::cout<<"Library created"<<std::endl; 
}

Library::~Library()
{
    std::cout<<"Library destroyed"<<std::endl; 
}

void Library::print(std::string message)
{
    std::cout<<"Library message :" << message<<std::endl;
}