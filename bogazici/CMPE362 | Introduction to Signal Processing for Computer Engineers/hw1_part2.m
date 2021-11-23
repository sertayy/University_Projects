%%%%%%%% Problem 7 %%%%%%%%

figure(7);
subplot(1,3,1);
L = length(x);
plot(x);
S = fft(x);
f = (0:L-1)*(fs/L);     %frequency range
power = abs(S).^2/L;    %power
subplot(1,3,2);

plot(f,power);
Y = fftshift(S);
fshift = (-L/2:L/2-1)*(fs/L);
powershift = abs(Y).^2/L; 
subplot(1,3,3);
plot(fshift,powershift);

%%%%%%%% Problem 8 %%%%%%%%

figure(8);
[songy,songfs] = audioread('butterflyeffect.m4a');
plot(songy); %time domain graph
xlabel('Time');
ylabel('Signal');
songy1 = songy(:,1);
songy2 = songy(:,2);
songY = fft(songy1);
songl = length(songy1);

figure(9);
songY0 = fftshift(songY);
songf0 = (-songl/2:songl/2-1)*(songfs/songl);
songpower0 = abs(songY0).^2/songl;
plot(songf0,songpower0); %frequency domain graph
xlabel('Frequency');
ylabel('Power');
xlim([-5000 5000]);

%%%%%%%% Problem 9 %%%%%%%%

RGB = imread('lena.png');
I = rgb2gray(RGB);
meanval = mean(I, 'all');   %finding mean value

maxval=max(I(:));   %finding max value
[row_max, col_max] = find(ismember(I, max(I(:))));

minval=min(I(:));   %finding min value
[row_min, col_min] = find(ismember(I, min(I(:))));

I = double(I(:));   %finding standard deviation
stddev = std(I);
