from PyPDF2 import PdfReader

reader = PdfReader('fed-zakon-615-29122022.pdf')

print(len(reader.pages))

page = reader.pages[0]

text = page.extract_text()
print(text)

with open('data.txt', 'w') as out:
    out.write(text)