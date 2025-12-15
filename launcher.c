#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    int choice;
    char command[512];
    
    printf("======================================\n");
    printf("     ASCII Face - Camera Selection    \n");
    printf("======================================\n");
    printf("Please enter your camera index (0-9).\n");
    printf("Usually 0 is your default webcam.\n");
    printf("\n");
    printf("Selection: ");
    
    // Read integer input
    if (scanf("%d", &choice) != 1) {
        printf("Invalid input. Exiting.\n");
        return 1;
    }
    
    if (choice < 0 || choice > 10) {
        printf("Camera index out of likely range (0-10). Proceeding anyway...\n");
    }

    // Since 'go' might not be in PATH as per earlier steps, we use the full path if we knew it.
    // Ideally we assume user runs this from an environment where 'go' works OR we use the path from before.
    // The user had: C:\Program Files\Go\bin\go.exe
    // Let's try to construct the command.
    
    // We use quotes just in case of spaces, though Go path usually has none or we handle it.
    sprintf(command, "\"C:\\Program Files\\Go\\bin\\go.exe\" run main.go %d", choice);
    
    printf("Launching backend with Camera %d...\n", choice);
    system(command);
    
    return 0;
}
