import sys
import os
import shutil
import glob
from pathlib import Path

# Constants
IMAGES = 'images'
VIDEOS = 'videos'
DOCUMENTS = 'documents'
AUDIO = 'audio'
ARCHIVES = 'archives'
FILES_ACCORDING_CATEGORY = 'files_according_category'
KNOWN_EXTENSIONS = 'known_extensions'
UNKNOWN_EXTENSIONS = 'unknown_extensions'
UNKNOWN = 'unknown'
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ~`!@#$%^&*()-=+<>?\",.\'\\[]{}№;/:| "
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g", "_", "_", "_", "_", "_", "_",
                "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_",
                "_", "_", "_", "_", "_", "_", "")
TRANSLATE_DICT = {}  

result = {
    FILES_ACCORDING_CATEGORY: {
        IMAGES: [],
        VIDEOS: [],
        DOCUMENTS: [],
        AUDIO: [],
        ARCHIVES: [],
        UNKNOWN: []
    },
    KNOWN_EXTENSIONS: [],
    UNKNOWN_EXTENSIONS: []
}

sort_folders = {
    IMAGES: ['JPEG', 'PNG', 'JPG', 'SVG'],
    VIDEOS: ['AVI', 'MP4', 'MOV', 'MKV'],
    DOCUMENTS: ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
    AUDIO: ['MP3', 'OGG', 'WAV', 'AMR'],
    ARCHIVES: ['ZIP', 'GZ', 'TAR']
}


def translate_dict_create():
    for c , t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANSLATE_DICT[ord(c)] = t
        TRANSLATE_DICT[ord(c.upper())] = t.upper()


def normalize(file_name):
    return file_name.translate(TRANSLATE_DICT)


def create_folders(path, folder):
    if not os.path.exists(path+folder):
        os.makedirs(path+folder)


def rename_file(path, file_name, file_extension):
    file_spl = file_name.removesuffix('.'+file_extension)
    renamed_fname = normalize(file_spl)
    new_fname = renamed_fname+'.'+file_extension
    os.rename(path+file_name, path+new_fname)
    #print('Symbols of file name isn\'t cyrillic')
    return new_fname
  

def archive_process(main_patn, path, fname):
    unpack_folder = fname.split('.')
    try:
        shutil.unpack_archive(path+fname, main_patn+unpack_folder[0])
        os.remove(path+fname)
    except:
        print(f'Сouldn\'t open the archive - {path+fname}')
        os.remove(path+fname)
    

def sort_files(MAIN_PATH_SORT, path, file_name, file_extension):
    moved = 0
    renamed_fname = rename_file(path, file_name, file_extension)
    for folder, extensions in sort_folders.items():
            if str(file_extension).lower() in str(extensions).lower():
                create_folders(MAIN_PATH_SORT, folder)
                result[FILES_ACCORDING_CATEGORY][folder].append(renamed_fname)
                if not file_extension in result[KNOWN_EXTENSIONS]:
                    result[KNOWN_EXTENSIONS].append(file_extension)
                # Archive processing
                if folder == ARCHIVES:
                    archive_process(MAIN_PATH_SORT+folder+'/', path, renamed_fname)
                    moved = 1
                    break
                shutil.move(path+renamed_fname, MAIN_PATH_SORT+folder+'/'+renamed_fname)
                moved = 1
                break
    if moved == 0:
        create_folders(MAIN_PATH_SORT, UNKNOWN)
        result[FILES_ACCORDING_CATEGORY][UNKNOWN].append(renamed_fname)
        if not file_extension in result[UNKNOWN_EXTENSIONS]:
            result[UNKNOWN_EXTENSIONS].append(file_extension)
        shutil.move(path+renamed_fname, MAIN_PATH_SORT+UNKNOWN+'/'+renamed_fname)


def folders_iteration(MAIN_PATH_SORT, path):
    p = Path(path)
    list_files_for_remove = []
    for i in p.glob('**/*'):
        except_url = str(i).replace('\\', '/')
        if i.is_dir() and (len(os.listdir(str(i))) == 0):
            i.rmdir()
            continue

        if (i.is_file() and except_url.find(MAIN_PATH_SORT+IMAGES) < 0 and except_url.find(MAIN_PATH_SORT+VIDEOS) < 0 
            and except_url.find(MAIN_PATH_SORT+DOCUMENTS) < 0 and except_url.find(MAIN_PATH_SORT+AUDIO) < 0
            and except_url.find(MAIN_PATH_SORT+ARCHIVES) < 0 and except_url.find(MAIN_PATH_SORT+UNKNOWN) < 0):
            file_array = i.name.split('.')
            files_path = str(i.parent)+'\\'
            sort_files(MAIN_PATH_SORT, files_path, i.name, file_array[-1])

            folder_path = str(i.parent)+'\\*.*'
            if len(glob.glob(folder_path))  == 0:
                list_files_for_remove.append(files_path)

    # Remove empty folders
    for fold in list_files_for_remove:
        if os.path.exists(fold):
            shutil.rmtree(fold)


def main(path):
    MAIN_PATH_SORT = path
    print(path)
    translate_dict_create()
    folders_iteration(MAIN_PATH_SORT,path)

    print(result)
    return result


if __name__ == '__main__':
    #main(sys.argv[1])
    main('d:/temp/temp/ds/')