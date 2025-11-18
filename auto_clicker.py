#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动点击器 - Windows 桌面自动鼠标点击工具
使用 Tkinter GUI 和 pyautogui 实现
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui

# 禁用 pyautogui 的故障保护（可选，如果需要可以启用）
# pyautogui.FAILSAFE = False


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

        # 创建界面组件
        self._create_widgets()

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

        # ========== 提示信息 ==========
        tip_label = ttk.Label(
            self.root,
            text="提示: 将鼠标移到屏幕左上角可触发故障保护停止程序",
            font=("微软雅黑", 8),
            foreground="gray"
        )
        tip_label.pack(pady=5)

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
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()
