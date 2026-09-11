#!/usr/bin/env python3
"""
Bullet Cards — Doomsday Western Edition
Auto launcher: checks dependencies, then runs the game.
"""
import subprocess
import sys
import os

def check_pygame():
    try:
        import pygame
        return True
    except ImportError:
        return False

def install_pygame():
    print("Installing pygame...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])

def main():
    if not check_pygame():
        try:
            install_pygame()
        except Exception as e:
            print(f"Auto-install failed: {e}")
            print("Please run manually: pip install pygame")
            sys.exit(1)
    # Switch to script directory (ensures assets/ is found)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    # Run the game
    import game_v2
    game_v2.main()

if __name__ == "__main__":
    main()
