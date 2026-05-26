"""
文件解密工具

用于解密被公司加密软件加密的文本文件。
原理：利用加密软件不处理 .exe 文件的特性进行解密。

使用方式：
    python file_decrypt.py "path/to/file.txt"           # 解密单个文件
    python file_decrypt.py "path/to/folder"              # 解密整个目录
    python file_decrypt.py "path1" "path2" "path3"       # 解密多个路径
"""

import os
import sys
import stat
import ctypes
from typing import Optional


SKIP_EXTENSIONS = {'.exe', '.dll'}

_INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
_FILE_ATTRIBUTE_READONLY = 0x1


# ── 只读属性处理 (Win32 + POSIX) ──────────────────────────────

def _win_file_attrs(path: str):
    if sys.platform != 'win32':
        return None
    attrs = ctypes.windll.kernel32.GetFileAttributesW(os.fsdecode(path))
    return None if attrs == _INVALID_FILE_ATTRIBUTES else attrs


def _clear_readonly(path: str):
    """
    清除只读属性。
    返回 (original_mode, had_win_ro, should_restore)。
    """
    original_mode = os.stat(path).st_mode
    had_win_ro = False

    if sys.platform == 'win32':
        wa = _win_file_attrs(path)
        if wa is not None and (wa & _FILE_ATTRIBUTE_READONLY):
            had_win_ro = True
            p = os.fsdecode(path)
            if ctypes.windll.kernel32.SetFileAttributesW(p, wa & ~_FILE_ATTRIBUTE_READONLY):
                print(f"  解除只读(Windows): {path}")
            else:
                print(f"  警告: Windows 只读未能解除: {path}")

    posix_ro = not (original_mode & stat.S_IWRITE)
    if posix_ro:
        os.chmod(path, original_mode | stat.S_IWRITE)
        print(f"  解除只读: {path}")

    return original_mode, had_win_ro, had_win_ro or posix_ro


def _restore_readonly(path: str, original_mode: int, had_win_ro: bool, should_restore: bool):
    """恢复只读属性。"""
    if not should_restore:
        return
    try:
        os.chmod(path, original_mode)
    except OSError:
        pass
    if had_win_ro:
        try:
            wa = _win_file_attrs(path)
            if wa is not None:
                ctypes.windll.kernel32.SetFileAttributesW(
                    os.fsdecode(path), wa | _FILE_ATTRIBUTE_READONLY
                )
        except Exception:
            pass
    print(f"  恢复只读: {path}")


# ── 安全写入 ──────────────────────────────────────────────────

def _write_bytes_exact(path: str, data: bytes):
    """写入并校验：flush → fsync → 大小比对。"""
    with open(path, 'wb') as f:
        f.write(data)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    actual = os.path.getsize(path)
    if actual != len(data):
        raise OSError(
            f"写入不完整: {path} (期望 {len(data)} 字节, 实际 {actual})"
        )


# ── 单文件解密 ────────────────────────────────────────────────

def decrypt_file(file_path: str) -> bool:
    """
    解密单个文件。
    - 先解除只读 → 读内容 → 写临时 .exe → os.replace 原子替换 → 恢复只读
    - 失败时保证源文件不被破坏
    """
    if not os.path.isfile(file_path):
        print(f"[FAIL] 文件不存在: {file_path}")
        return False

    temp_exe_path = file_path + '.exe'
    while os.path.exists(temp_exe_path):
        temp_exe_path += '.exe'

    file_mode = None
    had_win_ro = False
    should_restore = False

    try:
        file_mode, had_win_ro, should_restore = _clear_readonly(file_path)

        with open(file_path, 'rb') as f:
            content = f.read()

        _write_bytes_exact(temp_exe_path, content)

        os.replace(temp_exe_path, file_path)

    except Exception as e:
        print(f"[FAIL] 解密失败: {file_path}")
        print(f"  错误: {e}")
        if os.path.exists(file_path) and os.path.exists(temp_exe_path):
            try:
                os.remove(temp_exe_path)
                print(f"  已清理临时文件: {temp_exe_path}")
            except Exception:
                pass
        elif not os.path.exists(file_path) and os.path.exists(temp_exe_path):
            print(f"  警告: 数据保留在临时文件中: {temp_exe_path}")
        if should_restore and file_mode is not None:
            try:
                if os.path.exists(file_path):
                    _restore_readonly(file_path, file_mode, had_win_ro, True)
            except Exception:
                pass
        return False

    if should_restore and file_mode is not None:
        try:
            _restore_readonly(file_path, file_mode, had_win_ro, True)
        except Exception:
            print(f"  警告: 无法恢复只读属性: {file_path}")

    print(f"[OK] 解密成功: {file_path}")
    return True


# ── 目录解密 ──────────────────────────────────────────────────

def decrypt_directory(dir_path: str, skip_extensions: Optional[set] = None) -> dict:
    if skip_extensions is None:
        skip_extensions = SKIP_EXTENSIONS

    result = {'success': 0, 'failed': 0, 'skipped': 0}
    current_script = os.path.abspath(__file__)

    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            if os.path.abspath(file_path) == current_script:
                print(f"[SKIP] {file_path} (脚本自身)")
                result['skipped'] += 1
                continue

            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in skip_extensions:
                print(f"[SKIP] {file_path} ({file_ext})")
                result['skipped'] += 1
                continue

            if decrypt_file(file_path):
                result['success'] += 1
            else:
                result['failed'] += 1

    return result


# ── 路径自动分发 ──────────────────────────────────────────────

def decrypt_path(path: str) -> dict:
    result = {'success': 0, 'failed': 0, 'skipped': 0}

    if os.path.isfile(path):
        file_ext = os.path.splitext(path)[1].lower()
        if file_ext in SKIP_EXTENSIONS:
            print(f"[SKIP] {path} ({file_ext})")
            result['skipped'] = 1
        elif decrypt_file(path):
            result['success'] = 1
        else:
            result['failed'] = 1
    elif os.path.isdir(path):
        result = decrypt_directory(path)
    else:
        print(f"[FAIL] 路径不存在: {path}")
        result['failed'] = 1

    return result


# ── CLI 入口 ──────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("File Decrypt Tool")
        print("=" * 50)
        print("Usage: python file_decrypt.py <path1> [path2] ...")
        print()
        print("Examples:")
        print('  python file_decrypt.py "D:\\Code\\file.txt"')
        print('  python file_decrypt.py "D:\\Code\\project"')
        print('  python file_decrypt.py "file1.txt" "folder1" "file2.txt"')
        print()
        print(f"自动跳过的扩展名: {', '.join(sorted(SKIP_EXTENSIONS))}")
        sys.exit(1)

    paths = sys.argv[1:]

    print("=" * 60)
    print("开始解密...")
    print("=" * 60)

    total = {'success': 0, 'failed': 0, 'skipped': 0}

    for path in paths:
        print(f"\n处理: {path}")
        print("-" * 40)
        result = decrypt_path(path)
        total['success'] += result['success']
        total['failed'] += result['failed']
        total['skipped'] += result['skipped']

    print()
    print("=" * 60)
    print("解密完成！")
    print(f"  成功: {total['success']} 个文件")
    print(f"  失败: {total['failed']} 个文件")
    print(f"  跳过: {total['skipped']} 个文件")
    print("=" * 60)

    sys.exit(0 if total['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
