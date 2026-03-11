# 便携运行环境（项目内自带 Python + 依赖）

可将 **Python 解释器** 和 **已安装依赖** 放入项目目录，整份项目复制到另一台 Windows 电脑后**无需**在该机安装 Python 或执行 `pip install`，直接使用即可。

**当前项目**：若已存在 `python/python.exe` 且已安装 pip 与 `requirements.txt`，则无需任何安装步骤；整份项目复制到别机后，直接使用 `python\python.exe` 或 `python scripts/run_with_env.py` 即可。

---

## 一、通用智能体如何使用

- **若项目根目录存在 `python/python.exe`**（便携环境已打好）：  
  运行本技能任意脚本时，**一律使用** `python\python.exe` 作为解释器（或通过 `scripts/run_with_env.py` 调用），**不要**依赖目标机上的系统 Python 或 pip。
- **若不存在 `python/` 目录**：  
  使用目标机已安装的 `python` / `python3`，并按需执行 `pip install -r requirements.txt`。

推荐用法（无论是否便携）：在项目根执行  
`python scripts/run_with_env.py <脚本名> [参数...]`  
例如：`python scripts/run_with_env.py do 截图`。  
`run_with_env.py` 会自动选用项目内 `python/python.exe`（若存在），否则使用当前解释器。

---

## 二、如何在本机打出便携环境（一次性）

在**当前电脑**上，将 Python 和依赖安装到项目内的 `python/` 目录，之后整份项目（含 `python/`）复制到别机即可直接用。

### 方式 A：Windows 嵌入式包（推荐，真正便携）

1. 下载 [Windows embeddable package](https://www.python.org/downloads/windows/)（与当前开发用 Python 版本一致或兼容，如 3.11），解压到项目根下的 `python/`，得到 `python/python.exe`、`python.dll` 等。
2. 在 `python/` 中启用 pip（若官方包未带 pip）：  
   - 下载 [get-pip.py](https://bootstrap.pypa.io/get-pip.py)，执行：  
     `python\python.exe get-pip.py`
3. 安装项目依赖到该环境：  
   `python\python.exe -m pip install -r requirements.txt`
4. 此后将**整个项目目录**（含 `python/`）复制到任意 Windows 电脑，在项目根执行：  
   `python\python.exe scripts\do.py 截图`  
   或通过 `python scripts/run_with_env.py do 截图`（若该机有系统 Python 可先用来调 run_with_env）。

### 方式 B：虚拟环境（仅限本机或同路径）

在本机项目根执行 `python -m venv .venv`，再 `.venv\Scripts\pip install -r requirements.txt`。  
注意：默认 venv 含本机路径，**复制到别机可能失效**。若希望“复制到别机直接用”，请用方式 A。

---

## 三、与 SKILL 的衔接

- SKILL.md 中已说明：通用智能体在存在 `python/python.exe` 时应**直接使用**该解释器运行脚本，无需在目标机安装 Python 或依赖。
- 所有「运行脚本」的示例均可改为：先 `python scripts/run_with_env.py` 再跟脚本名与参数；或在有便携环境时统一写为 `python\python.exe scripts\xxx.py`。
