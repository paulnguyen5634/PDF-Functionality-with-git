'''
Reads a desired folder of images, merges images into one pdf file
'''

import os
from PIL import Image
import re
from functions import folderfiles, tryint, alphanum_key, human_sort


# Creates folder if path is automatically made
def createFolder(img_path):
    try:
        if not os.path.exists(img_path):
            os.makedirs(img_path)
            print('Folder Created')
    except OSError:
        print('Error: Creating directory')


def image_to_pdf(img_folder, img_name, pdf_folder_path, i):
    '''
    Converts image into a pdf and saves it

    :param img_folder:
    :param img_name:
    :param pdf_folder_path:
    :param i:
    :return:
    '''
    img_path = os.path.join(img_folder, img_name)
    img = Image.open(img_path)
    im_1 = img.convert('RGB')

    # Now save that file into the Charity game v4 1 in the pdf_to_images section
    joined_PDFfile_path1 = os.path.join(pdf_folder_path, f'{i}.pdf')
    im_1.save(joined_PDFfile_path1)


def mergepdfs(path_fldr, desired_filename):
    '''

    :param path_fldr: path to the folder of individual pdfs
    :return:
    '''
    from PyPDF2 import PdfFileMerger

    merger = PdfFileMerger()
    list_of_files = os.listdir(path_fldr)
    human_sort(list_of_files)
    for file in list_of_files:
        loc = os.path.join(path_fldr, file)
        merger.append(loc)

    cwd = os.getcwd()
    save_location = os.path.join(cwd, 'pdf_not_translated', desired_filename+'.pdf')
    merger.write(save_location)
    merger.close()
    print('Pages Merged!')


def main():
    folder_name = 'ToDo'
    path_to_folder = folderfiles(folder_name)

    # getting name of folder
    pdf_name = path_to_folder.split('\\')[-1]
    print(pdf_name)

    # Retrieving the files for the folder of png's
    list_of_files = os.listdir(path_to_folder)
    human_sort(list_of_files)

    # This is for where to save the individual pdf files
    pdf_folder_path = os.path.join(path_to_folder, "pdf_not_translated")

    # create folder where pdf's will be saved (when images are converted from img to pdf)
    createFolder(pdf_folder_path)

    # iterating through list of images and converting them into pdf's
    i = 0
    for file in list_of_files:
        try:
            image_to_pdf(path_to_folder, file, pdf_folder_path, i)
            i+=1
        except PermissionError:
            break
    mergepdfs(pdf_folder_path, pdf_name)


if __name__ == '__main__':
    main()