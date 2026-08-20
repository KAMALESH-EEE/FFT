FileName    = r'C:\Users\KAMALESH\OneDrive\Documents\FFT\FreeCAD_1.1.3-Windows-x86_64-py311'
Ftype       = '7z'
Size        = 50 * 1024 *1024
path        = f'{FileName}.{Ftype}'
i=1

with open (path, 'rb') as file:
    while True:
        data = file.read(Size)
        print(data)
        if len(data) == 0:
            print(i,'\n\n')
            break

        with open (f'New_{i}.bin','wb') as wfile:
            wfile.write(data)
        i+=1

