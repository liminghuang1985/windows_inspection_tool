#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程与软件 - Page 4
"""

import flet as ft
from ui.theme import load_theme


def build_page(data: dict, theme: dict = None) -> list:
    if theme is None:
        theme = load_theme()

    GRAY = theme.get("secondary_text", "#888888")
    GREEN = theme.get("green", "#34a853")
    YELLOW = theme.get("yellow", "#f9ab00")
    RED = theme.get("red", "#ea4335")
    ACCENT = theme.get("accent", "#4a9eff")
    CARD_BG = theme.get("card_bg", "#1B2838")
    DARK_BG = theme.get("dark_bg", "#0A0F1A")
    TEXT_PRI = theme.get("primary_text", "#ffffff")

    cards = []

    # 进程/服务统计
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Row([
            ft.Column([
                ft.Text(f"{data.get('proc_count', 'N/A')}", size=28, weight=ft.FontWeight.W_700, color=ACCENT),
                ft.Text('进程总数', size=11, color=GRAY),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(expand=True),
            ft.Column([
                ft.Text(f"{data.get('svc_running', 'N/A')}", size=28, weight=ft.FontWeight.W_700, color=ACCENT),
                ft.Text('运行服务', size=11, color=GRAY),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(expand=True),
            ft.Column([
                ft.Text(f"{len(data.get('startup_items', []))}", size=28, weight=ft.FontWeight.W_700, color=ACCENT),
                ft.Text('启动项', size=11, color=GRAY),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(expand=True),
            ft.Column([
                ft.Text(f"{len(data.get('sched_tasks', []))}", size=28, weight=ft.FontWeight.W_700, color=ACCENT),
                ft.Text('计划任务', size=11, color=GRAY),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=0),
    ))

    # 内存Top10进程
    proc_items = []
    proc_list = data.get('proc_top10', [])
    for i, (name, mem) in enumerate(proc_list):
        proc_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Text(name, size=12, color=TEXT_PRI, width=150),
                ft.Text(f"{mem:,} KB", size=12, color=ACCENT, weight=ft.FontWeight.W_600),
                ft.Container(expand=True),
                ft.Container(
                    height=6, width=80, border_radius=3, bgcolor="#2A3A4A",
                    content=ft.Stack([
                        ft.Container(width=80, height=6, border_radius=3, bgcolor=ACCENT),
                    ]),
                ),
            ], spacing=8),
        ))
        if i < len(proc_list) - 1:
            proc_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text('📊 内存 Top10 进程', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
             ft.Divider(height=12, color=CARD_BG)] + proc_items,
            spacing=4,
        ),
    ))

    # 启动项
    if data.get('startup_items'):
        startup_items = []
        startup_list = data.get('startup_items', [])
        for i, item in enumerate(startup_list):
            startup_items.append(ft.Container(
                padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
                content=ft.Column([
                    ft.Text(item.get('name',''), size=12, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                    ft.Text(item.get('cmd',''), size=10, color=GRAY, max_lines=2),
                ], spacing=2),
            ))
            if i < len(startup_list) - 1:
                startup_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

        cards.append(ft.Container(
            padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column(
                [ft.Text(f'🚀 启动项 ({len(startup_list)})', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                 ft.Divider(height=12, color=CARD_BG)] + startup_items,
                spacing=4,
            ),
        ))

    # 计划任务
    if data.get('sched_tasks'):
        task_items = []
        task_list = data.get('sched_tasks', [])
        for i, t in enumerate(task_list):
            task_items.append(ft.Container(
                padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
                content=ft.Column([
                    ft.Row([
                        ft.Text(t.get('name',''), size=12, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                        ft.Container(expand=True),
                        ft.Container(
                            padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                            border_radius=6, bgcolor=ACCENT,
                            content=ft.Text(t.get('state',''), size=10, color=TEXT_PRI),
                        ),
                    ]),
                    ft.Text(t.get('action','')[:80], size=10, color=GRAY),
                ], spacing=2),
            ))
            if i < len(task_list) - 1:
                task_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

        cards.append(ft.Container(
            padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column(
                [ft.Text(f'📅 计划任务 ({len(task_list)})', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                 ft.Divider(height=12, color=CARD_BG)] + task_items,
                spacing=4,
            ),
        ))

    # 已安装软件
    software = data.get('software', [])
    sw_items = []
    sw_display = software[:30]
    for i, s in enumerate(sw_display):
        sw_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Column([
                    ft.Text(s.get('name',''), size=12, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                    ft.Text(f"{s.get('version','')}  |  {s.get('publisher','')[:30]}", size=10, color=GRAY),
                ], spacing=1, tight=True),
                ft.Container(expand=True),
                ft.Text(s.get('install_date',''), size=10, color=GRAY),
            ], spacing=8),
        ))
        if i < len(sw_display) - 1:
            sw_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text(f'📦 已安装软件 ({len(software)} 个)', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
             ft.Divider(height=12, color=CARD_BG)] + sw_items +
            ([ft.Text(f'... 共 {len(software)} 个，显示前30条', size=11, color=GRAY)] if len(software) > 30 else []),
            spacing=4,
        ),
    ))

    # 最近补丁
    update_items = []
    update_list = data.get('updates', [])
    for i, u in enumerate(update_list):
        update_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Container(
                    padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                    border_radius=6, bgcolor="#2A3A4A",
                    content=ft.Text(u.get('id',''), size=11, color=ACCENT, weight=ft.FontWeight.W_600),
                ),
                ft.Text(u.get('type',''), size=11, color=GRAY),
                ft.Container(expand=True),
                ft.Text(u.get('date',''), size=10, color=GRAY),
            ], spacing=8),
        ))
        if i < len(update_list) - 1:
            update_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text(f'🔧 最近补丁 ({len(update_list)})', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
             ft.Divider(height=12, color=CARD_BG)] + update_items,
            spacing=4,
        ),
    ))

    return cards