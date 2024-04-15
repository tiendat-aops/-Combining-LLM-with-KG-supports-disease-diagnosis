import os
import fitz

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

files = os.listdir(data_path)

for file_name in files[:1]:
    file_path = os.path.join(data_path, file_name)
    doc = fitz.open(file_path)
    print(file_name)
    check_pages = int(doc.page_count / 3)
    for i in range(40):
        print(f'page {i}')
        fonts = doc.get_page_fonts(full=True, pno=i)
        for font in fonts:
            print(font[3])
