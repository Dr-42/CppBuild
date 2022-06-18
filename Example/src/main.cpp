#include <iostream>
#include "utils/renderer.h"
#include "utils/log.h"


int main(){
    Renderer r;
    Log l;
    l.LogMessage("Hello World!");
    float num = r.div(2.2f, 2.3f);
    l.LogNumber(num);
    return 0;
}
