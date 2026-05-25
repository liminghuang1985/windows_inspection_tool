#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设置弹窗 — 主题配置"""

import flet as ft
from ..theme import PRESETS, DEFAULTS, load_theme, save_theme


class SettingsDialog:
    def __init__(self, page: ft.Page, on_theme_changed=None):
        self.page = page
        self.on_theme_changed = on_theme_changed
        self.current = load_theme()
        self._build()

    def _build(self):
        # 预设主题选择
        preset_buttons = []
        for key, preset in PRESETS.items():
            is_active = self._is_preset_active(key)
            btn = ft.Container(
                padding=8,
                border_radius=8,
                bgcolor="#2A3A4A" if is_active else "#1B2838",
                on_click=lambda e, k=key: self._select_preset(k),
                content=ft.Text(preset["name"], size=13, color="#FFFFFF"),
            )
            preset_buttons.append(btn)

        # 自定义颜色区域
        self.color_items = {}
        color_labels = {
            "primary_text": "主文字",
            "secondary_text": "次要文字",
            "accent": "强调色",
            "green": "绿色",
            "yellow": "黄色",
            "red": "红色",
            "card_bg": "卡片背景",
            "dark_bg": "页面背景",
        }
        for key, label in color_labels.items():
            color = self.current.get(key, DEFAULTS.get(key, "#888888"))
            self.color_items[key] = ft.ColorPicker(
                label=label,
                color=color,
                width=300,
            )

        color_pickers = [self.color_items[k] for k in color_labels.keys()]

        # 确认/取消按钮
        confirm_btn = ft.ElevatedButton(
            "确认",
            on_click=self._on_confirm,
            bgcolor="#4a9eff",
            color="#FFFFFF",
        )
        cancel_btn = ft.TextButton(
            "取消",
            on_click=self._on_cancel,
        )

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚙️ 主题设置", size=18, weight=ft.FontWeight.W_700),
            content=ft.Container(
                width=350,
                padding=10,
                content=ft.Column([
                    ft.Text("预设主题", size=14, weight=ft.FontWeight.W_600),
                    ft.Row(preset_buttons, spacing=8, wrap=True),
                    ft.Container(height=20),
                    ft.Text("自定义颜色", size=14, weight=ft.FontWeight.W_600),
                    ft.Container(height=5),
                    *color_pickers,
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
            ),
            actions=[
                cancel_btn,
                confirm_btn,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    @property
    def dlg(self):
        return self._dialog

    def _is_preset_active(self, key: str) -> bool:
        preset = PRESETS[key]
        return (
            self.current.get("primary_text") == preset.get("primary_text")
            and self.current.get("dark_bg") == preset.get("dark_bg")
        )

    def _select_preset(self, key: str):
        preset = PRESETS[key]
        # 更新color picker显示
        for k, picker in self.color_items.items():
            picker.color = preset.get(k, DEFAULTS.get(k, "#888888"))
        self._dialog.update()

    def _on_cancel(self, e):
        self._dialog.open = False
        self.page.update()

    def _on_confirm(self, e):
        # 收集当前颜色
        new_theme = {}
        for key, picker in self.color_items.items():
            new_theme[key] = picker.color
        save_theme(new_theme)
        if self.on_theme_changed:
            self.on_theme_changed(new_theme)
        self._dialog.open = False
        self.page.update()

    def show(self):
        self._dialog.open = True
        self.page.dialog = self._dialog
        self.page.update()