'''
Reads a locked pdf file and unlocks it given a txt file containing the password.
txt file needs to be the same name as the pdf being unlocked
'''

import pikepdf
from functions import folderfiles
import os


def main():
    folder_name = 'locked_pdfs'
    locked_pdf_path = folderfiles(folder_name)

    # Keeping only the name of the file and removing '.pdf' from remaining string
    pdf_name = locked_pdf_path.split('\\')[-1]
    pdf_name = pdf_name[:-4]

    #Extracting text file name
    txt_name = pdf_name + '.txt'
    txt_path = os.path.join(folder_name, txt_name)

    with open(txt_path, 'r') as file:
        # Read the content of the file
        pdf_pass = file.read()

    pdf = pikepdf.open(locked_pdf_path, password=pdf_pass)

    print("\nProcessing...")

    folder_to_save = 'pdf_not_translated'
    pdf.save(folder_to_save + '\\' + pdf_name + '.pdf')

    print("Password successfully removed from the PDF")


if __name__ == '__main__':
    main()

