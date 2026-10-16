# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
        'pygame.transform',
        'engine.card_renderer',
        'engine.particles',
        'engine.sound',
        'engine.ui',
        'engine.visual_fx',
        'models.card',
        'models.enemy',
        'models.entity',
        'models.player',
        'models.potion',
        'models.relic',
        'models.status',
        'systems.combat',
        'systems.events',
        'systems.map_generator',
        'systems.reward',
        'systems.save_manager',
        'systems.shop',
        'views.char_select_view',
        'views.combat_view',
        'views.deck_view',
        'views.event_view',
        'views.game_over_view',
        'views.load_game_view',
        'views.map_view',
        'views.rest_view',
        'views.reward_view',
        'views.shop_view',
        'views.title_view',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CryptOfTheNecrolord',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets\\icon.ico',
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CryptOfTheNecrolord',
)
