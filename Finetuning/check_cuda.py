"""
Script pour vérifier la configuration CUDA/GPU
"""
import torch
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_cuda_setup():
    """Vérifier la configuration CUDA"""
    logger.info("=" * 60)
    logger.info("VERIFICATION DE LA CONFIGURATION CUDA/GPU")
    logger.info("=" * 60)
    
    # Version PyTorch
    logger.info(f"PyTorch version: {torch.__version__}")
    
    # CUDA disponible
    cuda_available = torch.cuda.is_available()
    logger.info(f"CUDA disponible: {cuda_available}")
    
    if cuda_available:
        # Nombre de GPUs
        num_gpus = torch.cuda.device_count()
        logger.info(f"Nombre de GPUs: {num_gpus}")
        
        # Informations sur chaque GPU
        for i in range(num_gpus):
            logger.info(f"GPU {i}:")
            logger.info(f"   Nom: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            logger.info(f"   Memoire totale: {props.total_memory / 1e9:.2f} GB")
            logger.info(f"   Compute Capability: {props.major}.{props.minor}")
        
        # GPU actuel
        current_device = torch.cuda.current_device()
        logger.info(f"GPU actuel: {current_device} ({torch.cuda.get_device_name(current_device)})")
        
        # Version CUDA
        logger.info(f"Version CUDA: {torch.version.cuda}")
        logger.info(f"Version cuDNN: {torch.backends.cudnn.version()}")
        
        # Test simple
        logger.info("Test de calcul sur GPU...")
        try:
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = torch.matmul(x, y)
            logger.info("   Calcul GPU reussi!")
        except Exception as e:
            logger.error(f"   Erreur lors du calcul GPU: {e}")
    else:
        logger.warning("CUDA n'est pas disponible")
        logger.warning("   Le code utilisera le CPU (beaucoup plus lent)")
        logger.info("Pour installer PyTorch avec CUDA:")
        logger.info("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    logger.info("=" * 60)
    
    return cuda_available


if __name__ == "__main__":
    cuda_available = check_cuda_setup()
    sys.exit(0 if cuda_available else 1)





