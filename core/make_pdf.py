from PyPDF2 import PdfFileWriter, PdfFileReader
import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# path = os.path.join('/Users/admin/Desktop/API_ENV/ecommerce/pdf_files' + '/example.pdf')

# PWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PWD = "/Users/admin/Desktop/API_ENV/ecommerce/pdf_files"


def write_new_pdf(filename, data={}):

    path = os.path.join(PWD + "/" + str(filename) + ".pdf")

    if data:
        with open(path, "a+", encoding="utf-8") as pdf:
            for key, value in data.items():
                pdf.write(key + " : " + value + "\n ")
    else:
        print("sorry No Data")


n = {"thomas": "3", "adel": "5", "saeed": "10"}
write_new_pdf("example", n)

