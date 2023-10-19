
import os
from functions import createFolder, folderfiles, percentage_calculator, start_timer, end_timer, progress_percentage
from functions import human_sort, alphanum_key, tryint
import fitz
import cv2
import os
from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
from deep_translator import GoogleTranslator, single_detection
from pdf2image import convert_from_path
import easyocr
import math


def convert_pdf_to_image(fic, filename, folder_name):
    '''
    Splits a pdf into individual images

    :param fic: string path to the pdf to be split
    :param filename: name of file that will be split
    :param folder_name: name of folder in which images will be saved
    :return:
    '''
    print("\nSplitting PDF...\n")
    start_time = datetime.now()
    if fic.endswith('pdf'):
        # open your file
        doc = fitz.open(fic)
        # iterate through the pages of the document and create a RGB image of the page
        for page in doc:
            dim = page.get_pixmap()

            if dim.width < 2880:
                zoom = 2880 / (dim.width)
                # zoom = 4    # zoom factor
                mat = fitz.Matrix(zoom, zoom)
                # pix = page.getPixmap(matrix = mat, <...>)
                pix = page.get_pixmap(matrix=mat)

                pix.save(f"{folder_name}\\{filename}\%i.png" % page.number)

                #pix.save(f"{filename}\%i.png" % page.number)
            else:
                pix = page.get_pixmap()
                # Save individual images to folder of same name as pdf name
                pix.save(f"{folder_name}\\{filename}\%i.png" % page.number)
                #pix.save(f"{filename}\%i.png" % page.number)

        print('PDF has been converted')
    elif fic.endswith('mp4'):
        # Read the video from specified path
        cam = cv2.VideoCapture(fic)
        currentframe = 0

        while (True):

            # reading from frame
            ret, frame = cam.read()

            if ret:
                # if video is still left continue creating images
                name = f'./{filename}/{currentframe}.png'
                print('Creating...' + name)

                # writing the extracted images
                cv2.imwrite(name, frame)

                # increasing counter so that it will
                # show how many frames are created
                currentframe += 1
            else:
                break

        cam.release()
        cv2.destroyAllWindows()

    end_time = datetime.now()
    fin_time = str(end_time - start_time)
    a = datetime.strptime(fin_time, "%H:%M:%S.%f")
    print(f'It took {a.hour} hrs, {a.minute} mins, {a.second} seconds, {a.microsecond} microseconds to finish')


def translate_images(untranslated_pdf_folder, pdf_being_split_name):
    '''
    Goes to untranslated pdf and returns a translated pdf

    :param untranslated_pdf_folder: path to untranslated pdf
    :param pdf_being_split_name: string name of pdf being split
    :return: translated pdf located in 'Finished_pdf' folder in the same directory as program
    '''
    path_to_imagefldr = os.path.join(untranslated_pdf_folder, pdf_being_split_name)
    path_to_translatedIMGS = os.path.join(path_to_imagefldr, 'translated_imges')
    createFolder(path_to_translatedIMGS)

    list_of_imgs = os.listdir(path_to_imagefldr)

    # % number we want
    increment = 0.05
    len_pdf = len(list_of_imgs)
    j = 0

    print("\nTranslating PDF...\n")
    for file in list_of_imgs:
        # Main images
        if file[-4:] == '.png' or file[-4:] == '.jpg':
            # print(file)
            if os.path.basename(os.path.join(path_to_imagefldr, file)) == '0.png':
                mang_page = path_to_imagefldr + '\\' + file
                with Image.open(mang_page) as im:

                    if im.mode == 'RGBA':
                        im = im.convert('RGB')

                    increment = progress_percentage(len_pdf, increment, j)
                    j += 1
                    translated_pdf_path = os.path.join(path_to_translatedIMGS, file[:-4] + '.pdf')
                    im.save(translated_pdf_path)
            else:
                mang_page = path_to_imagefldr + '\\' + file
                in_line = True
                reader = easyocr.Reader(['ch_sim'], gpu=True)
                results = reader.readtext(mang_page, paragraph=in_line)

                with Image.open(mang_page) as im:
                    for i in range(len(results)):
                        try:
                            captured_text = results[i][1]
                            if len(captured_text) == 1:
                                continue
                            translated = GoogleTranslator(
                                source='chinese (simplified)',
                                target='english').translate(captured_text)
                            # Height and Weidth
                            height = abs(results[i][0][1][1] - results[i][0][2][1])
                            width = abs(results[i][0][0][0] - results[i][0][1][0])

                            # TopLeft and BottomRight Coordinates of rectangle to be drawn
                            topLeft_X = results[i][0][0][0]
                            topLeft_Y = results[i][0][0][1]

                            botRight_X = results[i][0][2][0]
                            botRight_Y = results[i][0][2][1]

                            selected_size = 0

                            draw = ImageDraw.Draw(im)
                            draw.rectangle((topLeft_X, topLeft_Y, botRight_X, botRight_Y), fill='white')
                        except:
                            continue
                        for size in range(1, 500):
                            try:
                                font = ImageFont.truetype(
                                    font="font\\CC Wild Words Roman.ttf",
                                    size=size)

                                text = translated

                                textBox_singlelined = font.getbbox(text)

                                single_Length = abs(textBox_singlelined[0] - textBox_singlelined[2])
                                avg_char_width_using_getbbox = single_Length / len(text)

                                max_char_count_Using_getbbox = int((width * .95) / avg_char_width_using_getbbox)

                                text_wrapped = textwrap.fill(text=text, width=max_char_count_Using_getbbox)

                                current_lines = math.ceil(len(text) / max_char_count_Using_getbbox)

                                textBox_multilined = draw.multiline_textbbox(
                                    xy=(im.size[0] / 2, im.size[1] / 2),
                                    text=text_wrapped,
                                    font=font,
                                    anchor='mm',
                                    align='center')
                                #print(textBox_multilined)

                                Multi_Length = abs(textBox_multilined[0] - textBox_multilined[2])
                                Multi_Height = abs(textBox_multilined[1] - textBox_multilined[3])

                                height_PerLine = Multi_Height / current_lines

                                if Multi_Length > width * .7 and Multi_Height > height * .9:
                                    break

                                selected_size += 1
                            except:
                                break
                        try:
                            font = ImageFont.truetype(
                                font="font\\CC Wild Words Roman.ttf",
                                size=selected_size)

                            textBox_singlelined = font.getbbox(translated)

                            single_Length = abs(textBox_singlelined[0] - textBox_singlelined[2])
                            avg_char_width_using_getbbox = single_Length / len(translated)

                            max_char_count_Using_getbbox = int((width * .95) / avg_char_width_using_getbbox)

                            text_wrapped = textwrap.fill(text=translated, width=max_char_count_Using_getbbox)
                            draw.text(
                                xy=((results[i][0][0][0] + results[i][0][1][0]) / 2,
                                    (results[i][0][0][1] + results[i][0][2][1]) / 2),
                                text=text_wrapped,
                                font=font,
                                fill='black',
                                anchor='mm',
                                align='center')
                        except:
                            continue
                    # Prints percentage of files that are complete
                    increment = progress_percentage(len_pdf, increment, j)
                    j += 1
                    translated_pdf_path = os.path.join(path_to_translatedIMGS, file[:-4] + '.pdf')
                    im.save(translated_pdf_path)

        elif file[-4:] != '.png' or file[-4:] == '.jpg':
            continue

        else:
            # Base Image
            mang_page = path_to_imagefldr + '\\' + file

            with Image.open(mang_page) as im:
                # Prints percentage of files that are complete
                increment = progress_percentage(len_pdf, increment, j)
                j += 1
                if im.mode == 'RGBA':
                    im = im.convert('RGB')

                translated_pdf_path = os.path.join(path_to_translatedIMGS, file[:-4] + '.pdf')
                im.save(translated_pdf_path)


def mergepdfs(path_fldr, desired_filename):
    '''

    :param path_fldr: path to the folder of individual pdfs
    :param desired_filename: string name of pdf
    :return:
    '''
    from PyPDF2 import PdfFileMerger

    merger = PdfFileMerger()
    list_of_files = os.listdir(path_fldr)
    human_sort(list_of_files)

    i=0
    for file in list_of_files:
        loc = os.path.join(path_fldr, file)
        merger.append(loc)
        i+=1
        '''if i == 5:
            break'''

    cwd = os.getcwd()
    save_location = os.path.join(cwd, 'Finished_pdf', desired_filename+'.pdf')
    merger.write(save_location)
    merger.close()
    print('Pages Merged!')


def main():

    # This is where we will look to find pdf's to translate
    cwd = os.getcwd()
    untranslated_pdf_folder = 'pdf_not_translated'
    path_to_imagefldr = os.path.join(cwd, untranslated_pdf_folder)

    # Path to pdf to be converted
    pdf_path = folderfiles(untranslated_pdf_folder)

    # Removes '.pdf' to create a new folder
    createFolder(pdf_path[:-4])

    filename = os.path.basename(pdf_path)[:-4]
    convert_pdf_to_image(pdf_path, filename, untranslated_pdf_folder)

    start_time = time.time()

    translate_images(path_to_imagefldr, filename)

    folder_of_pdfs = os.path.join(cwd, 'pdf_not_translated', filename, 'translated_imges')
    mergepdfs(folder_of_pdfs, filename)

    # Record the end time
    end_time = time.time()
    # Calculate the elapsed time in seconds
    elapsed_time = end_time - start_time
    # Convert seconds to minutes and seconds
    minutes, seconds = divmod(elapsed_time, 60)

    # Print the elapsed time nicely
    print(f"The code took {int(minutes)} minutes and {seconds:.2f} seconds to run.")

if __name__ == '__main__':
    main()