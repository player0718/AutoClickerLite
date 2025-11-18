#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动点击器 - Windows 桌面自动鼠标点击工具
使用 Tkinter GUI 和 pyautogui 实现
支持全局快捷键控制开始/停止
iOS 风格界面设计
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from pynput import keyboard
import threading

# 禁用 pyautogui 的故障保护（可选，如果需要可以启用）
# pyautogui.FAILSAFE = False

# iOS 风格颜色方案
COLORS = {
    'bg': '#f5f5f7',           # 背景色
    'card': '#ffffff',          # 卡片背景
    'primary': '#007AFF',       # 主色调（iOS蓝）
    'primary_dark': '#0056b3',  # 主色调深色
    'danger': '#FF3B30',        # 危险色（iOS红）
    'success': '#34C759',       # 成功色（iOS绿）
    'text': '#1d1d1f',          # 主文字
    'text_secondary': '#86868b', # 次要文字
    'border': '#e5e5e5',        # 边框色
    'disabled': '#c7c7cc',      # 禁用色
}


class HotkeyDialog:
    """快捷键设置对话框"""

    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("快捷键设置")
        self.dialog.geometry("380x240")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=COLORS['bg'])

        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 380) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 240) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        # 主容器
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title = tk.Label(main_frame, text="快捷键设置", font=("Segoe UI", 16, "bold"),
                        bg=COLORS['bg'], fg=COLORS['text'])
        title.pack(pady=(0, 15))

        # 卡片容器
        card = tk.Frame(main_frame, bg=COLORS['card'], highlightbackground=COLORS['border'],
                       highlightthickness=1)
        card.pack(fill="x", pady=5)

        # 开始/停止快捷键
        toggle_frame = tk.Frame(card, bg=COLORS['card'])
        toggle_frame.pack(fill="x", padx=15, pady=12)

        tk.Label(toggle_frame, text="开始/停止", font=("Segoe UI", 11),
                bg=COLORS['card'], fg=COLORS['text']).pack(side="left")

        self.toggle_hotkey_var = tk.StringVar(value=self.app._format_hotkey(self.app.hotkey_toggle))

        toggle_btn_frame = tk.Frame(toggle_frame, bg=COLORS['card'])
        toggle_btn_frame.pack(side="right")

        self.toggle_label = tk.Label(toggle_btn_frame, textvariable=self.toggle_hotkey_var,
                                     font=("Segoe UI", 10), bg=COLORS['bg'], fg=COLORS['primary'],
                                     padx=10, pady=3)
        self.toggle_label.pack(side="left", padx=(0, 8))

        self.set_toggle_btn = tk.Button(toggle_btn_frame, text="设置", font=("Segoe UI", 9),
                                        bg=COLORS['primary'], fg="white", relief="flat",
                                        padx=12, pady=2, cursor="hand2",
                                        command=self._start_recording_toggle)
        self.set_toggle_btn.pack(side="left")

        # 分隔线
        separator = tk.Frame(card, height=1, bg=COLORS['border'])
        separator.pack(fill="x", padx=15)

        # 紧急停止快捷键
        stop_frame = tk.Frame(card, bg=COLORS['card'])
        stop_frame.pack(fill="x", padx=15, pady=12)

        tk.Label(stop_frame, text="紧急停止", font=("Segoe UI", 11),
                bg=COLORS['card'], fg=COLORS['text']).pack(side="left")

        self.stop_hotkey_var = tk.StringVar(value=self.app._format_hotkey(self.app.hotkey_stop))

        stop_btn_frame = tk.Frame(stop_frame, bg=COLORS['card'])
        stop_btn_frame.pack(side="right")

        self.stop_label = tk.Label(stop_btn_frame, textvariable=self.stop_hotkey_var,
                                   font=("Segoe UI", 10), bg=COLORS['bg'], fg=COLORS['danger'],
                                   padx=10, pady=3)
        self.stop_label.pack(side="left", padx=(0, 8))

        self.set_stop_btn = tk.Button(stop_btn_frame, text="设置", font=("Segoe UI", 9),
                                      bg=COLORS['primary'], fg="white", relief="flat",
                                      padx=12, pady=2, cursor="hand2",
                                      command=self._start_recording_stop)
        self.set_stop_btn.pack(side="left")

        # 提示
        tk.Label(main_frame, text="点击「设置」后按下快捷键组合",
                font=("Segoe UI", 9), bg=COLORS['bg'], fg=COLORS['text_secondary']).pack(pady=(15, 0))

    def _start_recording_toggle(self):
        self.app.is_recording_toggle = True
        self.app.recorded_keys = set()
        self.toggle_hotkey_var.set("请按键...")
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
        self.stop_hotkey_var.set("请按键...")
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
        self.root.title("自动点击器")
        self.root.geometry("380x520")
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
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="快捷键设置...", command=self._show_hotkey_dialog)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

    def _show_hotkey_dialog(self):
        HotkeyDialog(self.root, self)

    def _show_about(self):
        messagebox.showinfo(
            "关于",
            "自动点击器 v1.2\n\n"
            "简洁现代的自动鼠标点击工具\n\n"
            "默认快捷键:\n"
            "F6 - 开始/停止\n"
            "F7 - 紧急停止"
        )

    def _create_card(self, parent, title):
        """创建 iOS 风格卡片"""
        container = tk.Frame(parent, bg=COLORS['bg'])
        container.pack(fill="x", padx=20, pady=(0, 12))

        # 标题
        if title:
            tk.Label(container, text=title, font=("Segoe UI", 11, "bold"),
                    bg=COLORS['bg'], fg=COLORS['text_secondary']).pack(anchor="w", pady=(0, 6))

        # 卡片
        card = tk.Frame(container, bg=COLORS['card'], highlightbackground=COLORS['border'],
                       highlightthickness=1)
        card.pack(fill="x")

        return card

    def _create_widgets(self):
        # 主滚动区域
        main_frame = tk.Frame(self.root, bg=COLORS['bg'])
        main_frame.pack(fill="both", expand=True, pady=15)

        # ========== 点击间隔卡片 ==========
        interval_card = self._create_card(main_frame, "点击间隔")
        interval_inner = tk.Frame(interval_card, bg=COLORS['card'])
        interval_inner.pack(fill="x", padx=15, pady=12)

        self.interval_var = tk.StringVar(value="1000")
        interval_entry = tk.Entry(interval_inner, textvariable=self.interval_var,
                                  font=("Segoe UI", 12), width=10, relief="flat",
                                  bg=COLORS['bg'], fg=COLORS['text'],
                                  insertbackground=COLORS['primary'])
        interval_entry.pack(side="left")
        self.interval_entry = interval_entry

        self.unit_var = tk.StringVar(value="毫秒")
        unit_frame = tk.Frame(interval_inner, bg=COLORS['card'])
        unit_frame.pack(side="right")

        for unit in ["毫秒", "秒"]:
            rb = tk.Radiobutton(unit_frame, text=unit, variable=self.unit_var,
                               value=unit, font=("Segoe UI", 10),
                               bg=COLORS['card'], fg=COLORS['text'],
                               selectcolor=COLORS['card'], activebackground=COLORS['card'])
            rb.pack(side="left", padx=5)

        # ========== 点击类型卡片 ==========
        type_card = self._create_card(main_frame, "点击类型")

        self.click_type_var = tk.StringVar(value="左键单击")
        types = [("左键单击", "left"), ("右键单击", "right"), ("左键双击", "double")]

        for i, (text, value) in enumerate(types):
            type_row = tk.Frame(type_card, bg=COLORS['card'])
            type_row.pack(fill="x", padx=15, pady=8)

            rb = tk.Radiobutton(type_row, text=text, variable=self.click_type_var,
                               value=text, font=("Segoe UI", 11),
                               bg=COLORS['card'], fg=COLORS['text'],
                               selectcolor=COLORS['card'], activebackground=COLORS['card'])
            rb.pack(side="left")

            if i < len(types) - 1:
                sep = tk.Frame(type_card, height=1, bg=COLORS['border'])
                sep.pack(fill="x", padx=15)

        # ========== 点击位置卡片 ==========
        pos_card = self._create_card(main_frame, "点击位置")

        self.use_current_pos_var = tk.BooleanVar(value=True)

        # 当前位置选项
        current_row = tk.Frame(pos_card, bg=COLORS['card'])
        current_row.pack(fill="x", padx=15, pady=8)

        current_cb = tk.Checkbutton(current_row, text="使用当前鼠标位置",
                                    variable=self.use_current_pos_var,
                                    font=("Segoe UI", 11), bg=COLORS['card'],
                                    fg=COLORS['text'], selectcolor=COLORS['card'],
                                    activebackground=COLORS['card'],
                                    command=self._toggle_position_entry)
        current_cb.pack(side="left")

        sep = tk.Frame(pos_card, height=1, bg=COLORS['border'])
        sep.pack(fill="x", padx=15)

        # 坐标输入
        coord_row = tk.Frame(pos_card, bg=COLORS['card'])
        coord_row.pack(fill="x", padx=15, pady=10)

        tk.Label(coord_row, text="X", font=("Segoe UI", 10),
                bg=COLORS['card'], fg=COLORS['text_secondary']).pack(side="left")

        self.x_var = tk.StringVar(value="0")
        self.x_entry = tk.Entry(coord_row, textvariable=self.x_var,
                                font=("Segoe UI", 11), width=6, relief="flat",
                                bg=COLORS['bg'], fg=COLORS['text'])
        self.x_entry.pack(side="left", padx=(5, 15))

        tk.Label(coord_row, text="Y", font=("Segoe UI", 10),
                bg=COLORS['card'], fg=COLORS['text_secondary']).pack(side="left")

        self.y_var = tk.StringVar(value="0")
        self.y_entry = tk.Entry(coord_row, textvariable=self.y_var,
                                font=("Segoe UI", 11), width=6, relief="flat",
                                bg=COLORS['bg'], fg=COLORS['text'])
        self.y_entry.pack(side="left", padx=5)

        self.get_pos_btn = tk.Button(coord_row, text="获取", font=("Segoe UI", 9),
                                     bg=COLORS['bg'], fg=COLORS['primary'],
                                     relief="flat", padx=8, cursor="hand2",
                                     command=self._get_current_position)
        self.get_pos_btn.pack(side="right")

        self._toggle_position_entry()

        # ========== 控制按钮 ==========
        btn_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        btn_frame.pack(fill="x", padx=20, pady=(5, 0))

        self.start_btn = tk.Button(btn_frame, text="开始", font=("Segoe UI", 12, "bold"),
                                   bg=COLORS['primary'], fg="white", relief="flat",
                                   height=2, cursor="hand2", command=self._start_clicking)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_btn = tk.Button(btn_frame, text="停止", font=("Segoe UI", 12, "bold"),
                                  bg=COLORS['disabled'], fg="white", relief="flat",
                                  height=2, state="disabled", command=self._stop_clicking)
        self.stop_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # ========== 状态显示 ==========
        status_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        status_frame.pack(fill="x", padx=20, pady=(15, 0))

        self.status_var = tk.StringVar(value="已停止")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                     font=("Segoe UI", 14, "bold"),
                                     bg=COLORS['bg'], fg=COLORS['text'])
        self.status_label.pack()

        self.click_count = 0
        self.count_var = tk.StringVar(value="点击次数: 0")
        tk.Label(status_frame, textvariable=self.count_var,
                font=("Segoe UI", 10), bg=COLORS['bg'],
                fg=COLORS['text_secondary']).pack()

        # 快捷键提示
        self.hotkey_hint_var = tk.StringVar()
        self._update_hotkey_hint()
        tk.Label(status_frame, textvariable=self.hotkey_hint_var,
                font=("Segoe UI", 9), bg=COLORS['bg'],
                fg=COLORS['text_secondary']).pack(pady=(5, 0))

    def _update_hotkey_hint(self):
        toggle_key = self._format_hotkey(self.hotkey_toggle)
        stop_key = self._format_hotkey(self.hotkey_stop)
        self.hotkey_hint_var.set(f"{toggle_key} 开始/停止 · {stop_key} 紧急停止")

    def _format_hotkey(self, keys):
        if not keys:
            return "未设置"

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
            self.x_entry.config(state="disabled", bg=COLORS['disabled'])
            self.y_entry.config(state="disabled", bg=COLORS['disabled'])
            self.get_pos_btn.config(state="disabled", fg=COLORS['disabled'])
        else:
            self.x_entry.config(state="normal", bg=COLORS['bg'])
            self.y_entry.config(state="normal", bg=COLORS['bg'])
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
            self.count_var.set(f"点击次数: {self.click_count}")

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
        self.count_var.set("点击次数: 0")

        self.status_var.set("正在点击...")
        self.status_label.config(fg=COLORS['success'])
        self.start_btn.config(state="disabled", bg=COLORS['disabled'])
        self.stop_btn.config(state="normal", bg=COLORS['danger'], cursor="hand2")

        self.interval_entry.config(state="disabled")

        self._perform_click()

    def _stop_clicking(self):
        self.is_clicking = False

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.status_var.set("已停止")
        self.status_label.config(fg=COLORS['text'])
        self.start_btn.config(state="normal", bg=COLORS['primary'], cursor="hand2")
        self.stop_btn.config(state="disabled", bg=COLORS['disabled'], cursor="")

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
