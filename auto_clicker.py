#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动点击器 - Windows 桌面自动鼠标点击工具
使用 Tkinter GUI 和 pyautogui 实现
支持全局快捷键控制开始/停止
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from pynput import keyboard
import threading

# 禁用 pyautogui 的故障保护（可选，如果需要可以启用）
# pyautogui.FAILSAFE = False


class HotkeyDialog:
    """快捷键设置对话框"""

    def __init__(self, parent, app):
        """
        初始化快捷键设置对话框

        Args:
            parent: 父窗口
            app: AutoClicker 实例
        """
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("快捷键设置")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 350) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 200) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        """创建对话框组件"""
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill="both", expand=True)

        # 开始/停止切换快捷键
        toggle_frame = ttk.Frame(main_frame)
        toggle_frame.pack(fill="x", pady=5)

        ttk.Label(toggle_frame, text="开始/停止:", width=10).pack(side="left")
        self.toggle_hotkey_var = tk.StringVar(value=self.app._format_hotkey(self.app.hotkey_toggle))
        self.toggle_hotkey_label = ttk.Label(toggle_frame, textvariable=self.toggle_hotkey_var,
                                              width=15, relief="sunken", anchor="center")
        self.toggle_hotkey_label.pack(side="left", padx=5)

        self.set_toggle_btn = ttk.Button(
            toggle_frame,
            text="设置",
            command=self._start_recording_toggle,
            width=8
        )
        self.set_toggle_btn.pack(side="left", padx=5)

        # 紧急停止快捷键
        stop_frame = ttk.Frame(main_frame)
        stop_frame.pack(fill="x", pady=5)

        ttk.Label(stop_frame, text="紧急停止:", width=10).pack(side="left")
        self.stop_hotkey_var = tk.StringVar(value=self.app._format_hotkey(self.app.hotkey_stop))
        self.stop_hotkey_label = ttk.Label(stop_frame, textvariable=self.stop_hotkey_var,
                                            width=15, relief="sunken", anchor="center")
        self.stop_hotkey_label.pack(side="left", padx=5)

        self.set_stop_btn = ttk.Button(
            stop_frame,
            text="设置",
            command=self._start_recording_stop,
            width=8
        )
        self.set_stop_btn.pack(side="left", padx=5)

        # 提示信息
        ttk.Label(main_frame, text="点击「设置」后按下想要的快捷键组合",
                  font=("微软雅黑", 8), foreground="gray").pack(pady=10)

        # 关闭按钮
        ttk.Button(main_frame, text="关闭", command=self.dialog.destroy, width=10).pack(pady=5)

    def _start_recording_toggle(self):
        """开始录入开始/停止快捷键"""
        self.app.is_recording_toggle = True
        self.app.recorded_keys = set()
        self.toggle_hotkey_var.set("按下快捷键...")
        self.set_toggle_btn.config(state="disabled")
        self.set_stop_btn.config(state="disabled")

        # 设置回调以更新对话框
        self.app.on_recording_complete = self._on_toggle_complete

    def _on_toggle_complete(self):
        """录入开始/停止快捷键完成回调"""
        self.toggle_hotkey_var.set(self.app._format_hotkey(self.app.hotkey_toggle))
        self.set_toggle_btn.config(state="normal")
        self.set_stop_btn.config(state="normal")
        self.app.on_recording_complete = None

    def _start_recording_stop(self):
        """开始录入紧急停止快捷键"""
        self.app.is_recording_stop = True
        self.app.recorded_keys = set()
        self.stop_hotkey_var.set("按下快捷键...")
        self.set_toggle_btn.config(state="disabled")
        self.set_stop_btn.config(state="disabled")

        # 设置回调以更新对话框
        self.app.on_recording_complete = self._on_stop_complete

    def _on_stop_complete(self):
        """录入紧急停止快捷键完成回调"""
        self.stop_hotkey_var.set(self.app._format_hotkey(self.app.hotkey_stop))
        self.set_toggle_btn.config(state="normal")
        self.set_stop_btn.config(state="normal")
        self.app.on_recording_complete = None


class AutoClicker:
    """自动点击器主类"""

    def __init__(self, root):
        """
        初始化自动点击器

        Args:
            root: Tkinter 主窗口
        """
        self.root = root
        self.root.title("自动点击器")
        self.root.geometry("400x450")
        self.root.resizable(False, False)

        # 点击状态标志
        self.is_clicking = False
        # 定时器 ID，用于取消定时任务
        self.timer_id = None

        # 快捷键设置
        # 默认快捷键：F6 开始/停止（切换模式）
        self.hotkey_toggle = {keyboard.Key.f6}  # 开始/停止切换键
        self.hotkey_stop = {keyboard.Key.f7}    # 紧急停止键

        # 当前按下的键
        self.current_keys = set()

        # 快捷键录入状态
        self.is_recording_toggle = False
        self.is_recording_stop = False
        self.recorded_keys = set()
        self.on_recording_complete = None  # 录入完成回调

        # 创建菜单栏
        self._create_menu()

        # 创建界面组件
        self._create_widgets()

        # 启动键盘监听器
        self._start_keyboard_listener()

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="快捷键设置...", command=self._show_hotkey_dialog)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

    def _show_hotkey_dialog(self):
        """显示快捷键设置对话框"""
        HotkeyDialog(self.root, self)

    def _show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "自动点击器 v1.1\n\n"
            "一个简单的 Windows 自动鼠标点击工具\n\n"
            "默认快捷键:\n"
            "F6 - 开始/停止\n"
            "F7 - 紧急停止"
        )

    def _create_widgets(self):
        """创建所有界面组件"""

        # ========== 时间间隔设置区域 ==========
        interval_frame = ttk.LabelFrame(self.root, text="点击间隔设置", padding=10)
        interval_frame.pack(fill="x", padx=10, pady=5)

        # 间隔数值输入
        ttk.Label(interval_frame, text="间隔时间:").grid(row=0, column=0, sticky="w")
        self.interval_var = tk.StringVar(value="1000")
        self.interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=0, column=1, padx=5)

        # 时间单位选择
        self.unit_var = tk.StringVar(value="毫秒")
        unit_combo = ttk.Combobox(interval_frame, textvariable=self.unit_var,
                                   values=["毫秒", "秒"], width=6, state="readonly")
        unit_combo.grid(row=0, column=2)

        # ========== 点击类型设置区域 ==========
        click_type_frame = ttk.LabelFrame(self.root, text="点击类型", padding=10)
        click_type_frame.pack(fill="x", padx=10, pady=5)

        self.click_type_var = tk.StringVar(value="左键单击")

        # 使用单选按钮选择点击类型
        ttk.Radiobutton(click_type_frame, text="左键单击",
                        variable=self.click_type_var, value="左键单击").pack(anchor="w")
        ttk.Radiobutton(click_type_frame, text="右键单击",
                        variable=self.click_type_var, value="右键单击").pack(anchor="w")
        ttk.Radiobutton(click_type_frame, text="左键双击",
                        variable=self.click_type_var, value="左键双击").pack(anchor="w")

        # ========== 点击位置设置区域 ==========
        position_frame = ttk.LabelFrame(self.root, text="点击位置", padding=10)
        position_frame.pack(fill="x", padx=10, pady=5)

        # 位置模式选择
        self.use_current_pos_var = tk.BooleanVar(value=True)

        # 使用当前鼠标位置
        current_pos_check = ttk.Checkbutton(
            position_frame,
            text="使用当前鼠标位置",
            variable=self.use_current_pos_var,
            command=self._toggle_position_entry
        )
        current_pos_check.pack(anchor="w")

        # 固定坐标输入框架
        self.coord_frame = ttk.Frame(position_frame)
        self.coord_frame.pack(fill="x", pady=5)

        ttk.Label(self.coord_frame, text="X:").pack(side="left")
        self.x_var = tk.StringVar(value="0")
        self.x_entry = ttk.Entry(self.coord_frame, textvariable=self.x_var, width=8)
        self.x_entry.pack(side="left", padx=5)

        ttk.Label(self.coord_frame, text="Y:").pack(side="left")
        self.y_var = tk.StringVar(value="0")
        self.y_entry = ttk.Entry(self.coord_frame, textvariable=self.y_var, width=8)
        self.y_entry.pack(side="left", padx=5)

        # 获取当前坐标按钮
        self.get_pos_btn = ttk.Button(
            self.coord_frame,
            text="获取当前位置",
            command=self._get_current_position
        )
        self.get_pos_btn.pack(side="left", padx=5)

        # 初始状态下禁用坐标输入
        self._toggle_position_entry()

        # ========== 控制按钮区域 ==========
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        # 开始按钮
        self.start_btn = ttk.Button(
            control_frame,
            text="开始",
            command=self._start_clicking,
            width=15
        )
        self.start_btn.pack(side="left", padx=5, expand=True)

        # 停止按钮
        self.stop_btn = ttk.Button(
            control_frame,
            text="停止",
            command=self._stop_clicking,
            width=15,
            state="disabled"
        )
        self.stop_btn.pack(side="right", padx=5, expand=True)

        # ========== 状态显示区域 ==========
        status_frame = ttk.LabelFrame(self.root, text="当前状态", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)

        self.status_var = tk.StringVar(value="已停止")
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("微软雅黑", 12, "bold")
        )
        self.status_label.pack()

        # 点击计数
        self.click_count = 0
        self.count_var = tk.StringVar(value="点击次数: 0")
        ttk.Label(status_frame, textvariable=self.count_var).pack()

        # 快捷键提示
        self.hotkey_hint_var = tk.StringVar()
        self._update_hotkey_hint()
        ttk.Label(status_frame, textvariable=self.hotkey_hint_var,
                  font=("微软雅黑", 8), foreground="gray").pack()

        # ========== 提示信息 ==========
        tip_label = ttk.Label(
            self.root,
            text="提示: 将鼠标移到屏幕左上角可触发故障保护停止程序",
            font=("微软雅黑", 8),
            foreground="gray"
        )
        tip_label.pack(pady=5)

    def _update_hotkey_hint(self):
        """更新快捷键提示"""
        toggle_key = self._format_hotkey(self.hotkey_toggle)
        stop_key = self._format_hotkey(self.hotkey_stop)
        self.hotkey_hint_var.set(f"快捷键: {toggle_key} 开始/停止, {stop_key} 紧急停止")

    def _format_hotkey(self, keys):
        """
        格式化快捷键为可读字符串

        Args:
            keys: 按键集合

        Returns:
            str: 格式化后的快捷键字符串
        """
        if not keys:
            return "未设置"

        key_names = []
        for key in keys:
            if isinstance(key, keyboard.Key):
                # 特殊键
                name = key.name.upper()
                # 美化一些常见键名
                name_map = {
                    'CTRL_L': 'Ctrl',
                    'CTRL_R': 'Ctrl',
                    'ALT_L': 'Alt',
                    'ALT_R': 'Alt',
                    'SHIFT_L': 'Shift',
                    'SHIFT_R': 'Shift',
                    'CMD': 'Win',
                    'CMD_L': 'Win',
                    'CMD_R': 'Win',
                }
                name = name_map.get(name, name.replace('_', ' ').title())
                key_names.append(name)
            elif isinstance(key, keyboard.KeyCode):
                # 普通字符键
                if key.char:
                    key_names.append(key.char.upper())
                elif key.vk:
                    key_names.append(f"VK{key.vk}")

        return " + ".join(sorted(key_names))

    def _start_keyboard_listener(self):
        """启动键盘监听器"""
        def on_press(key):
            # 添加按键到当前按下的键集合
            self.current_keys.add(key)

            # 如果正在录入快捷键
            if self.is_recording_toggle or self.is_recording_stop:
                self.recorded_keys.add(key)
                return

            # 检查是否匹配快捷键
            self._check_hotkeys()

        def on_release(key):
            # 如果正在录入快捷键，释放时完成录入
            if self.is_recording_toggle and self.recorded_keys:
                self._finish_recording_toggle()
            elif self.is_recording_stop and self.recorded_keys:
                self._finish_recording_stop()

            # 从当前按下的键中移除
            self.current_keys.discard(key)

        # 创建并启动监听器（在后台线程中运行）
        self.keyboard_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def _check_hotkeys(self):
        """检查当前按下的键是否匹配快捷键"""
        # 标准化当前按键集合（处理左右修饰键）
        normalized_current = self._normalize_keys(self.current_keys)
        normalized_toggle = self._normalize_keys(self.hotkey_toggle)
        normalized_stop = self._normalize_keys(self.hotkey_stop)

        # 检查紧急停止快捷键（优先级更高）
        if normalized_current == normalized_stop:
            # 使用 after 在主线程中执行，确保线程安全
            self.root.after(0, self._stop_clicking)
        # 检查开始/停止切换快捷键
        elif normalized_current == normalized_toggle:
            self.root.after(0, self._toggle_clicking)

    def _normalize_keys(self, keys):
        """
        标准化按键集合，将左右修饰键统一

        Args:
            keys: 按键集合

        Returns:
            frozenset: 标准化后的按键集合
        """
        normalized = set()
        for key in keys:
            if isinstance(key, keyboard.Key):
                # 统一左右修饰键
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
        """切换点击状态（开始/停止）"""
        if self.is_clicking:
            self._stop_clicking()
        else:
            self._start_clicking()

    def _finish_recording_toggle(self):
        """完成录入开始/停止快捷键"""
        if self.recorded_keys:
            self.hotkey_toggle = self.recorded_keys.copy()

        self.is_recording_toggle = False
        self.recorded_keys = set()

        # 更新状态栏提示
        self._update_hotkey_hint()

        # 调用回调（如果有）
        if self.on_recording_complete:
            self.root.after(0, self.on_recording_complete)

    def _finish_recording_stop(self):
        """完成录入紧急停止快捷键"""
        if self.recorded_keys:
            self.hotkey_stop = self.recorded_keys.copy()

        self.is_recording_stop = False
        self.recorded_keys = set()

        # 更新状态栏提示
        self._update_hotkey_hint()

        # 调用回调（如果有）
        if self.on_recording_complete:
            self.root.after(0, self.on_recording_complete)

    def _toggle_position_entry(self):
        """切换坐标输入框的启用/禁用状态"""
        if self.use_current_pos_var.get():
            # 使用当前鼠标位置，禁用坐标输入
            self.x_entry.config(state="disabled")
            self.y_entry.config(state="disabled")
            self.get_pos_btn.config(state="disabled")
        else:
            # 使用固定坐标，启用坐标输入
            self.x_entry.config(state="normal")
            self.y_entry.config(state="normal")
            self.get_pos_btn.config(state="normal")

    def _get_current_position(self):
        """获取当前鼠标位置并填入坐标框"""
        x, y = pyautogui.position()
        self.x_var.set(str(x))
        self.y_var.set(str(y))

    def _validate_inputs(self):
        """
        验证用户输入是否有效

        Returns:
            bool: 输入有效返回 True，否则返回 False
        """
        # 验证时间间隔
        try:
            interval = int(self.interval_var.get())
            if interval <= 0:
                raise ValueError("间隔必须大于 0")
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的时间间隔（正整数）")
            return False

        # 验证坐标（如果使用固定坐标）
        if not self.use_current_pos_var.get():
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
                if x < 0 or y < 0:
                    raise ValueError("坐标不能为负数")
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的坐标（非负整数）")
                return False

        return True

    def _get_interval_ms(self):
        """
        获取点击间隔（毫秒）

        Returns:
            int: 间隔时间（毫秒）
        """
        interval = int(self.interval_var.get())
        if self.unit_var.get() == "秒":
            interval *= 1000
        return interval

    def _perform_click(self):
        """执行一次鼠标点击"""
        if not self.is_clicking:
            return

        try:
            # 确定点击位置
            if self.use_current_pos_var.get():
                # 使用当前鼠标位置
                x, y = pyautogui.position()
            else:
                # 使用固定坐标
                x = int(self.x_var.get())
                y = int(self.y_var.get())

            # 根据点击类型执行相应操作
            click_type = self.click_type_var.get()
            if click_type == "左键单击":
                pyautogui.click(x, y, button='left')
            elif click_type == "右键单击":
                pyautogui.click(x, y, button='right')
            elif click_type == "左键双击":
                pyautogui.doubleClick(x, y)

            # 更新点击计数
            self.click_count += 1
            self.count_var.set(f"点击次数: {self.click_count}")

            # 安排下一次点击
            # 使用 tkinter 的 after() 方法，在主线程中定时执行
            # 这样可以避免多线程的复杂性和线程安全问题
            interval = self._get_interval_ms()
            self.timer_id = self.root.after(interval, self._perform_click)

        except pyautogui.FailSafeException:
            # 触发故障保护（鼠标移到左上角）
            self._stop_clicking()
            messagebox.showinfo("已停止", "检测到故障保护触发，自动点击已停止")
        except Exception as e:
            self._stop_clicking()
            messagebox.showerror("错误", f"点击时发生错误: {str(e)}")

    def _start_clicking(self):
        """开始自动点击"""
        # 验证输入
        if not self._validate_inputs():
            return

        # 设置点击状态
        self.is_clicking = True
        self.click_count = 0
        self.count_var.set("点击次数: 0")

        # 更新界面状态
        self.status_var.set("正在自动点击...")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        # 禁用设置选项，防止运行时修改
        self._set_controls_state("disabled")

        # 开始第一次点击
        self._perform_click()

    def _stop_clicking(self):
        """停止自动点击"""
        # 设置停止状态
        self.is_clicking = False

        # 取消定时器
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        # 更新界面状态
        self.status_var.set("已停止")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        # 重新启用设置选项
        self._set_controls_state("normal")
        # 根据复选框状态更新坐标输入框
        self._toggle_position_entry()

    def _set_controls_state(self, state):
        """
        设置控制组件的启用/禁用状态

        Args:
            state: "normal" 或 "disabled"
        """
        self.interval_entry.config(state=state)

    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()

    # 设置窗口图标（如果有的话）
    # root.iconbitmap("icon.ico")

    # 创建自动点击器应用
    app = AutoClicker(root)

    # 窗口关闭时的处理
    def on_closing():
        if app.is_clicking:
            app._stop_clicking()
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()
