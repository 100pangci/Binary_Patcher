# Binary Patcher

这是一个用于生成和应用二进制补丁的 Windows 友好项目，并支持整目录补丁工作流。

## 目录结构

```text
.
├─ .github/workflows/      # GitHub Actions 自动构建
├─ scripts/                # Windows 批处理与构建脚本
├─ src/                    # Python 源码
├─ .gitignore
├─ pyproject.toml
├─ requirements.txt
└─ requirements-build.txt
```

## 主要文件说明

- `src/binary_patcher.py`：核心命令行工具
- `src/apply_patch.py`：面向最终用户的自动补丁脚本
- `scripts/build.py`：统一构建与发布整理脚本
- `scripts/build.bat`：Windows 下一键构建入口

## 本地使用

### 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### 整目录补丁工作流

首次运行：

```powershell
python src/binary_patcher.py
```

程序会自动创建：

- `Old/`
- `New/`
- `Patch/`

然后你只需要：

1. 把旧版完整目录放进 `Old/`
2. 把新版完整目录放进 `New/`
3. 再次运行 `python src/binary_patcher.py`

程序会先计算 SHA256，再按相同相对路径找出变更、新增、删除文件，并在 `Patch/` 中生成：

- `manifest.json`
- 与原目录结构一致的 `*.patch`
- 对新增文件生成 `*.new`
- 自动复制 `apply_patch.py`

### 应用整包补丁

把生成好的整个 `Patch/` 文件夹复制到旧版程序根目录内，然后双击：

- `Patch/apply_patch.py`
  或
- `apply_patch.exe`（如果你后续把 exe 一起分发到旧版根目录）

它会按照 `manifest.json` 自动：

- 校验旧文件 SHA256
- 对变更文件打补丁
- 复制新增文件
- 删除新版中已不存在的旧文件
- 为原文件生成 `*.backup_before_patch` 备份

### 单文件命令模式

```powershell
python src/binary_patcher.py create old.bin new.bin update.patch
python src/binary_patcher.py apply old.bin update.patch restored.bin
```

### 构建 exe

```powershell
scripts\build.bat
```

构建后会输出：

- `Releases/`：PyInstaller 直接输出的 exe 发布目录

## GitHub Actions

已支持在 GitHub 上自动构建 Windows 可执行文件，工作流文件位于：

- `.github/workflows/build.yml`
