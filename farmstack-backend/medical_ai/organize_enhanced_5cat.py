"""
Organize Enhanced 5-Category Dataset (12,432 images)
Date: 2025-11-05 16:16:12 UTC
User: Manishnm10

Creates proper 80/20 train/validation split for enhanced dataset
Input: data/skin_diseases_enhanced_5cat_complete/train/
Output: data/skin_diseases_phase1_enhanced_5cat/
"""

import os
import shutil
from pathlib import Path
import random
import json

def organize_enhanced_5cat():
    """Organize enhanced dataset with 80/20 split"""
    
    print("\n" + "="*70)
    print("📦 ORGANIZING ENHANCED 5-CATEGORY DATASET")
    print("="*70)
    print(f"⏰ Started: 2025-11-05 16:16:12 UTC")
    print(f"👤 User: Manishnm10")
    
    source_dir = Path('data/skin_diseases_enhanced_5cat_complete/train')
    target_dir = Path('data/skin_diseases_phase1_enhanced_5cat')
    
    train_split = 0.80  # 80% training, 20% validation
    random.seed(42)  # Reproducible split
    
    # Check source exists
    if not source_dir.exists():
        print(f"\n❌ ERROR: Source not found: {source_dir}")
        print("   Expected: data/skin_diseases_enhanced_5cat_complete/train/")
        return
    
    print(f"\n📂 Source: {source_dir.absolute()}")
    print(f"📂 Target: {target_dir.absolute()}")
    print(f"📊 Split:  {train_split*100:.0f}% train / {(1-train_split)*100:.0f}% validation")
    
    # Get categories
    categories = [d.name for d in source_dir.iterdir() if d.is_dir()]
    
    if not categories:
        print(f"\n❌ ERROR: No categories found in {source_dir}")
        return
    
    print(f"\n📝 Processing {len(categories)} categories:")
    for cat in sorted(categories):
        marker = " ⭐" if cat == 'dermatitis' else ""
        print(f"   • {cat}{marker}")
    
    stats = {}
    
    # Process each category
    for category in sorted(categories):
        print(f"\n{'='*70}")
        print(f"📁 {category.upper()}")
        if category == 'dermatitis':
            print("   ⭐ MERGED CATEGORY")
        print('='*70)
        
        # Get all images
        cat_source = source_dir / category
        images = list(cat_source.glob('*.*'))
        
        print(f"   Found: {len(images):,} images")
        
        if not images:
            print(f"   ⚠️  No images found, skipping...")
            continue
        
        # Shuffle for random split
        random.shuffle(images)
        
        # Calculate split
        split_idx = int(len(images) * train_split)
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        # Create directories
        train_dir = target_dir / 'train' / category
        val_dir = target_dir / 'validation' / category
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy training images
        print(f"\n   🔄 Copying training images...")
        for idx, img in enumerate(train_images):
            shutil.copy2(img, train_dir / img.name)
            if (idx + 1) % 1000 == 0:
                print(f"      Copied {idx + 1}/{len(train_images)}...")
        
        # Copy validation images
        print(f"   🔄 Copying validation images...")
        for idx, img in enumerate(val_images):
            shutil.copy2(img, val_dir / img.name)
            if (idx + 1) % 500 == 0:
                print(f"      Copied {idx + 1}/{len(val_images)}...")
        
        stats[category] = {
            'train': len(train_images),
            'validation': len(val_images),
            'total': len(images)
        }
        
        print(f"\n   ✅ {category}:")
        print(f"      Train: {len(train_images):,}")
        print(f"      Val:   {len(val_images):,}")
        print(f"      Total: {len(images):,}")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 ORGANIZATION COMPLETE!")
    print("="*70)
    
    print(f"\n{'Category':<15} {'Train':<10} {'Val':<10} {'Total':<10}")
    print("-"*50)
    
    total_train = 0
    total_val = 0
    total_all = 0
    
    for cat in sorted(stats.keys()):
        train = stats[cat]['train']
        val = stats[cat]['validation']
        total = stats[cat]['total']
        
        total_train += train
        total_val += val
        total_all += total
        
        marker = " ⭐" if cat == 'dermatitis' else ""
        print(f"{cat:<15} {train:<10,} {val:<10,} {total:<10,}{marker}")
    
    print("-"*50)
    print(f"{'TOTAL':<15} {total_train:<10,} {total_val:<10,} {total_all:<10,}")
    
    print("\n✅ DATASET READY:")
    print("-"*70)
    print(f"   Training samples:   {total_train:,} (80%)")
    print(f"   Validation samples: {total_val:,} (20%)")
    print(f"   Total samples:      {total_all:,}")
    
    print(f"\n📍 Location: {target_dir.absolute()}")
    
    # Save organization info
    org_info = {
        'timestamp': '2025-11-05 16:16:12 UTC',
        'user': 'Manishnm10',
        'total_images': total_all,
        'train_images': total_train,
        'val_images': total_val,
        'split_ratio': f'{train_split*100:.0f}/{(1-train_split)*100:.0f}',
        'categories': stats
    }
    
    with open(target_dir / 'dataset_info.json', 'w') as f:
        json.dump(org_info, f, indent=4)
    
    print(f"💾 Dataset info saved: {target_dir / 'dataset_info.json'}")
    
    print("\n🎯 NEXT STEP: TRAIN ENHANCED MODEL")
    print("="*70)
    print("\n1. Update training script DATA_DIR:")
    print("   notepad train_phase1_5categories.py")
    print("   Change line:")
    print("   DATA_DIR = 'data/skin_diseases_phase1_enhanced_5cat'")
    print("")
    print("2. Start training:")
    print("   python train_phase1_5categories.py")
    print("")
    print("3. Expected:")
    print("   • Training time: 3-4 hours")
    print("   • Expected accuracy: 72-79% 🎉🎉")
    print("   • Completion: ~20:00 UTC (Nov 5, 2025)")
    
    print("\n" + "="*70)
    print("✅ READY TO TRAIN ENHANCED MODEL!")
    print("="*70)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎯 ORGANIZE ENHANCED DATASET")
    print("="*70)
    print("\nThis will create 80/20 train/validation split")
    print("Source: 12,432 merged images")
    print("Output: Organized dataset ready for training")
    
    response = input("\n❓ Proceed with organization? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print("\n🔄 Starting organization...")
        print("   This will take 15-20 minutes")
        print("   Please wait...\n")
        
        organize_enhanced_5cat()
    else:
        print("\n❌ Cancelled.")