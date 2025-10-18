"""
Model and prompt versioning for reproducibility
Tracks which version generated each recommendation
"""
import hashlib
from typing import Dict
from datetime import datetime
from .config import settings

class ModelVersioning:
    """Track model versions and prompt hashes"""
    
    @staticmethod
    def get_prompt_hash(prompt_template: str) -> str:
        """
        Generate SHA256 hash of prompt template
        
        Args:
            prompt_template: The prompt string
        
        Returns:
            8-character hash
        """
        full_hash = hashlib.sha256(prompt_template.encode()).hexdigest()
        return full_hash[:8]
    
    @staticmethod
    def add_version_info(
        result: dict,
        agent_name: str,
        prompt_template: str
    ) -> dict:
        """
        Add versioning metadata to agent output
        
        Args:
            result: Agent output dict
            agent_name: Name of agent (router, recommend, etc.)
            prompt_template: Prompt used
        
        Returns:
            Result with version info added
        """
        version_key = f"{agent_name}_version"
        version = getattr(settings, version_key, "v1.0")
        
        result['model_version'] = f"{agent_name}_{version}"
        result['prompt_hash'] = ModelVersioning.get_prompt_hash(prompt_template)
        result['generated_at'] = datetime.now().isoformat()
        
        return result

# Global instance
versioning = ModelVersioning()

