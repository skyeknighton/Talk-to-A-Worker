# Sprites Directory

This directory contains sprite images for the "Talk To A Worker" game.

## Required Sprite Files:

- `player.png` - Player character sprite (32x32 recommended)
- `worker.png` - Worker character sprite (32x32 recommended)  
- `protestor.png` - Protesting worker sprite (32x32 recommended)
- `boss.png` - Boss character sprite (32x32 recommended)
- `background.png` - Background image (800x600 recommended)
- `pause.png` - Pause screen overlay (800x600 recommended)

## How to Add Custom Sprites:

1. Place your sprite images in this directory with the exact filenames listed above
2. Supported formats: PNG, JPG, GIF
3. The game will automatically scale sprites to the appropriate size
4. If a sprite file is missing, the game will use colored rectangles as fallbacks

## Fallback Colors:

- Player: Blue
- Worker: Green  
- Protestor: Yellow
- Boss: Red
- Background: Gray
- Pause Screen: Semi-transparent Gray

## Tips:

- Use transparent backgrounds (PNG) for better visual integration
- Keep sprites simple and recognizable at small sizes
- Test your sprites in the game to ensure they look good
- The pause screen sprite should be designed to overlay the game without completely obscuring it 