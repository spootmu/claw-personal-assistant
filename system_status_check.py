import sys
import os
sys.path.insert(0, r'F:\AIP\claw-personal-assistant')

print("Checking Claw Personal Assistant system status...")
try:
    # Test importing core modules
    import claw_main
    print("[OK] claw_main module imported successfully")
    
    import database
    print("[OK] database module imported successfully")
    
    import learning_system
    print("[OK] learning_system module imported successfully")
    
    import community_integration
    print("[OK] community_integration module imported successfully")
    
    import tasks.intelligent_scheduler
    print("[OK] intelligent_scheduler module imported successfully")
    
    import tasks.task_manager
    print("[OK] task_manager module imported successfully")
    
    print("\n[System Status] All core modules are accessible and ready")
    print("[Next Steps] Ready to apply community insights and optimizations")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
except Exception as e:
    print(f"[ERROR] Error: {e}")