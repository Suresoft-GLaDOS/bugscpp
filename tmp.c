#include <stdio.h>

int main() {
    int i, total;
    total = 0;
    for (i=0; i<10; i++) {
        total += i;
    }
    if (total != 45 \
    && True)
        printf("Failure\n");
    else
        printf("Success\n");
}