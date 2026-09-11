"""
Download all game assets (21 images) to the local assets/ directory.
Run this if assets are missing: python download_assets.py
"""
import urllib.request
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(ASSET_DIR, exist_ok=True)

ASSETS = {
    # ── Playing Cards (bullet suit) ──
    'card_1.png': 'https://aka.doubaocdn.com/s/Y8ItThxUb7',
    'card_2.png': 'https://aka.doubaocdn.com/s/RkKeDHh3vn',
    'card_3.png': 'https://aka.doubaocdn.com/s/eOBqm7lTP1',
    'card_4.png': 'https://aka.doubaocdn.com/s/Uy8UsVQuGS',
    'card_5.png': 'https://aka.doubaocdn.com/s/bcdYbR8stO',
    'card_6.png': 'https://aka.doubaocdn.com/s/dxFjQodnCI',
    'card_back.png': 'https://aka.doubaocdn.com/s/uLeTofpjYD',
    # ── Snake Character (Player 1) ──
    'snake_normal.png': 'https://aka.doubaocdn.com/s/48dchQSMnn',
    'snake_scared.png': 'https://aka.doubaocdn.com/s/6GwaAqay3k',
    'snake_dead.png': 'https://aka.doubaocdn.com/s/UziAGgDS32',
    'snake_survivor.png': 'https://aka.doubaocdn.com/s/yqF7H9Pudc',
    'snake_victory.png': 'https://aka.doubaocdn.com/s/Nzw4K2kmIa',
    # ── Lizard Character (Player 2) ──
    'lizard_normal.png': 'https://aka.doubaocdn.com/s/rd1UUx8IJp',
    'lizard_scared.png': 'https://aka.doubaocdn.com/s/k8fCjM5Sp1',
    'lizard_dead.png': 'https://aka.doubaocdn.com/s/Bp0CMq1WVD',
    'lizard_survivor.png': 'https://aka.doubaocdn.com/s/iQpeLorDS8',
    'lizard_victory.png': 'https://aka.doubaocdn.com/s/8ciyurMh36',
    # ── Atmosphere / Props ──
    'dealer_owl.png': 'https://aka.doubaocdn.com/s/ptLC259Yv4',
    'roulette_cylinder.png': 'https://aka.doubaocdn.com/s/uUVezgaI3Y',
    'background_menu.png': 'https://aka.doubaocdn.com/s/KoznXpfA0J',
    'background_saloon.png': 'https://aka.doubaocdn.com/s/QV1cn3UdIG',
}

def main():
    total = len(ASSETS)
    success = 0
    failed = []
    print(f"Downloading {total} game assets to: {ASSET_DIR}\n")
    for filename, url in ASSETS.items():
        path = os.path.join(ASSET_DIR, filename)
        try:
            urllib.request.urlretrieve(url, path)
            size = os.path.getsize(path)
            print(f"  [OK] {filename:28s} ({size:>8,} bytes)")
            success += 1
        except Exception as e:
            print(f"  [FAIL] {filename}: {e}")
            failed.append(filename)
    print(f"\n{'='*50}")
    print(f"Download complete: {success}/{total} succeeded")
    if failed:
        print(f"Failed: {failed}")
        print("Try running the script again, or download manually.")
    else:
        print("All assets ready! Run 'python game_v2.py' to play.")

if __name__ == "__main__":
    main()
