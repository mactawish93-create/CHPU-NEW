import base64

# Открываем вашу картинку логотипа
with open("logo.png", "rb") as image_file:
    # Кодируем её в текстовую строку
    base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    
# Сохраняем получившийся длинный текст в файл, чтобы скопировать
with open("string_code.txt", "w") as text_file:
    text_file.write(base64_string)

print("Текст для вставки успешно сохранен в файл string_code.txt!")
