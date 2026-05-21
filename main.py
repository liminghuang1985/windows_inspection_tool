#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 系统巡检工具 - Flet GUI
"""

import flet as ft
import sys
import threading
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inspector.collector import collect_all
from inspector.reporter import generate_html, save_html_report
from ui.pages import page_overview, page_hardware, page_security, page_processes

# ==================== 主题配置 ====================
DARK_BG  = "#0A0F1A"
CARD_BG  = "#1B2838"
ACCENT   = "#4a9eff"
TEXT_PRI = "#ffffff"
TEXT_SEC = "#888888"

PAGE_TABS = [
    ("概览", "🏠"),
    ("硬件网络", "💻"),
    ("安全用户", "🛡️"),
    ("进程软件", "📊"),
]


class InspectionApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Windows 系统巡检工具"
        self.page.window_width = 1100
        self.page.window_height = 750
        self.page.window_resizable = False
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.spacing = 0

        self.data = None
        self.loading = False
        self.tab_index = 0

        self._build_ui()
        # 启动时自动采集
        self._run_inspection()

    def _build_ui(self):
        """构建UI"""
        # 顶部TabBar
        self.tab_buttons = []
        self.tab_row = ft.Container(
            padding=ft.Padding.only(left=16, right=16, top=8, bottom=8),
            bgcolor=DARK_BG,
            content=ft.Row(self._make_tab_buttons(), spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

        # 页面内容区
        self.content_area = ft.Container(
            expand=True,
            padding=15,
            bgcolor=DARK_BG,
        )

        # 底部状态栏
        self.status_bar = ft.Container(
            padding=ft.Padding.only(left=16, right=16, top=6, bottom=6),
            bgcolor="#0A0F1A",
            content=ft.Row([
                self.status_text("就绪"),
                ft.Container(expand=True),
                ft.Text("Windows 系统巡检工具 v1.0", size=11, color=TEXT_SEC),
            ]),
        )

        self.page.add(self.tab_row, self.content_area, self.status_bar)

    def _make_tab_buttons(self):
        buttons = []
        for i, (label, icon) in enumerate(PAGE_TABS):
            is_selected = (i == self.tab_index)
            btn = ft.Container(
                padding=ft.Padding.only(left=20, right=20, top=10, bottom=10),
                border_radius=ft.BorderRadius(topLeft=10, topRight=10, bottomLeft=0, bottomRight=0),
                bgcolor="#1B2838" if is_selected else "transparent",
                on_click=lambda e, idx=i: self._switch_tab(idx),
                content=ft.Column([
                    ft.Row([
                        ft.Text(icon, size=16),
                        ft.Text(label, size=14, weight=ft.FontWeight.W_700 if is_selected else ft.FontWeight.W_600,
                                color="#FFFFFF" if is_selected else TEXT_SEC),
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            )
            buttons.append(btn)
            self.tab_buttons.append(btn)
            # 添加 | 分隔符（非最后一项）
            if i < len(PAGE_TABS) - 1:
                sep = ft.Container(
                    width=1,
                    bgcolor="#2A3A4A",
                    margin=ft.Margin.only(top=10, bottom=10),
                )
                buttons.append(sep)
        return buttons

    def _switch_tab(self, index: int):
        """切换Tab"""
        self.tab_index = index
        # 重建Tab按钮以更新选中样式
        self.tab_buttons = []
        self.tab_row.content = ft.Row(self._make_tab_buttons(), spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self._render_page()
        self.page.update()

    def _render_page(self):
        """渲染当前页面"""
        if self.loading or self.data is None:
            return

        page_map = {
            0: page_overview,
            1: page_hardware,
            2: page_security,
            3: page_processes,
        }
        page_fn = page_map.get(self.tab_index, page_overview)
        widgets = page_fn.build_page(self.data)

        self.content_area.content = ft.ListView(
            controls=widgets,
            spacing=12,
            padding=5,
            expand=True,
        )

    def _show_loading(self, message: str = "采集中..."):
        """显示加载状态"""
        self.loading = True
        self.content_area.content = ft.Container(
            expand=True,
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, color=ACCENT),
                ft.Text(message, size=14, color=TEXT_SEC),
            ], spacing=16, alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.Alignment(0.5, 0.5),
        )
        self.page.update()

    def status_text(self, msg: str):
        return ft.Text(msg, size=12, color=TEXT_SEC)

    def _update_status(self, msg: str):
        self.status_bar.content.controls[0] = self.status_text(msg)
        self.page.update()

    def _run_inspection(self):
        """后台运行巡检"""
        self._show_loading("正在巡检，请稍候...")
        self._update_status("采集中...")

        def bg():
            try:
                self.data = collect_all()
                # 采集完成后渲染
                def done():
                    self.loading = False
                    self._update_status(f"巡检完成 · {self.data.get('_meta',{}).get('timestamp','')}")
                    self._render_page()
                    self.page.update()
                    # 自动生成报告
                    try:
                        path = save_html_report(self.data)
                        self._update_status(f"巡检完成 · 报告已保存到桌面: {os.path.basename(path)}")
                    except Exception as e:
                        self._update_status(f"巡检完成 · 报告保存失败: {e}")
                    self.page.update()
                self.page.run_thread(done)
            except Exception as e:
                def err():
                    self.loading = False
                    self.content_area.content = ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Text("❌ 巡检失败", size=16, color="#ea4335"),
                            ft.Text(str(e), size=12, color=TEXT_SEC),
                            ft.Container(height=20),
                            ft.ElevatedButton("重新巡检", on_click=lambda _: self._run_inspection(), bgcolor=ACCENT),
                        ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                        alignment=ft.Alignment(0.5, 0.5),
                    )
                    self._update_status("巡检失败")
                    self.page.update()
                self.page.run_thread(err)

        t = threading.Thread(target=bg, daemon=True)
        t.start()

    def refresh(self):
        """重新巡检"""
        self._run_inspection()


def main(page: ft.Page):
    app = InspectionApp(page)


if __name__ == "__main__":
    # 添加刷新按钮到窗口菜单
    if len(sys.argv) > 1 and sys.argv[1] == "--refresh":
        # CLI 模式刷新
        data = collect_all()
        save_html_report(data)
        print("巡检完成")
    else:
        # GUI 模式
        ft.app(target=main, assets_dir="assets")
