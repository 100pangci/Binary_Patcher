# Binary Patcher
这是一个用于生成和应用二进制补丁项目，并支持整目录补丁工作流。项目现已统一通过 HDiffPatch (`hdiffz` / `hpatchz`) 处理补丁生成与应用。

支持：

- 生成整目录补丁
- 应用整目录补丁
- 一键回滚已经应用的补丁

项目底层统一使用 **HDiffPatch**（`hdiffz` / `hpatchz`）。

## 目录结构

```text
.
├─ .github/workflows/      # GitHub Actions 自动构建
├─ scripts/                # 构建脚本
├─ src/                    # Python 源码
├─ src/legacy              # 项目之前的源码，使用的旧方案
├─ .gitignore
├─ pyproject.toml
├─ requirements.txt
└─ requirements-build.txt
```

## 主要文件说明

- `src/binary_patcher.py`：核心命令行工具
- `src/apply_patch.py`：面向最终用户的自动补丁脚本
- `src/rollback_patch.py`：面向最终用户的自动回滚脚本
- `scripts/build.py`：统一构建与发布整理脚本
- `scripts/build.bat`：Windows 下一键构建入口

## 下载什么？

请直接下载发布页里的：

- `binary_patcher_toolkit.zip`

压缩包内包含 3 个工具：

- `binary_patcher.exe`：生成补丁
- `apply_patch.exe`：应用补丁
- `rollback_patch.exe`：回滚补丁

---

## 一、生成整目录补丁

### 第一次运行

双击运行：

- `binary_patcher.exe`

程序会自动创建以下目录：

- `Old/`
- `New/`
- `Patch/`

### 准备文件

然后你只需要：

1. 把**旧版本完整目录**放进 `Old/`
2. 把**新版本完整目录**放进 `New/`
3. 再次双击运行 `binary_patcher.exe`

### 生成结果

程序会先计算 SHA256，再按相同相对路径找出变更、新增、删除文件，并在 `Patch/` 中生成：

- `manifest.json`
- 与原目录结构一致的 `*.patch`
- 对新增文件生成 `*.new`
> 生成补丁时，程序会自动读取当前电脑的 CPU 线程数，默认会预留 1 个线程给系统，其余线程用于 HDiffPatch 多线程加速；如果机器只有 1 个线程，则仍至少使用 1 个线程运行。

---

## 二、应用整包补丁

把以下内容复制到**旧版本程序根目录**：

- 整个 `Patch/` 文件夹
- `apply_patch.exe`

然后双击运行：

- `apply_patch.exe`

程序会按照 `manifest.json` 自动：

- 校验旧文件 SHA256
- 对变更文件打补丁
- 复制新增文件
- 删除新版中已不存在的旧文件
- 为原文件生成 `*.backup_before_patch` 备份

---

## 三、回滚已经应用的补丁

如果你需要撤销已经打过的补丁，请在**旧版本程序根目录**准备：

- 整个 `Patch/` 文件夹
- `rollback_patch.exe`

然后双击运行：

- `rollback_patch.exe`

程序会按 `manifest.json` 自动：

- 恢复变更文件对应的 `*.backup_before_patch`
- 恢复被删除文件对应的 `*.backup_before_patch`
- 删除补丁新增出来的文件
- 保持原有目录结构不乱

回滚完成后，已恢复成功的 `*.backup_before_patch` 备份文件会被自动删除。

---

## 四、发布包中包含什么？

GitHub Release / GitHub Actions 产物中会提供：

- `binary_patcher.exe`
- `apply_patch.exe`
- `rollback_patch.exe`
- `binary_patcher_toolkit.zip`

其中推荐最终用户直接下载：

- `binary_patcher_toolkit.zip`

这样可以一次性拿到全部工具。

### 构建 exe

```powershell
scripts\build.bat
```

构建脚本会自动下载 HDiffPatch 最新版 Windows 64 位发行包到 `bin/`，并在使用 **Nuitka** 打包 `binary_patcher.exe` / `apply_patch.exe` / `rollback_patch.exe` 时一并嵌入。

构建后的工具包包含：

- `binary_patcher.exe`
- `apply_patch.exe`
- `rollback_patch.exe`
- `binary_patcher_toolkit.zip`（包含以上三个 exe，便于整包分发）

构建后会输出：

- `Releases/`：Nuitka 构建后整理好的 exe 发布目录

---

## 五、GitHub Actions

项目已支持自动构建 Windows 发布包，工作流文件位于：

- `.github/workflows/build.yml`