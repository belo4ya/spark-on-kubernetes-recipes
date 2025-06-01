#!/usr/bin/env python3
import sys
import os
import stat
import pwd
import grp
import datetime

def format_mode(mode):
    return stat.filemode(mode)

def format_mtime(epoch_secs):
    dt = datetime.datetime.fromtimestamp(epoch_secs)
    return dt.strftime("%b %d %H:%M")

def ls_la(path):
    try:
        entries = os.listdir(path)
    except FileNotFoundError:
        print(f"Ошибка: директория «{path}» не найдена")
        sys.exit(1)
    except NotADirectoryError:
        print(f"Ошибка: «{path}» не является директорией")
        sys.exit(1)
    except PermissionError:
        print(f"Ошибка: нет прав доступа к «{path}»")
        sys.exit(1)

    # Включаем скрытые файлы (os.listdir уже возвращает их)
    for name in sorted(entries):
        full = os.path.join(path, name)
        try:
            st = os.lstat(full)
        except OSError as e:
            print(f"Не удалось прочитать «{name}»: {e}")
            continue

        mode = format_mode(st.st_mode)
        nlink = st.st_nlink
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        size = st.st_size
        mtime = format_mtime(st.st_mtime)

        print(f"{mode} {nlink:3} {owner:8} {group:8} {size:8} {mtime} {name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Использование: {sys.argv[0]} <путь_к_директории>")
        sys.exit(1)

    directory = sys.argv[1]
    ls_la(directory)
