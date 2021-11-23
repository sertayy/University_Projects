#include <stdio.h>
#include <pthread.h>

int sum = 0; // global variable of sum

void *count(void *param) {
    int i; //local to each thread
    for (i = 0; i < 10000000; i++) {
        sum += 1;
    }
    return NULL;
}

int main() {
    pthread_t tid1, tid2;
    pthread_create(&tid1, NULL, count, NULL);
    pthread_create(&tid2, NULL, count, NULL);
    
    pthread_join(tid1, NULL);
    pthread_join(tid2, NULL);
    
    printf("The total sum is %d\n", sum);
    return 0;
}
