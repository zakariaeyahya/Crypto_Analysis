"""
Script to check CUDA/GPU configuration
"""
import torch
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_cuda_setup():
    """Check CUDA configuration"""
    logger.info("=" * 60)
    logger.info("CUDA/GPU CONFIGURATION CHECK")
    logger.info("=" * 60)
    
    # PyTorch version
    logger.info(f"PyTorch version: {torch.__version__}")
    
    # CUDA available
    cuda_available = torch.cuda.is_available()
    logger.info(f"CUDA available: {cuda_available}")
    
    if cuda_available:
        # Number of GPUs
        num_gpus = torch.cuda.device_count()
        logger.info(f"Number of GPUs: {num_gpus}")
        
        # Information about each GPU
        for i in range(num_gpus):
            logger.info(f"GPU {i}:")
            logger.info(f"   Name: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            logger.info(f"   Total memory: {props.total_memory / 1e9:.2f} GB")
            logger.info(f"   Compute Capability: {props.major}.{props.minor}")
        
        # Current GPU
        current_device = torch.cuda.current_device()
        logger.info(f"Current GPU: {current_device} ({torch.cuda.get_device_name(current_device)})")
        
        # CUDA version
        logger.info(f"CUDA version: {torch.version.cuda}")
        logger.info(f"cuDNN version: {torch.backends.cudnn.version()}")
        
        # Simple test
        logger.info("Testing GPU computation...")
        try:
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = torch.matmul(x, y)
            logger.info("   GPU computation successful!")
        except Exception as e:
            logger.error(f"   Error during GPU computation: {e}")
    else:
        logger.warning("CUDA is not available")
        logger.warning("   Code will use CPU (much slower)")
        logger.info("To install PyTorch with CUDA:")
        logger.info("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    logger.info("=" * 60)
    
    return cuda_available


if __name__ == "__main__":
    cuda_available = check_cuda_setup()
    sys.exit(0 if cuda_available else 1)






