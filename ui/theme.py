#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主题配置 — 颜色方案"""

import os
import json

CONFIG_PATH = os.path.expanduser("~/.windows_inspection_tool/config.json")

# 默认颜色
DEFAULTS = {
    "primary_text": "#ffffff",
    "secondary_text": "#888888",
    "accent": "#4a9eff",
    "green": "#34a853",
    "yellow": "#f9ab00",
    "red": "#ea4335",
    "card_bg": "#1B2838",
    "dark_bg": "#0A0F1A",
}

# 预设主题
PRESETS = {
    "dark": {
        "name": "深色",
        "primary_text": "#ffffff",
        "secondary_text": "#888888",
        "accent": "#4a9eff",
        "green": "#34a853",
        "yellow": "#f9ab00",
        "red": "#ea4335",
        "card_bg": "#1B2838",
        "dark_bg": "#0A0F1A",
    },
    "light": {
        "name": "浅色",
        "primary_text": "#1a1a1a",
        "secondary_text": "#666666",
        "accent": "#0066cc",
        "green": "#2e8b57",
        "yellow": "#d4a017",
        "red": "#cc3300",
        "card_bg": "#f5f5f5",
        "dark_bg": "#e8e8e8",
    },
    "eye_care": {
        "name": "护眼绿",
        "primary_text": "#e8f0e8",
        "secondary_text": "#8fa88f",
        "accent": "#7cb87c",
        "green": "#5fa55f",
        "yellow": "#c4b030",
        "red": "#c06030",
        "card_bg": "#2a3a2a",
        "dark_bg": "#1a251a",
    },
}


def load_theme() -> dict:
    """加载主题配置，返回配色dict"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULTS.copy()


def save_theme(colors: dict):
    """保存主题配置"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(colors, f, indent=2)


def get_preset(name: str) -> dict:
    """获取预设主题"""
    return PRESETS.get(name, PRESETS["dark"]).copy()