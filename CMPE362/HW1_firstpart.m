%%%%%%%% Problem 1 %%%%%%%%

t = -2:0.01:2;
figure(1);
%used subplot function to fit all subfigures belong to a single figure
subplot(5,2,1);
y1 = sin(2*pi*t);
plot(t,y1);
title('Subplot of y1');

subplot(5,2,2);
y2 = sin(2*pi*10*t); 
plot(t,y2);
title('Subplot of y2');

subplot(5,2,3);
y3 = 10*sin(2*pi*t);
plot(t,y3);
title('Subplot of y3');

subplot(5,2,4);
y4 = sin(2*pi*t)+10; 
plot(t,y4);
title('Subplot of y4');

subplot(5,2,5);
y5 = sin(2*pi*(t-0.5)); 
plot(t,y5);
title('Subplot of y5');

subplot(5,2,6);
y6 = 10*sin(2*pi*10*t); 
plot(t,y6);
title('Subplot of y6');

subplot(5,2,7);
y7 = t.*sin(2*pi*t);
plot(t,y7);
title('Subplot of y7');

subplot(5,2,8);
y8 = sin(2*pi*t)./t;
plot(t,y8);
title('Subplot of y8');

subplot(5,2,9);
y9 = y1+y2+y3+y4+y5+y6+y7+y8;
plot(t,y9);
title('Subplot of y9');

%%%%%%%% Problem 2 %%%%%%%%

figure(2);
z = randn(401,1);
z = 0.1.*z;

subplot(5,2,1);
y10 = z';
plot(y10);
title('Subplot of y10');

subplot(5,2,2);
y11 = z'+t;
plot(y11);
title('Subplot of y11');

subplot(5,2,3);
y12 = z'+y1; 
plot(y12);
title('Subplot of y12');

subplot(5,2,4);
y13 = z'.*y1;
plot(y13);
title('Subplot of y13');

subplot(5,2,5);
y14 = t.*sin(2*pi*z');
plot(y14);
title('Subplot of y14');

subplot(5,2,6);
y15 = sin(2*pi*(t+z'));
plot(y15);
title('Subplot of y15');

subplot(5,2,7);
y16 = z'.*y2;
plot(y16);
title('Subplot of y16');

subplot(5,2,8);
y17 = sin(2*pi*(t+10*z'));
plot(y17);
title('Subplot of y17');

subplot(5,2,9);
y18 = y1./z';
plot(y18);
title('Subplot of y18');

subplot(5,2,10);
y19 = y11+y12+y13+y14+y15+y16+y17+y18;
plot(y19);
title('Subplot of y19');

%%%%%%%% Problem 3 %%%%%%%%

figure(3);

z = rand(401,1);
z = 0.1.*z;

subplot(5,2,1);
y20 = z;
plot(y20);
title('Subplot of y20');

subplot(5,2,2);
y21 = z'+t;
plot(y21);
title('Subplot of y21');

subplot(5,2,3);
y22 = z'+y1;
plot(y22);
title('Subplot of y22');

subplot(5,2,4);
y23 = z'.*y1;
plot(y23);
title('Subplot of y23');

subplot(5,2,5);
y24 = t.*sin(2*pi*z');
plot(y24);
title('Subplot of y24');

subplot(5,2,6);
y25 = sin(2*pi*(t+z'));
plot(y25);
title('Subplot of y25');

subplot(5,2,7);
y26 = z'.*y2;
plot(y26);
title('Subplot of y26');

subplot(5,2,8);
y27 = sin(2*pi*(t+10*z'));
plot(y27);
title('Subplot of y27');

subplot(5,2,9);
y28 = y1./z';
plot(y28);
title('Subplot of y28');

subplot(5,2,10);
y29 = y21+y22+y23+y24+y25+y26+y27+y28;
plot(y29);
title('Subplot of y29');

%%%%%%%% Problem 4 %%%%%%%%

figure(4);

subplot(1,4,1);
r1 = randn(5000,1);
histogram(r1);
title('Histogram of r1');

subplot(1,4,2);
r2 = 2*sqrt(2).*randn(5000,1);
histogram(r2);
title('Histogram of r2');

subplot(1,4,3);
r3 = 8.*randn(5000,1);
histogram(r3);
title('Histogram of r3');

subplot(1,4,4);
r4 = 16.*randn(5000,1);
histogram(r4);
title('Histogram of r4');

%%%%%%%% Problem 5 %%%%%%%%

figure(5);

subplot(1,4,1);
r6 = randn(5000,1) + 10;
histogram(r6);
title('Histogram of r6');

subplot(1,4,2);
r7 = 2.*randn(5000,1) + 20;
histogram(r7);
title('Histogram of r7');

subplot(1,4,3);
r8 = randn(5000,1) - 10;
histogram(r8);
title('Histogram of r8');

subplot(1,4,4);
r9 = 2.*randn(5000,1) - 20;
histogram(r9);
title('Histogram of r9');

%%%%%%%% Problem 6 %%%%%%%%

figure(6);

subplot(1,2,1);
r11 = 8.*rand(5000,1) - 4;
histogram(r11);
title('Histogram of r11');

subplot(1,2,2);
r21 = 40.*rand(5000,1) - 20;
histogram(r21);
title('Histogram of r21');

