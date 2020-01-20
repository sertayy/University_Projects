
code segment

    mov si, 0  ;to reset si register before usage
    mov bp, 0  ;to reset bp registor before usage
    read:
    mov ax,0   ;to reset ax register
    mov ah,01h ;getting input command
    int 21h    ;to execute getting input command
    mov ah,0   ;to prevent possible mistakes in calculations

    conent:    ;if enter is given as input jumps to _enter label
    cmp al, 13
    je _enter


    con1:      ;if space is given as input jumps to jmpspace label
    cmp al, 32
    je jmpspace

    con2 :     ;if plus sign is given as input jumps to jmpaddition label
    cmp al, 43
    je jmpaddition

    con3 :     ;if asterisk is given as input jumps to jmpmulti label
    cmp al, 42
    je jmpmulti

    con4 :     ;if slash is given as input jumps to jmpdivision label
    cmp al, 47
    je jmpdivision

    con5 :     ;if A is given as input jumps to jumpa label
    cmp al, 65
    je jumpa

    con6 :     ;if B is given as input jumps to jumpb label
    cmp al, 66
    je jumpb

    con7:      ;if C is given as input jumps to jumpc label
    cmp al, 67
    je jumpc

    con8:      ;if D is given as input jumps to jumpd label
    cmp al, 68
    je jumpd

    con9:      ;if E is given as input jumps to jumpe label
    cmp al, 69
    je jumpe

    con10:     ;if F is given as input jumps to jumpf label
    cmp al, 70
    je jumpf

    con11:     ;if xor sign is given as input jumps to jumpxor label
    cmp al, 94
    je jumpxor

    con12:     ;if and sign is given as input jumps to jumpand label
    cmp al, 38
    je jumpand

    con13:     ;if or sign is given as input jumps to jumpor label
    cmp al, 124
    je jumpor



    inc bp     ;to represent a number is given as input

    jmp stack1 ;to place given number in stack


    jmp read

    jmpspace:  ;intermediate label to jump to space label
    jmp space


    jumpa:     ;intermediate label to jump to _a label
    jmp _a

    jumpb:     ;intermediate label to jump to _b label
    jmp _b

    jumpc:     ;intermediate label to jump to _c label
    jmp _c


    jumpd:     ;intermediate label to jump to _d label
    jmp _d

    jumpf:     ;intermediate label to jump to _f label
    jmp _f

    jumpe:     ;intermediate label to jump to _e label
    jmp _e

    jumpor:    ;intermediate label to jump to bitwiseor label
    jmp bitwiseor

    jumpand:   ;intermediate label to jump to bitwiseand label
    jmp bitwiseand

    jumpxor:   ;intermediate label to jump to bitwisexor label
    jmp bitwisexor

    read1:     ;intermediate label to jump to read label
    jmp read


    jmpmulti:  ;intermediate label to jump to multiplication label
    jmp multiplication

    jmpdivision:  ;intermediate label to jump to division label
    jmp division

    jmpaddition:  ;intermediate label to jump to addition label
    jmp addition


    _enter:       ;when enter is given as input this label is being executed
    inc si        ;counter for number of digits of the output
    mov ax, 0     ;to reset dx register
    mov dx, 0     ;to reset ax register
    pop ax        ;result is popped  to ax
    mov bx, 16d
    div bx        ;to divide result to 16
    push dx       ;remainder is pushed to stack
    push ax       ;quotient is pushed to stack for dividing later
    mov cx, ax
    cmp cx, 0
    jne _enter    ;if quotient is not zero more divisions are needed
    pop dx        ;zero is popped from stack
    mov ah,02h    ;output command
    mov dx,0Ah    ;new line command
    int 21h
    jmp print     ;to print output

    ifnumber:     ;if a character of the output is a digit this label is executed
    add dx, 30h
    jmp print1

    ifletter:     ;if a character of the output is a letter this label is executed
    add dx, 37h
    jmp print1


    print:        ;to print the output
    mov dx, 0     ;sets dx to 0 to give the output right
    pop dx        ;first character to write
    cmp dx, 0Ah   ;compares this character is a digit or a letter
    jae ifletter
    jb ifnumber
    print1:
    mov ax, 0
    mov ah, 02h   ;print command
    int 21h       ;prints the value in dl register
    dec si        ;decrements si value
    cmp si, 0
    jne print     ;if si is not zero executes again the print label to print all characters
    int 20h

    space:        ;if space is given as input
    mov bp, 0     ;sets bp as 0 to represent a new number or symbol is going to be the input
    jmp read1

    _stack:       ;if a number of digits in an input is more than 1
    mov bx, ax
    mov ax, 0
    sub bx, 30h   ;subtracts 30h from the input
    pop ax        ;pops the last input before the current input
    mov cx, 16d
    mul cx        ;multiplies the top of stack by 16    
    add ax, bx    ;adds the input
    push ax       ;pushes it to stack again as the last input
    dec bp        ;decrements bp to control numbers of digits in an input
    jmp read


    stack3:       ;has the same job with the _stack label, just for A, B, C, D, E, F inputs
    mov bx, ax
    mov ax, 0
    pop ax
    mov cx, 16d
    mul cx
    add ax, bx
    push ax
    dec bp
    jmp read



    bitwisexor:  ;being executed if xor is given as input
    mov bp, 0    ;sets bp to 0
    mov ax, 0
    mov bx, 0
    pop ax       ;pops the last value as operand
    pop bx       ;pops the second last value as operand
    xor ax, bx   ;operation is executed
    push ax      ;result is pushed to stack
    mov ax, 0
    mov bx, 0
    jmp read1

    bitwiseand:  ;being executed if and is given as input
    mov bp, 0    ;sets bp to 0
    mov ax, 0
    mov bx, 0
    pop ax       ;pops the last value as operand
    pop bx       ;pops the second last value as operand
    and ax, bx   ;operation is done
    push ax      ;result is pushed to stack
    mov ax, 0
    mov bx, 0
    jmp read1

    bitwiseor:   ;being executed if or is given as input
    mov bp, 0
    mov ax, 0
    mov bx, 0
    pop ax
    pop bx
    or ax, bx    ;operation is executed
    push ax      ;result is pushed to stack
    mov ax, 0
    mov bx, 0
    jmp read1


    stack1:     ;makes the stack operations if a number is given as input
    cmp bp, 1
    jne _stack
    sub ax, 30h
    push ax
    jmp read1

     stack2:    ;makes the stack operations if a letter is given as input
    cmp bp, 1
    jne stack3
    push ax
    jmp read1


    division:   ;being executed if slash is given as input
    mov bp, 0
    mov dx, 0h
    mov ax, 0
    mov bx, 0
    pop bx      ;takes the first operand
    pop ax      ;takes the second operand
    div bx      ;operation is executed
    push ax     ;result is pushed to stack
    mov ax,0
    mov cx,0
    jmp read1


    addition:   ;being executed if plus sign is given as input
    mov bp,0
    mov dx, 0
    pop bx      ;takes the first operand
    pop dx      ;takes the second operand
    add dx, bx  ;operation is executed
    push dx     ;result is pushed to stack
    mov bx, 0
    mov bx, dx
    jmp read1


    multiplication:  ;being executed if asterisk sign is given as input
    mov dx, 0
    mov bp, 0
    mov ax, 0
    pop ax           ;takes the first operand
    pop bx           ;takes the second operand
    mul bx           ;operation is executed
    push ax          ;result is pushed to stack
    mov ax,0
    mov bx,0
    jmp read1



    _a:              ;if A is given as input
    sub ax, 55d
    inc bp
    jmp stack2

    _b:              ;if B is given as input
    sub ax, 55d
    inc bp
    jmp stack2

    _c:              ;if C is given as input
    sub ax, 55d
    inc bp
    jmp stack2

    _d:              ;if D is given as input
    sub ax, 55d
    inc bp
    jmp stack2

    _e:              ;if E is given as input
    sub ax, 55d
    inc bp
    jmp stack2

    _f:              ;if F is given as input
    sub ax, 55d
    inc bp
    jmp stack2


code ends
