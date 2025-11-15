"""
Configuration Management for AXA Startup Filter

Centralizes all configuration with support for:
- Environment variables
- YAML/JSON config files  
- Runtime validation
- Type safety with dataclasses
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
import json
import yaml
from pathlib import Path


@dataclass
class LLMConfig:
    """LLM-specific configuration"""
    enabled: bool = True
    provider: str = "nvidia_nim"
    model: str = "deepseek-ai/deepseek-r1"
    temperature: float = 0.3
    max_tokens: int = 300
    timeout: int = 60
    
    # Confidence thresholds
    min_confidence_accept: int = 70
    min_confidence_reject: int = 70
    edge_case_confidence: int = 50
    
    # Multi-model settings
    use_multi_model_consensus: bool = False
    consensus_models: list = field(default_factory=lambda: [
        "deepseek-ai/deepseek-r1",
        "meta/llama-3.1-70b-instruct"
    ])


@dataclass
class FilteringConfig:
    """Filtering thresholds and criteria"""
    min_score: int = 50
    min_funding_millions: float = 0
    min_employees: int = 0
    
    # Scoring weights
    weight_rule_match: float = 1.0
    weight_funding: float = 1.0
    weight_company_size: float = 0.8
    weight_maturity: float = 0.6
    
    # Enable/disable features
    use_hard_exclusions: bool = True
    use_llm_assessment: bool = True
    use_mcp_enrichment: bool = False
    
    # Industry-specific settings
    industry_specific_prompts: bool = False


@dataclass
class PerformanceConfig:
    """Performance and concurrency settings"""
    max_parallel_llm: int = 3
    batch_size: int = 5
    enable_cache: bool = True
    cache_ttl_seconds: int = 86400  # 24 hours
    
    # Rate limiting
    max_requests_per_minute: int = 60
    backoff_factor: float = 1.5
    max_retries: int = 3
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_fail_threshold: int = 5
    circuit_breaker_timeout: int = 60


@dataclass
class LoggingConfig:
    """Logging and observability settings"""
    level: str = "INFO"
    format: str = "json"  # "json" or "text"
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Log destinations
    log_to_file: bool = True
    log_file_path: str = "logs/axa_filter.log"
    log_to_stdout: bool = True
    log_to_datadog: bool = False


@dataclass
class AXAFilterConfig:
    """Master configuration for AXA startup filter"""
    # Sub-configs
    llm: LLMConfig = field(default_factory=LLMConfig)
    filtering: FilteringConfig = field(default_factory=FilteringConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # File paths
    input_file: str = "docs/architecture/ddbb/slush_full_list.json"
    output_file: Optional[str] = None
    keywords_config: str = "config/keywords.yaml"
    
    # Execution mode
    debug_mode: bool = False
    dry_run: bool = False
    
    @classmethod
    def from_env(cls) -> 'AXAFilterConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # LLM config from env
        config.llm.enabled = os.getenv('AXA_LLM_ENABLED', 'true').lower() == 'true'
        config.llm.provider = os.getenv('AXA_LLM_PROVIDER', 'nvidia_nim')
        config.llm.model = os.getenv('AXA_LLM_MODEL', 'deepseek-ai/deepseek-r1')
        config.llm.temperature = float(os.getenv('AXA_LLM_TEMPERATURE', '0.3'))
        
        # Performance config from env
        config.performance.max_parallel_llm = int(os.getenv('AXA_MAX_PARALLEL', '3'))
        config.performance.enable_cache = os.getenv('AXA_ENABLE_CACHE', 'true').lower() == 'true'
        config.performance.max_requests_per_minute = int(os.getenv('AXA_RATE_LIMIT', '60'))
        
        # Filtering config from env
        config.filtering.min_score = int(os.getenv('AXA_MIN_SCORE', '50'))
        
        # Logging config from env
        config.logging.level = os.getenv('AXA_LOG_LEVEL', 'INFO')
        config.logging.enable_metrics = os.getenv('AXA_METRICS_ENABLED', 'true').lower() == 'true'
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AXAFilterConfig':
        """Load configuration from YAML or JSON file"""
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AXAFilterConfig':
        """Create config from dictionary"""
        config = cls()
        
        # LLM config
        if 'llm' in data:
            for key, value in data['llm'].items():
                if hasattr(config.llm, key):
                    setattr(config.llm, key, value)
        
        # Filtering config
        if 'filtering' in data:
            for key, value in data['filtering'].items():
                if hasattr(config.filtering, key):
                    setattr(config.filtering, key, value)
        
        # Performance config
        if 'performance' in data:
            for key, value in data['performance'].items():
                if hasattr(config.performance, key):
                    setattr(config.performance, key, value)
        
        # Logging config
        if 'logging' in data:
            for key, value in data['logging'].items():
                if hasattr(config.logging, key):
                    setattr(config.logging, key, value)
        
        # Top-level config
        for key in ['input_file', 'output_file', 'debug_mode', 'dry_run']:
            if key in data:
                setattr(config, key, data[key])
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary"""
        return {
            'llm': {
                'enabled': self.llm.enabled,
                'provider': self.llm.provider,
                'model': self.llm.model,
                'temperature': self.llm.temperature,
                'max_tokens': self.llm.max_tokens,
                'timeout': self.llm.timeout,
            },
            'filtering': {
                'min_score': self.filtering.min_score,
                'min_funding_millions': self.filtering.min_funding_millions,
                'use_hard_exclusions': self.filtering.use_hard_exclusions,
                'use_llm_assessment': self.filtering.use_llm_assessment,
            },
            'performance': {
                'max_parallel_llm': self.performance.max_parallel_llm,
                'batch_size': self.performance.batch_size,
                'enable_cache': self.performance.enable_cache,
                'max_requests_per_minute': self.performance.max_requests_per_minute,
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'enable_metrics': self.logging.enable_metrics,
            },
            'input_file': self.input_file,
            'output_file': self.output_file,
            'debug_mode': self.debug_mode,
        }
    
    def save_to_file(self, config_path: str):
        """Save configuration to YAML file"""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(self.to_dict(), f, indent=2)
    
    def validate(self) -> bool:
        """Validate configuration values"""
        errors = []
        
        # Validate LLM config
        if self.llm.temperature < 0 or self.llm.temperature > 2:
            errors.append("LLM temperature must be between 0 and 2")
        
        if self.llm.max_tokens < 50 or self.llm.max_tokens > 4000:
            errors.append("LLM max_tokens must be between 50 and 4000")
        
        # Validate filtering config
        if self.filtering.min_score < 0 or self.filtering.min_score > 100:
            errors.append("Min score must be between 0 and 100")
        
        # Validate performance config
        if self.performance.max_parallel_llm < 1 or self.performance.max_parallel_llm > 20:
            errors.append("Max parallel LLM requests must be between 1 and 20")
        
        if self.performance.max_requests_per_minute < 1:
            errors.append("Max requests per minute must be at least 1")
        
        # Validate logging config
        if self.logging.level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            errors.append(f"Invalid log level: {self.logging.level}")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True


# Singleton instance
_config_instance: Optional[AXAFilterConfig] = None


def get_config() -> AXAFilterConfig:
    """Get singleton configuration instance"""
    global _config_instance
    
    if _config_instance is None:
        # Try to load from file first
        config_file = os.getenv('AXA_CONFIG_FILE', 'config/axa_filter_config.yaml')
        if Path(config_file).exists():
            _config_instance = AXAFilterConfig.from_file(config_file)
        else:
            # Fall back to environment variables
            _config_instance = AXAFilterConfig.from_env()
        
        # Validate configuration
        if not _config_instance.validate():
            raise ValueError("Invalid configuration")
    
    return _config_instance


def set_config(config: AXAFilterConfig):
    """Set singleton configuration instance"""
    global _config_instance
    _config_instance = config


# Example usage
if __name__ == '__main__':
    # Create default config
    config = AXAFilterConfig.from_env()
    
    print("Configuration loaded:")
    print(f"  LLM Provider: {config.llm.provider}")
    print(f"  LLM Model: {config.llm.model}")
    print(f"  Max Parallel: {config.performance.max_parallel_llm}")
    print(f"  Cache Enabled: {config.performance.enable_cache}")
    print(f"  Min Score: {config.filtering.min_score}")
    
    # Save to file
    config.save_to_file('config/axa_filter_config.yaml')
    print("\nConfiguration saved to config/axa_filter_config.yaml")
