# apply_patch.py
import json
from pathlib import Path
import shutil
import sys

from hdiffpatch_utils import run_hpatchz


MANIFEST_NAME = "manifest.json"
BACKUP_SUFFIX = ".backup_before_patch"


def print_header(title):
    print("=" * 60)
    print(f"== {title.center(54)} ==")
    print("=" * 60)
    print()


def pause_and_exit(exit_code=0):
    print("\n按 Enter 键退出...")
    try:
        input()
    except EOFError:
        pass
    sys.exit(exit_code)


def sha256_of_file(file_path):
    import hashlib

    hasher = hashlib.sha256()
    with open(file_path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ensure_parent_dir(file_path):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def load_manifest(patch_dir):
    manifest_path = patch_dir / MANIFEST_NAME
    if not manifest_path.exists():
        print(f"错误: 未找到补丁清单文件 '{manifest_path}'")
        pause_and_exit(1)

    with open(manifest_path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def apply_binary_patch(old_file_path, patch_file_path, output_file_path):
    ensure_parent_dir(output_file_path)
    run_hpatchz(old_file_path, patch_file_path, output_file_path)


def create_backup(target_path):
    backup_path = target_path.with_name(target_path.name + BACKUP_SUFFIX)
    if backup_path.exists():
        backup_path.unlink()
    shutil.copy2(target_path, backup_path)
    return backup_path


def restore_backup(backup_path, target_path):
    shutil.copy2(backup_path, target_path)


def main():
    print_header("整包自动补丁应用脚本")

    base_dir = Path.cwd()
    patch_dir = base_dir / "Patch"

    if not patch_dir.exists():
        print(f"错误: 当前目录下未找到 Patch 文件夹: {patch_dir}")
        print("请把 Patch 文件夹复制到旧版本根目录后，再双击运行 apply_patch.py / apply_patch.exe。")
        pause_and_exit(1)

    manifest = load_manifest(patch_dir)

    changed = manifest.get("changed", [])
    added = manifest.get("added", [])
    deleted = manifest.get("deleted", [])

    print(f"检测到补丁内容: 变更 {len(changed)}，新增 {len(added)}，删除 {len(deleted)}")

    for item in changed:
        relative_path = item["path"]
        target_path = base_dir / Path(relative_path)
        patch_file = patch_dir / Path(item["patch_file"])

        if not target_path.exists():
            print(f"错误: 缺少需要打补丁的旧文件: {target_path}")
            pause_and_exit(1)

        current_hash = sha256_of_file(target_path)
        expected_hash = item["old_sha256"]
        if current_hash != expected_hash:
            print(f"错误: 文件校验不匹配，无法应用补丁: {relative_path}")
            print(f"- 当前 SHA256: {current_hash}")
            print(f"- 预期 SHA256: {expected_hash}")
            pause_and_exit(1)

        backup_path = create_backup(target_path)
        print(f"[变更] {relative_path}")
        print(f"  已备份到: {backup_path.name}")
        apply_binary_patch(backup_path, patch_file, target_path)

        new_hash = sha256_of_file(target_path)
        if new_hash != item["new_sha256"]:
            print(f"错误: 补丁应用后校验失败: {relative_path}")
            restore_backup(backup_path, target_path)
            print("已自动恢复原始文件。")
            pause_and_exit(1)

    for item in added:
        relative_path = item["path"]
        source_file = patch_dir / Path(item["file"])
        target_path = base_dir / Path(relative_path)
        print(f"[新增] {relative_path}")
        ensure_parent_dir(target_path)
        shutil.copy2(source_file, target_path)

        new_hash = sha256_of_file(target_path)
        if new_hash != item["new_sha256"]:
            print(f"错误: 新增文件校验失败: {relative_path}")
            pause_and_exit(1)

    for item in deleted:
        relative_path = item["path"]
        target_path = base_dir / Path(relative_path)
        if target_path.exists():
            backup_path = create_backup(target_path)
            print(f"[删除] {relative_path}")
            print(f"  已备份到: {backup_path.name}")
            target_path.unlink()

    print()
    print("整包补丁应用完成！")
    print("如果需要回滚，可使用同目录下的 rollback_patch.exe 恢复。")
    pause_and_exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n发生未预料错误: {exc}")
        import traceback

        traceback.print_exc()
        pause_and_exit(1)