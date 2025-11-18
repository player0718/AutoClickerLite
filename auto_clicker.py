#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动点击器 - Windows 桌面自动鼠标点击工具
使用 Tkinter GUI 和 pyautogui 实现
支持全局快捷键控制开始/停止
科技风格界面设计
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from pynput import keyboard
import threading

# 禁用 pyautogui 的故障保护（可选，如果需要可以启用）
# pyautogui.FAILSAFE = False

# 浅色科技风格颜色方案
COLORS = {
    'bg': '#f0f2f5',            # 浅色背景
    'bg_secondary': '#e4e6eb',   # 次级背景
    'card': '#ffffff',          # 卡片背景
    'card_hover': '#f5f5f5',    # 卡片悬停
    'primary': '#0066ff',       # 主色调（科技蓝）
    'primary_glow': '#0052cc',  # 主色深色
    'secondary': '#6c5ce7',     # 次要色（紫色）
    'accent': '#e84393',        # 强调色（粉色）
    'success': '#00b894',       # 成功色（青绿）
    'danger': '#ff4757',        # 危险色（红色）
    'warning': '#ffa502',       # 警告色
    'text': '#2d3436',          # 主文字
    'text_secondary': '#636e72', # 次要文字
    'border': '#dfe6e9',        # 边框色
    'border_glow': '#0066ff',   # 发光边框
    'disabled': '#b2bec3',      # 禁用色
}


class HotkeyDialog:
    """快捷键设置对话框"""

    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("快捷键设置")
        self.dialog.geometry("400x280")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=COLORS['bg'])

        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 280) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        # 主容器
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title = tk.Label(main_frame, text="⚡ 快捷键设置", font=("Consolas", 16, "bold"),
                        bg=COLORS['bg'], fg=COLORS['primary'])
        title.pack(pady=(0, 20))

        # 卡片容器
        card = tk.Frame(main_frame, bg=COLORS['card'], highlightbackground=COLORS['border_glow'],
                       highlightthickness=2)
        card.pack(fill="x", pady=5)

        # 开始/停止快捷键
        toggle_frame = tk.Frame(card, bg=COLORS['card'])
        toggle_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(toggle_frame, text="开始/停止", font=("Consolas", 11),
                bg=COLORS['card'], fg=COLORS['text']).pack(side="left")

        self.toggle_hotkey_var = tk.StringVar(value=self.app._format_hotkey(self.app.hotkey_toggle))

        toggle_btn_frame = tk.Frame(toggle_frame, bg=COLORS['card'])
        toggle_btn_frame.pack(side="right")

        self.toggle_label = tk.Label(toggle_btn_frame, textvariable=self.toggle_hotkey_var,
                                     font=("Consolas", 10), bg=COLORS['bg_secondary'],
                                     fg=COLORS['primary'], padx=12, pady=4)
        self.toggle_label.pack(side="left", padx=(0, 10))

        self.set_toggle_btn = tk.Button(toggle_btn_frame, text="设置", font=("Consolas", 9),
                                        bg=COLORS['primary'], fg="white", relief="flat",
                                        padx=15, pady=3, cursor="hand2",
                                        activebackground=COLORS['primary_glow'],
                                        command=self._start_recording_toggle)
        self.set_toggle_btn.pack(side="left")

        # 分隔线
        separator = tk.Frame(card, height=1, bg=COLORS['border'])
        separator.pack(fill="x", padx=15)

        # 紧急停止快捷键
        stop_frame = tk.Frame(card, bg=COLORS['card'])
        stop_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(stop_frame, text="紧急停止", font=("Consolas", 11),
                bg=COLORS['card'], fg=COLORS['text']).pack(side="left")

        self.stop_hotkey_var = tk.StringVar(value=self.app._format_hotkey(self.app.hotkey_stop))

        stop_btn_frame = tk.Frame(stop_frame, bg=COLORS['card'])
        stop_btn_frame.pack(side="right")

        self.stop_label = tk.Label(stop_btn_frame, textvariable=self.stop_hotkey_var,
                                   font=("Consolas", 10), bg=COLORS['bg_secondary'],
                                   fg=COLORS['danger'], padx=12, pady=4)
        self.stop_label.pack(side="left", padx=(0, 10))

        self.set_stop_btn = tk.Button(stop_btn_frame, text="设置", font=("Consolas", 9),
                                      bg=COLORS['primary'], fg="white", relief="flat",
                                      padx=15, pady=3, cursor="hand2",
                                      activebackground=COLORS['primary_glow'],
                                      command=self._start_recording_stop)
        self.set_stop_btn.pack(side="left")

        # 提示
        tk.Label(main_frame, text="点击「设置」后按下快捷键组合",
                font=("Consolas", 9), bg=COLORS['bg'], fg=COLORS['text_secondary']).pack(pady=(20, 0))

    def _start_recording_toggle(self):
        self.app.is_recording_toggle = True
        self.app.recorded_keys = set()
        self.toggle_hotkey_var.set("等待输入...")
        self.set_toggle_btn.config(state="disabled", bg=COLORS['disabled'])
        self.set_stop_btn.config(state="disabled", bg=COLORS['disabled'])
        self.app.on_recording_complete = self._on_toggle_complete

    def _on_toggle_complete(self):
        self.toggle_hotkey_var.set(self.app._format_hotkey(self.app.hotkey_toggle))
        self.set_toggle_btn.config(state="normal", bg=COLORS['primary'])
        self.set_stop_btn.config(state="normal", bg=COLORS['primary'])
        self.app.on_recording_complete = None

    def _start_recording_stop(self):
        self.app.is_recording_stop = True
        self.app.recorded_keys = set()
        self.stop_hotkey_var.set("等待输入...")
        self.set_toggle_btn.config(state="disabled", bg=COLORS['disabled'])
        self.set_stop_btn.config(state="disabled", bg=COLORS['disabled'])
        self.app.on_recording_complete = self._on_stop_complete

    def _on_stop_complete(self):
        self.stop_hotkey_var.set(self.app._format_hotkey(self.app.hotkey_stop))
        self.set_toggle_btn.config(state="normal", bg=COLORS['primary'])
        self.set_stop_btn.config(state="normal", bg=COLORS['primary'])
        self.app.on_recording_complete = None


class AutoClicker:
    """自动点击器主类"""

    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("400x560")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg'])

        # 点击状态
        self.is_clicking = False
        self.timer_id = None

        # 快捷键设置
        self.hotkey_toggle = {keyboard.Key.f6}
        self.hotkey_stop = {keyboard.Key.f7}

        # 键盘状态
        self.current_keys = set()
        self.is_recording_toggle = False
        self.is_recording_stop = False
        self.recorded_keys = set()
        self.on_recording_complete = None

        self._create_menu()
        self._create_widgets()
        self._start_keyboard_listener()

    def _create_menu(self):
        menubar = tk.Menu(self.root, bg=COLORS['bg'], fg=COLORS['text'],
                         activebackground=COLORS['primary'], activeforeground=COLORS['bg'])
        self.root.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['card'], fg=COLORS['text'],
                               activebackground=COLORS['primary'], activeforeground=COLORS['bg'])
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="快捷键设置...", command=self._show_hotkey_dialog)

        help_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['card'], fg=COLORS['text'],
                           activebackground=COLORS['primary'], activeforeground=COLORS['bg'])
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

    def _show_hotkey_dialog(self):
        HotkeyDialog(self.root, self)

    def _show_about(self):
        messagebox.showinfo(
            "关于",
            "Auto Clicker v2.0\n\n"
            "科技风格自动鼠标点击工具\n\n"
            "默认快捷键:\n"
            "F6 - 开始/停止\n"
            "F7 - 紧急停止"
        )

    def _create_card(self, parent, title):
        """创建科技风格卡片"""
        container = tk.Frame(parent, bg=COLORS['bg'])
        container.pack(fill="x", padx=20, pady=(0, 15))

        # 标题
        if title:
            title_frame = tk.Frame(container, bg=COLORS['bg'])
            title_frame.pack(fill="x", pady=(0, 8))

            # 装饰线
            tk.Frame(title_frame, width=3, height=14, bg=COLORS['primary']).pack(side="left", padx=(0, 8))
            tk.Label(title_frame, text=title, font=("Consolas", 10, "bold"),
                    bg=COLORS['bg'], fg=COLORS['text_secondary']).pack(side="left")

        # 卡片（带发光边框效果）
        card_outer = tk.Frame(container, bg=COLORS['border_glow'], padx=1, pady=1)
        card_outer.pack(fill="x")

        card = tk.Frame(card_outer, bg=COLORS['card'])
        card.pack(fill="both", expand=True)

        return card

    def _create_widgets(self):
        # 主滚动区域
        main_frame = tk.Frame(self.root, bg=COLORS['bg'])
        main_frame.pack(fill="both", expand=True, pady=15)

        # ========== 标题区域 ==========
        header = tk.Frame(main_frame, bg=COLORS['bg'])
        header.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(header, text="⚡ AUTO CLICKER", font=("Consolas", 18, "bold"),
                bg=COLORS['bg'], fg=COLORS['primary']).pack(side="left")

        # ========== 点击间隔卡片 ==========
        interval_card = self._create_card(main_frame, "INTERVAL")
        interval_inner = tk.Frame(interval_card, bg=COLORS['card'])
        interval_inner.pack(fill="x", padx=15, pady=12)

        self.interval_var = tk.StringVar(value="1000")
        interval_entry = tk.Entry(interval_inner, textvariable=self.interval_var,
                                  font=("Consolas", 14), width=10, relief="flat",
                                  bg=COLORS['bg_secondary'], fg=COLORS['primary'],
                                  insertbackground=COLORS['primary'],
                                  highlightthickness=1, highlightcolor=COLORS['primary'],
                                  highlightbackground=COLORS['border'])
        interval_entry.pack(side="left")
        self.interval_entry = interval_entry

        self.unit_var = tk.StringVar(value="毫秒")
        unit_frame = tk.Frame(interval_inner, bg=COLORS['card'])
        unit_frame.pack(side="right")

        for unit in ["毫秒", "秒"]:
            rb = tk.Radiobutton(unit_frame, text=unit, variable=self.unit_var,
                               value=unit, font=("Consolas", 10),
                               bg=COLORS['card'], fg=COLORS['text'],
                               selectcolor=COLORS['bg_secondary'],
                               activebackground=COLORS['card'],
                               activeforeground=COLORS['primary'])
            rb.pack(side="left", padx=8)

        # ========== 点击类型卡片 ==========
        type_card = self._create_card(main_frame, "CLICK TYPE")

        self.click_type_var = tk.StringVar(value="左键单击")
        types = [("左键单击", "左键单击"), ("右键单击", "右键单击"), ("左键双击", "左键双击")]

        for i, (text, value) in enumerate(types):
            type_row = tk.Frame(type_card, bg=COLORS['card'])
            type_row.pack(fill="x", padx=15, pady=8)

            rb = tk.Radiobutton(type_row, text=text, variable=self.click_type_var,
                               value=value, font=("Consolas", 11),
                               bg=COLORS['card'], fg=COLORS['text'],
                               selectcolor=COLORS['bg_secondary'],
                               activebackground=COLORS['card'],
                               activeforeground=COLORS['primary'])
            rb.pack(side="left")

            if i < len(types) - 1:
                sep = tk.Frame(type_card, height=1, bg=COLORS['border'])
                sep.pack(fill="x", padx=15)

        # ========== 点击位置卡片 ==========
        pos_card = self._create_card(main_frame, "POSITION")

        self.use_current_pos_var = tk.BooleanVar(value=True)

        # 当前位置选项
        current_row = tk.Frame(pos_card, bg=COLORS['card'])
        current_row.pack(fill="x", padx=15, pady=10)

        current_cb = tk.Checkbutton(current_row, text="使用当前鼠标位置",
                                    variable=self.use_current_pos_var,
                                    font=("Consolas", 11), bg=COLORS['card'],
                                    fg=COLORS['text'], selectcolor=COLORS['bg_secondary'],
                                    activebackground=COLORS['card'],
                                    activeforeground=COLORS['primary'],
                                    command=self._toggle_position_entry)
        current_cb.pack(side="left")

        sep = tk.Frame(pos_card, height=1, bg=COLORS['border'])
        sep.pack(fill="x", padx=15)

        # 坐标输入
        coord_row = tk.Frame(pos_card, bg=COLORS['card'])
        coord_row.pack(fill="x", padx=15, pady=12)

        tk.Label(coord_row, text="X", font=("Consolas", 10, "bold"),
                bg=COLORS['card'], fg=COLORS['primary']).pack(side="left")

        self.x_var = tk.StringVar(value="0")
        self.x_entry = tk.Entry(coord_row, textvariable=self.x_var,
                                font=("Consolas", 11), width=6, relief="flat",
                                bg=COLORS['bg_secondary'], fg=COLORS['text'],
                                insertbackground=COLORS['primary'],
                                highlightthickness=1, highlightcolor=COLORS['primary'],
                                highlightbackground=COLORS['border'])
        self.x_entry.pack(side="left", padx=(5, 15))

        tk.Label(coord_row, text="Y", font=("Consolas", 10, "bold"),
                bg=COLORS['card'], fg=COLORS['primary']).pack(side="left")

        self.y_var = tk.StringVar(value="0")
        self.y_entry = tk.Entry(coord_row, textvariable=self.y_var,
                                font=("Consolas", 11), width=6, relief="flat",
                                bg=COLORS['bg_secondary'], fg=COLORS['text'],
                                insertbackground=COLORS['primary'],
                                highlightthickness=1, highlightcolor=COLORS['primary'],
                                highlightbackground=COLORS['border'])
        self.y_entry.pack(side="left", padx=5)

        self.get_pos_btn = tk.Button(coord_row, text="获取", font=("Consolas", 9),
                                     bg=COLORS['bg_secondary'], fg=COLORS['primary'],
                                     relief="flat", padx=10, cursor="hand2",
                                     activebackground=COLORS['card'],
                                     command=self._get_current_position)
        self.get_pos_btn.pack(side="right")

        self._toggle_position_entry()

        # ========== 控制按钮 ==========
        btn_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        btn_frame.pack(fill="x", padx=20, pady=(5, 0))

        self.start_btn = tk.Button(btn_frame, text="▶ 开始", font=("Consolas", 12, "bold"),
                                   bg=COLORS['primary'], fg="white", relief="flat",
                                   height=2, cursor="hand2",
                                   activebackground=COLORS['primary_glow'],
                                   command=self._start_clicking)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_btn = tk.Button(btn_frame, text="■ 停止", font=("Consolas", 12, "bold"),
                                  bg=COLORS['disabled'], fg=COLORS['text_secondary'], relief="flat",
                                  height=2, state="disabled", command=self._stop_clicking)
        self.stop_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # ========== 状态显示 ==========
        status_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        status_frame.pack(fill="x", padx=20, pady=(15, 0))

        # 状态指示器（带背景色块）
        self.status_indicator = tk.Frame(status_frame, bg=COLORS['disabled'], padx=20, pady=8)
        self.status_indicator.pack(fill="x", pady=(0, 10))

        self.status_var = tk.StringVar(value="● STOPPED")
        self.status_label = tk.Label(self.status_indicator, textvariable=self.status_var,
                                     font=("Consolas", 16, "bold"),
                                     bg=COLORS['disabled'], fg="white")
        self.status_label.pack()

        self.click_count = 0
        self.count_var = tk.StringVar(value="Clicks: 0")
        self.count_label = tk.Label(self.status_indicator, textvariable=self.count_var,
                font=("Consolas", 11), bg=COLORS['disabled'], fg="white")
        self.count_label.pack()

        # 快捷键提示
        self.hotkey_hint_var = tk.StringVar()
        self._update_hotkey_hint()
        tk.Label(status_frame, textvariable=self.hotkey_hint_var,
                font=("Consolas", 9), bg=COLORS['bg'],
                fg=COLORS['border']).pack(pady=(8, 0))

    def _update_hotkey_hint(self):
        toggle_key = self._format_hotkey(self.hotkey_toggle)
        stop_key = self._format_hotkey(self.hotkey_stop)
        self.hotkey_hint_var.set(f"[{toggle_key}] Toggle · [{stop_key}] Stop")

    def _format_hotkey(self, keys):
        if not keys:
            return "N/A"

        key_names = []
        for key in keys:
            if isinstance(key, keyboard.Key):
                name = key.name.upper()
                name_map = {
                    'CTRL_L': 'Ctrl', 'CTRL_R': 'Ctrl',
                    'ALT_L': 'Alt', 'ALT_R': 'Alt',
                    'SHIFT_L': 'Shift', 'SHIFT_R': 'Shift',
                    'CMD': 'Win', 'CMD_L': 'Win', 'CMD_R': 'Win',
                }
                name = name_map.get(name, name.replace('_', ' ').title())
                key_names.append(name)
            elif isinstance(key, keyboard.KeyCode):
                if key.char:
                    key_names.append(key.char.upper())
                elif key.vk:
                    key_names.append(f"VK{key.vk}")

        return "+".join(sorted(key_names))

    def _start_keyboard_listener(self):
        def on_press(key):
            self.current_keys.add(key)

            if self.is_recording_toggle or self.is_recording_stop:
                self.recorded_keys.add(key)
                return

            self._check_hotkeys()

        def on_release(key):
            if self.is_recording_toggle and self.recorded_keys:
                self._finish_recording_toggle()
            elif self.is_recording_stop and self.recorded_keys:
                self._finish_recording_stop()

            self.current_keys.discard(key)

        self.keyboard_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def _check_hotkeys(self):
        normalized_current = self._normalize_keys(self.current_keys)
        normalized_toggle = self._normalize_keys(self.hotkey_toggle)
        normalized_stop = self._normalize_keys(self.hotkey_stop)

        if normalized_current == normalized_stop:
            self.root.after(0, self._stop_clicking)
        elif normalized_current == normalized_toggle:
            self.root.after(0, self._toggle_clicking)

    def _normalize_keys(self, keys):
        normalized = set()
        for key in keys:
            if isinstance(key, keyboard.Key):
                name = key.name
                if name in ('ctrl_l', 'ctrl_r'):
                    normalized.add('ctrl')
                elif name in ('alt_l', 'alt_r'):
                    normalized.add('alt')
                elif name in ('shift_l', 'shift_r'):
                    normalized.add('shift')
                elif name in ('cmd', 'cmd_l', 'cmd_r'):
                    normalized.add('cmd')
                else:
                    normalized.add(name)
            elif isinstance(key, keyboard.KeyCode):
                if key.char:
                    normalized.add(key.char.lower())
                elif key.vk:
                    normalized.add(f"vk{key.vk}")
        return frozenset(normalized)

    def _toggle_clicking(self):
        if self.is_clicking:
            self._stop_clicking()
        else:
            self._start_clicking()

    def _finish_recording_toggle(self):
        if self.recorded_keys:
            self.hotkey_toggle = self.recorded_keys.copy()

        self.is_recording_toggle = False
        self.recorded_keys = set()
        self._update_hotkey_hint()

        if self.on_recording_complete:
            self.root.after(0, self.on_recording_complete)

    def _finish_recording_stop(self):
        if self.recorded_keys:
            self.hotkey_stop = self.recorded_keys.copy()

        self.is_recording_stop = False
        self.recorded_keys = set()
        self._update_hotkey_hint()

        if self.on_recording_complete:
            self.root.after(0, self.on_recording_complete)

    def _toggle_position_entry(self):
        if self.use_current_pos_var.get():
            self.x_entry.config(state="disabled", bg=COLORS['disabled'],
                               highlightbackground=COLORS['disabled'])
            self.y_entry.config(state="disabled", bg=COLORS['disabled'],
                               highlightbackground=COLORS['disabled'])
            self.get_pos_btn.config(state="disabled", fg=COLORS['disabled'])
        else:
            self.x_entry.config(state="normal", bg=COLORS['bg_secondary'],
                               highlightbackground=COLORS['border'])
            self.y_entry.config(state="normal", bg=COLORS['bg_secondary'],
                               highlightbackground=COLORS['border'])
            self.get_pos_btn.config(state="normal", fg=COLORS['primary'])

    def _get_current_position(self):
        x, y = pyautogui.position()
        self.x_var.set(str(x))
        self.y_var.set(str(y))

    def _validate_inputs(self):
        try:
            interval = int(self.interval_var.get())
            if interval <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的时间间隔（正整数）")
            return False

        if not self.use_current_pos_var.get():
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
                if x < 0 or y < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的坐标（非负整数）")
                return False

        return True

    def _get_interval_ms(self):
        interval = int(self.interval_var.get())
        if self.unit_var.get() == "秒":
            interval *= 1000
        return interval

    def _perform_click(self):
        if not self.is_clicking:
            return

        try:
            if self.use_current_pos_var.get():
                x, y = pyautogui.position()
            else:
                x = int(self.x_var.get())
                y = int(self.y_var.get())

            click_type = self.click_type_var.get()
            if click_type == "左键单击":
                pyautogui.click(x, y, button='left')
            elif click_type == "右键单击":
                pyautogui.click(x, y, button='right')
            elif click_type == "左键双击":
                pyautogui.doubleClick(x, y)

            self.click_count += 1
            self.count_var.set(f"Clicks: {self.click_count}")

            interval = self._get_interval_ms()
            self.timer_id = self.root.after(interval, self._perform_click)

        except pyautogui.FailSafeException:
            self._stop_clicking()
            messagebox.showinfo("已停止", "检测到故障保护触发，自动点击已停止")
        except Exception as e:
            self._stop_clicking()
            messagebox.showerror("错误", f"点击时发生错误: {str(e)}")

    def _start_clicking(self):
        if not self._validate_inputs():
            return

        self.is_clicking = True
        self.click_count = 0
        self.count_var.set("Clicks: 0")

        self.status_var.set("● RUNNING")
        self.status_indicator.config(bg=COLORS['success'])
        self.status_label.config(bg=COLORS['success'], fg="white")
        self.count_label.config(bg=COLORS['success'], fg="white")
        self.start_btn.config(state="disabled", bg=COLORS['disabled'], fg=COLORS['text_secondary'])
        self.stop_btn.config(state="normal", bg=COLORS['danger'], fg="white", cursor="hand2")

        self.interval_entry.config(state="disabled")

        self._perform_click()

    def _stop_clicking(self):
        self.is_clicking = False

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.status_var.set("● STOPPED")
        self.status_indicator.config(bg=COLORS['disabled'])
        self.status_label.config(bg=COLORS['disabled'], fg="white")
        self.count_label.config(bg=COLORS['disabled'], fg="white")
        self.start_btn.config(state="normal", bg=COLORS['primary'], fg="white", cursor="hand2")
        self.stop_btn.config(state="disabled", bg=COLORS['disabled'], fg=COLORS['text_secondary'], cursor="")

        self.interval_entry.config(state="normal")
        self._toggle_position_entry()

    def cleanup(self):
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()


def main():
    root = tk.Tk()

    # 设置 DPI 感知（Windows 高分屏支持）
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = AutoClicker(root)

    def on_closing():
        if app.is_clicking:
            app._stop_clicking()
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
