#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程与软件 - Page 4
"""

import flet as ft

CARD_BG = "#1a1a3e"
ACCENT  = "#4a9eff"
GREEN   = "#34a853"
GRAY    = "#888888"


def build_page(data: dict) -> list:
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
    for name, mem in data.get('proc_top10', []):
        proc_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor="#12122a", margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Text(name, size=12, color="#FFFFFF", width=150),
                ft.Text(f"{mem:,} KB", size=12, color=ACCENT, weight=ft.FontWeight.W_600),
                ft.Container(expand=True),
                ft.Container(
                    height=6, width=80, border_radius=3, bgcolor="#2d2d5a",
                    content=ft.Stack([
                        ft.Container(width=80, height=6, border_radius=3, bgcolor=ACCENT),
                    ]),
                ),
            ], spacing=8),
        ))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text('📊 内存 Top10 进程', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
             ft.Divider(height=12, color=CARD_BG)] + proc_items,
            spacing=4,
        ),
    ))

    # 启动项
    if data.get('startup_items'):
        startup_items = []
        for item in data.get('startup_items', []):
            startup_items.append(ft.Container(
                padding=8, border_radius=8, bgcolor="#12122a", margin=ft.Margin.only(bottom=4),
                content=ft.Column([
                    ft.Text(item.get('name',''), size=12, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                    ft.Text(item.get('cmd',''), size=10, color=GRAY, max_lines=2),
                ], spacing=2),
            ))

        cards.append(ft.Container(
            padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column(
                [ft.Text(f'🚀 启动项 ({len(startup_items)})', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                 ft.Divider(height=12, color=CARD_BG)] + startup_items,
                spacing=4,
            ),
        ))

    # 计划任务
    if data.get('sched_tasks'):
        task_items = []
        for t in data.get('sched_tasks', []):
            task_items.append(ft.Container(
                padding=8, border_radius=8, bgcolor="#12122a", margin=ft.Margin.only(bottom=4),
                content=ft.Column([
                    ft.Row([
                        ft.Text(t.get('name',''), size=12, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                        ft.Container(expand=True),
                        ft.Container(
                            padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                            border_radius=6, bgcolor="#4a9eff",
                            content=ft.Text(t.get('state',''), size=10, color="#FFFFFF"),
                        ),
                    ]),
                    ft.Text(t.get('action','')[:80], size=10, color=GRAY),
                ], spacing=2),
            ))

        cards.append(ft.Container(
            padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column(
                [ft.Text(f'📅 计划任务 ({len(task_items)})', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                 ft.Divider(height=12, color=CARD_BG)] + task_items,
                spacing=4,
            ),
        ))

    # 已安装软件
    software = data.get('software', [])
    sw_items = []
    for s in software[:30]:
        sw_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor="#12122a", margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Column([
                    ft.Text(s.get('name',''), size=12, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                    ft.Text(f"{s.get('version','')}  |  {s.get('publisher','')[:30]}", size=10, color=GRAY),
                ], spacing=1, tight=True),
                ft.Container(expand=True),
                ft.Text(s.get('install_date',''), size=10, color=GRAY),
            ], spacing=8),
        ))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text(f'📦 已安装软件 ({len(software)} 个)', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
             ft.Divider(height=12, color=CARD_BG)] + sw_items +
            ([ft.Text(f'... 共 {len(software)} 个，显示前30条', size=11, color=GRAY)] if len(software) > 30 else []),
            spacing=4,
        ),
    ))

    # 最近补丁
    update_items = []
    for u in data.get('updates', []):
        update_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor="#12122a", margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Container(
                    padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                    border_radius=6, bgcolor="#2a2a5a",
                    content=ft.Text(u.get('id',''), size=11, color=ACCENT, weight=ft.FontWeight.W_600),
                ),
                ft.Text(u.get('type',''), size=11, color=GRAY),
                ft.Container(expand=True),
                ft.Text(u.get('date',''), size=10, color=GRAY),
            ], spacing=8),
        ))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text(f'🔧 最近补丁 ({len(update_items)})', size=15, weight=ft.FontWeight.W_600, color="#FFFFFF"),
             ft.Divider(height=12, color=CARD_BG)] + update_items,
            spacing=4,
        ),
    ))

    return cards
