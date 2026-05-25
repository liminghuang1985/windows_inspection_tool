#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全与用户 - Page 3
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

    # 防火墙状态
    fw_items = []
    for i, (name, status) in enumerate([('域网络', data.get('fw_domain', 'OFF')), ('专用网络', data.get('fw_private', 'OFF')), ('公用网络', data.get('fw_public', 'OFF'))]):
        on = status == 'ON'
        color = GREEN if on else RED
        fw_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Text(name, size=12, color=TEXT_PRI),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.Padding.only(left=12, right=12, top=3, bottom=3),
                    border_radius=6, bgcolor=color,
                    content=ft.Text(status, size=11, weight=ft.FontWeight.W_700, color=TEXT_PRI),
                ),
            ], spacing=8),
        ))
        if i < 2:
            fw_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text('🛡️ 防火墙状态', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI)] + fw_items,
            spacing=4,
        ),
    ))

    # RDP状态
    rdp_color = YELLOW if data.get('rdp_enabled') == '已启用' else GREEN
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🖥️ 远程桌面(RDP)', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('RDP状态', data.get('rdp_enabled', 'N/A'), GRAY, TEXT_PRI, badge=data.get('rdp_enabled',''), badge_color=rdp_color),
            _info_row('NLA保护', data.get('rdp_nla', 'N/A'), GRAY, TEXT_PRI),
            _info_row('端口', data.get('rdp_port', '3389'), GRAY, TEXT_PRI),
        ], spacing=0),
    ))

    # BitLocker
    bl_on = data.get('bitlocker_available', False)
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🔐 BitLocker 加密', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('状态', '已启用' if bl_on else '未启用/不可用', GRAY, TEXT_PRI, badge='已启用' if bl_on else '未启用', badge_color=GREEN if bl_on else GRAY),
        ], spacing=0),
    ))

    # Defender
    def_status = data.get('defender_on', 'N/A')
    def_color = GREEN if def_status == '已启用' else RED
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('🦠 Windows Defender', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('防病毒', def_status, GRAY, TEXT_PRI, badge=def_status, badge_color=def_color),
            _info_row('实时保护', data.get('defender_rtp', 'N/A'), GRAY, TEXT_PRI),
            _info_row('引擎版本', data.get('defender_version', 'N/A'), GRAY, TEXT_PRI),
            _info_row('最后更新', data.get('defender_updated', 'N/A'), GRAY, TEXT_PRI),
        ], spacing=0),
    ))

    # 时间同步
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('⏰ 时间同步', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            _info_row('服务状态', data.get('time_sync', 'N/A'), GRAY, TEXT_PRI),
            _info_row('时间源', data.get('time_source', 'N/A'), GRAY, TEXT_PRI),
        ], spacing=0),
    ))

    # 密码策略
    pw_items = []
    for k, v in data.get('pw_policy', {}).items():
        pw_items.append(_info_row(k, v, GRAY, TEXT_PRI))
    if pw_items:
        cards.append(ft.Container(
            padding=16, border_radius=16, bgcolor=CARD_BG,
            content=ft.Column(
                [ft.Text('🔑 密码策略', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                 ft.Divider(height=12, color=CARD_BG)] + pw_items,
                spacing=0,
            ),
        ))

    # 本地用户
    user_items = []
    for i, u in enumerate(data.get('local_users', [])):
        en = u.get('enabled', 'N/A') == 'True'
        en_color = GREEN if en else RED
        user_items.append(ft.Container(
            padding=8, border_radius=8, bgcolor=CARD_BG, margin=ft.Margin.only(bottom=4),
            content=ft.Row([
                ft.Text(u.get('name',''), size=13, weight=ft.FontWeight.W_600, color=TEXT_PRI),
                ft.Container(expand=True),
                ft.Text(f"最后登录: {u.get('lastlogon','N/A')}", size=10, color=GRAY),
                ft.Container(
                    padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                    border_radius=6, bgcolor=en_color,
                    content=ft.Text('已启用' if en else '已禁用', size=10, color=TEXT_PRI),
                ),
            ], spacing=8),
        ))
        if i < len(data.get('local_users', [])) - 1:
            user_items.append(ft.Container(height=1, bgcolor="#2A3A4A", margin=ft.Margin.only(bottom=4)))

    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column(
            [ft.Text(f'👤 本地用户 ({len(user_items)})', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI)] + user_items,
            spacing=4,
        ),
    ))

    # 管理员组
    cards.append(ft.Container(
        padding=16, border_radius=16, bgcolor=CARD_BG,
        content=ft.Column([
            ft.Text('👥 管理员组成员', size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI),
            ft.Divider(height=12, color=CARD_BG),
            ft.Text(data.get('admin_members', 'N/A'), size=12, color=TEXT_PRI),
        ], spacing=0),
    ))

    return cards


def _info_row(label: str, value: str, gray: str, text_pri: str, badge: str = None, badge_color: str = None) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.only(top=5, bottom=5),
        content=ft.Row([
            ft.Text(label, size=12, color=gray, width=100),
            ft.Text(str(value), size=12, color=text_pri),
            ft.Container(expand=True),
            ft.Container(
                padding=ft.Padding.only(left=8, right=8, top=2, bottom=2),
                border_radius=6, bgcolor=badge_color or gray,
                content=ft.Text(badge or '', size=10, color=text_pri),
            ) if badge else ft.Container(),
        ], spacing=8),
    )