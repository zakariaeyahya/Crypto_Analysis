"""
Script pour vérifier la configuration CUDA/GPU
"""
import torch
import sys

def check_cuda_setup():
    """Vérifier la configuration CUDA"""
    print("=" * 60)
    print("VÉRIFICATION DE LA CONFIGURATION CUDA/GPU")
    print("=" * 60)
    
    # Version PyTorch
    print(f"\n📦 PyTorch version: {torch.__version__}")
    
    # CUDA disponible
    cuda_available = torch.cuda.is_available()
    print(f"\n🔧 CUDA disponible: {cuda_available}")
    
    if cuda_available:
        # Nombre de GPUs
        num_gpus = torch.cuda.device_count()
        print(f"🎮 Nombre de GPUs: {num_gpus}")
        
        # Informations sur chaque GPU
        for i in range(num_gpus):
            print(f"\n   GPU {i}:")
            print(f"      Nom: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            print(f"      Mémoire totale: {props.total_memory / 1e9:.2f} GB")
            print(f"      Compute Capability: {props.major}.{props.minor}")
        
        # GPU actuel
        current_device = torch.cuda.current_device()
        print(f"\n✅ GPU actuel: {current_device} ({torch.cuda.get_device_name(current_device)})")
        
        # Version CUDA
        print(f"🔧 Version CUDA: {torch.version.cuda}")
        print(f"🔧 Version cuDNN: {torch.backends.cudnn.version()}")
        
        # Test simple
        print("\n🧪 Test de calcul sur GPU...")
        try:
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = torch.matmul(x, y)
            print("   ✅ Calcul GPU réussi!")
        except Exception as e:
            print(f"   ❌ Erreur lors du calcul GPU: {e}")
    else:
        print("\n⚠️  CUDA n'est pas disponible")
        print("   Le code utilisera le CPU (beaucoup plus lent)")
        print("\n💡 Pour installer PyTorch avec CUDA:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    print("\n" + "=" * 60)
    
    return cuda_available


if __name__ == "__main__":
    cuda_available = check_cuda_setup()
    sys.exit(0 if cuda_available else 1)





