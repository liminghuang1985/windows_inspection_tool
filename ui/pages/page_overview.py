#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
概览仪表盘 - Page 1
"""

import flet as ft

DARK_BG = "#0f0f23"
CARD_BG = "#1a1a3e"
ACCENT  = "#4a9eff"
GREEN   = "#34a853"
YELLOW  = "#f9ab00"
RED     = "#ea4335"
GRAY    = "#888888"


def build_page(data: dict) -> list:
    """返回页面组件列表"""

    # 风险级别
    risks = data.get('risks', [])
    high_risks = [r for r in risks if r[0] == '高']
    med_risks  = [r for r in risks if r[0] == '中']
    risk_level = '高' if high_risks else '中' if med_risks else '低'
    risk_color = RED if risk_level == '高' else YELLOW if risk_level == '中' else GREEN

    # 内存百分比
    mem_pct = float(data.get('mem_pct', 0))
    mem_color = GREEN if mem_pct < 70 else YELLOW if mem_pct < 90 else RED

    # CPU负载
    cpu_load = float(data.get('cpu_load', 0) or 0)
    cpu_color = GREEN if cpu_load < 70 else YELLOW if cpu_load < 90 else RED

    cards = []

    # 概览卡片 - 主机名/OS/风险等级
    cards.append(ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text(data.get('hostname', 'N/A'), size=24, weight=ft.FontWeight.W_700, color=ft.colors.WHITE),
                    ft.Text(data.get('os', 'N/A'), size=13, color=GRAY),
                ], spacing=4),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    border_radius=12,
                    bgcolor=risk_color,
                    content=ft.Text(f'⚠️ {risk_level}风险', size=16, weight=ft.FontWeight.W_700, color=ft.colors.WHITE),
                ),
            ]),
            ft.Divider(height=20, color=CARD_BG),
            ft.Row([
                ft.Column([ft.Text('运行时间', size=11, color=GRAY), ft.Text(data.get('uptime', 'N/A'), size=13, color=ft.colors.WHITE)], spacing=2),
                ft.Container(expand=True),
                ft.Column([ft.Text('当前用户', size=11, color=GRAY), ft.Text(data.get('user', 'N/A'), size=13, color=ft.colors.WHITE)], spacing=2),
                ft.Container(expand=True),
                ft.Column([ft.Text('许可证', size=11, color=GRAY), ft.Text(f"{data.get('license_status','N/A')} ({data.get('license_type','N/A')})", size=13, color=ft.colors.WHITE)], spacing=2),
            ]),
        ], spacing=0),
        padding=20, border_radius=16, bgcolor=CARD_BG,
    ))

    # CPU/内存卡片（双列）
    cards.append(ft.Row([
        ft.Container(
            expand=1, padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column([
                ft.Text('💻 CPU负载', size=13, color=GRAY),
                ft.Text(f"{cpu_load:.0f}%", size=28, weight=ft.FontWeight.W_700, color=cpu_color),
                ft.Container(
                    height=8, border_radius=4,
                    bgcolor="#2d2d5a",
                    content=ft.Stack([
                        ft.Container(width=max(cpu_load, 2), height=8, border_radius=4, bgcolor=cpu_color),
                    ]),
                ),
                ft.Text(data.get('cpu_name', 'N/A')[:40], size=10, color=GRAY),
            ], spacing=6),
        ),
        ft.Container(width=10),
        ft.Container(
            expand=1, padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column([
                ft.Text('🧠 内存', size=13, color=GRAY),
                ft.Text(f"{mem_pct:.1f}%", size=28, weight=ft.FontWeight.W_700, color=mem_color),
                ft.Container(
                    height=8, border_radius=4,
                    bgcolor="#2d2d5a",
                    content=ft.Stack([
                        ft.Container(width=max(mem_pct, 2), height=8, border_radius=4, bgcolor=mem_color),
                    ]),
                ),
                ft.Text(f"{data.get('mem_used', 0):.1f} / {data.get('mem_total', 0):.1f} GB", size=10, color=GRAY),
            ], spacing=6),
        ),
    ]))

    # 磁盘卡片
    disk_items = []
    for disk in data.get('disks', []):
        pct = float(disk.get('pct', 0))
        color = GREEN if pct < 70 else YELLOW if pct < 90 else RED
        disk_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor="#12122a", margin=ft.margin.only(bottom=6),
            content=ft.Row([
                ft.Column([ft.Text(disk.get('drive',''), size=14, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)], spacing=0),
                ft.Column([ft.Text(disk.get('label','N/A'), size=10, color=GRAY), ft.Text(f"{disk.get('free','N/A')}GB 可用", size=10, color=GRAY)], spacing=0, tight=True),
                ft.Container(expand=True),
                ft.Text(f"{pct:.1f}%", size=14, weight=ft.FontWeight.W_700, color=color),
            ], spacing=8),
        ))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([ft.Text('💾 磁盘', size=15, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)] + disk_items, spacing=4),
    ))

    # 风险告警列表
    risk_items = []
    for level, desc in risks:
        color = RED if level == '高' else YELLOW
        risk_items.append(ft.Container(
            padding=10, border_radius=8, bgcolor="#12122a", margin=ft.margin.only(bottom=6),
            content=ft.Row([
                ft.Container(
                    width=8, height=8, border_radius=4, bgcolor=color,
                ),
                ft.Text(desc, size=12, color=ft.colors.WHITE),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    border_radius=6, bgcolor=color,
                    content=ft.Text(level, size=10, weight=ft.FontWeight.W_700, color=ft.colors.WHITE),
                ),
            ], spacing=8),
        ))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text(f'🚨 风险告警 ({len(risks)})', size=15, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)] +
            (risk_items if risk_items else [ft.Text('未发现风险项 ✓', size=12, color=GREEN)]),
            spacing=4,
        ),
    ))

    return cards
