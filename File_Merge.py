FileName    = r'Viwer'
Ftype       = '7z'
Size        = 50 * 1024 *1024
path        = f'{FileName}.{Ftype}'
i=1

with open (path, 'wb') as file:
    while True:
        with open (f'New_{i}.bin','rb') as rfile:
            data=rfile.read()
        file.write(data)
        print(data)
        i+=1

