import re
from pathlib import Path
import shutil

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
    "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g"
)


TRANS = {}
for cyr, lat in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyr)] = lat

for cyr, lat in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyr.upper())] = lat.upper()


def normalize(name: str) -> str:
    t_name = name.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)
    return t_name


def handle_media(file_name: Path, target_folder: Path, category_files):
    target_folder.mkdir(exist_ok=True, parents=True)
    new_name = normalize(file_name.stem) + file_name.suffix
    new_file_path = target_folder / new_name
    file_name.replace(new_file_path)
    category_files.append(new_file_path)


def handle_archive(file_name: Path, target_folder: Path, category_files):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(file_name.stem)
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(file_name), str(folder_for_file))
        file_name.unlink()
        category_files.append(folder_for_file)
    except shutil.ReadError:
        print(f'It is not a valid archive: {file_name}')
        folder_for_file.rmdir()


def handle_folder(path: Path, category_files, known_extensions, unknown_extensions):
    for item in path.iterdir():
        if item.is_dir() and item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'others'):
            handle_folder(item, category_files, known_extensions, unknown_extensions)
            if not any(item.iterdir()):
                item.rmdir()
        else:
            handle_file(item, path, category_files, known_extensions, unknown_extensions)


def handle_file(file_name: Path, path: Path, category_files, known_extensions, unknown_extensions):
    EXTENSIONS = {
        'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
        'video': ['AVI', 'MP4', 'MOV', 'MKV'],
        'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
        'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
        'archives': ['ZIP', 'GZ', 'TAR']
    }

    file_ext = file_name.suffix[1:].upper()
    known = False
    for category, extensions in EXTENSIONS.items():
        if file_ext in extensions:
            handle_media(file_name, path / category, category_files[category])
            known_extensions.add(file_ext)
            known = True
            break
    if not known:
        if file_ext in EXTENSIONS['archives']:
            handle_archive(file_name, path / 'archives', category_files['archives'])
            known_extensions.add(file_ext)
        else:
            handle_media(file_name, path / 'others', category_files['others'])
            unknown_extensions.add(file_ext)


def sort_folder(folder: Path):
    category_files = {
        'images': [],
        'video': [],
        'documents': [],
        'audio': [],
        'archives': [],
        'others': []
    }
    known_extensions = set()
    unknown_extensions = set()
    handle_folder(folder, category_files, known_extensions, unknown_extensions)

    print_results(category_files, known_extensions, unknown_extensions)


def print_results(category_files, known_extensions, unknown_extensions):
    print("List of files in each category:")
    for category, files in category_files.items():
        print(f"\n{category.capitalize()}:")
        for file in files:
            print(f"  {file}")

    print("\nList of all known extensions:")
    print(", ".join(sorted(known_extensions)))

    print("\nList of all unknown extensions:")
    print(", ".join(sorted(unknown_extensions)))


def main(folder_path):
    folder = Path(folder_path)

    if not folder.is_dir():
        print(f"{folder} is not a directory")
        return

    sort_folder(folder)


if __name__ == "__main__":
    folder_path = input("Enter the path to the folder for sorting: ")
    main(folder_path)
