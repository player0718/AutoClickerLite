# Auto Clicker

Windows 桌面自动鼠标点击工具，使用 Python + Tkinter 开发。

## 技术栈

- **GUI**: Tkinter (Python 内置)
- **鼠标控制**: pyautogui
- **键盘监听**: pynput
- **打包工具**: PyInstaller

## 项目结构

```
AutoClickerLite/
├── auto_clicker.py      # 主程序（约 660 行）
├── requirements.txt     # Python 依赖
├── README.md           # 用户文档
└── claude.md           # 本文件
```

## 主要功能

- 设置点击间隔（毫秒/秒）
- 选择点击类型（左键单击、右键单击、左键双击）
- 选择点击位置（当前鼠标位置或固定坐标）
- 全局快捷键支持（默认 F6 开始/停止，F7 紧急停止）
- 可自定义快捷键

## 代码架构

### 主要类

- `AutoClicker`: 主应用类，包含 GUI 和业务逻辑
- `HotkeyDialog`: 快捷键设置对话框

### 关键方法

- `_create_widgets()`: 创建 UI 组件
- `_start_clicking()`: 开始自动点击
- `_stop_clicking()`: 停止自动点击
- `_perform_click()`: 执行单次点击
- `_start_keyboard_listener()`: 启动全局键盘监听

### 设计模式

- 使用 `tkinter.after()` 实现定时点击，避免多线程
- 使用 `pynput.keyboard.Listener` 在后台线程监听全局快捷键
- 通过 `root.after(0, callback)` 确保 GUI 更新在主线程执行

## 开发说明

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python auto_clicker.py
```

### 打包为 exe

```bash
pyinstaller --onefile --windowed --name "AutoClicker" auto_clicker.py
```

生成文件位于 `dist/AutoClicker.exe`

## UI 风格

当前使用浅色科技风格：
- 背景色: `#f0f2f5`
- 主色调: `#0066ff` (科技蓝)
- 成功色: `#00b894` (青绿)
- 危险色: `#ff4757` (红色)
- 字体: Consolas

## 注意事项

- 程序需要在 Windows 上运行（依赖 pyautogui 和 pynput）
- 某些应用可能需要管理员权限才能点击
- 故障保护：将鼠标移到屏幕左上角可停止程序
