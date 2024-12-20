file_path = './profiles/Test4/current_save.sav'

def remove_last_16_bytes(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    
    new_data = data[:-16]
    
    with open(file_path + 'new', 'wb') as file:
        file.write(new_data)

remove_last_16_bytes(file_path)
