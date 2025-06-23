% Set IP address and port
ip_address = '192.168.0.100';  % Change to your instrument's IP
port = 5025;                   % SCPI port for LAN

% Create TCP/IP object
fs = tcpip(ip_address, port);
fs.InputBufferSize = 100000;  % Large enough to handle trace data
fs.Terminator = 'LF';         % Linefeed termination
fopen(fs);

% Identify instrument
fprintf(fs, '*IDN?');
idn = fscanf(fs);
disp(['Instrument ID: ', idn]);

% Stop continuous sweep and trigger single sweep
fprintf(fs, 'INIT:CONT OFF');
fprintf(fs, 'INIT;*WAI');

% Get frequency range and point count
fprintf(fs, 'SENS:FREQ:STAR?'); start_freq = str2double(fscanf(fs));
fprintf(fs, 'SENS:FREQ:STOP?'); stop_freq = str2double(fscanf(fs));
fprintf(fs, 'SWE:POIN?');       points = str2double(fscanf(fs));

% Get trace data
fprintf(fs, 'TRAC? TRACE1');
raw_data = fscanf(fs);
data = str2double(strsplit(strtrim(raw_data), ','));

% Frequency axis
freq_axis = linspace(start_freq, stop_freq, points);

% Plot
figure;
plot(freq_axis, data, 'b-', 'LineWidth', 1.5);
xlabel('Frequency (Hz)');
ylabel('Amplitude (dBm)');
title('R&S FSV Trace Data via LAN');
grid on;

% Save to CSV
trace_matrix = [freq_axis(:), data(:)];
csvwrite('fsv_trace_data.csv', trace_matrix);

% Clean up
fclose(fs);
delete(fs);
clear fs;
