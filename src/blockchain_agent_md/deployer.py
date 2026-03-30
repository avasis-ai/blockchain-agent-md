"""Blockchain deployment utilities."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class DeploymentConfig:
    """Configuration for smart contract deployment."""
    network: str
    rpc_url: str
    chain_id: int
    deployer_address: str
    private_key: Optional[str] = None
    gas_limit: Optional[int] = None
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "network": self.network,
            "rpc_url": self.rpc_url,
            "chain_id": self.chain_id,
            "deployer_address": self.deployer_address,
            "private_key": self.private_key[:8] + "..." if self.private_key else None,
            "gas_limit": self.gas_limit,
            "max_fee_per_gas": self.max_fee_per_gas,
            "max_priority_fee_per_gas": self.max_priority_fee_per_gas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeploymentConfig':
        """Create from dictionary."""
        return cls(
            network=data["network"],
            rpc_url=data["rpc_url"],
            chain_id=data["chain_id"],
            deployer_address=data["deployer_address"],
            private_key=data.get("private_key"),
            gas_limit=data.get("gas_limit"),
            max_fee_per_gas=data.get("max_fee_per_gas"),
            max_priority_fee_per_gas=data.get("max_priority_fee_per_gas")
        )


class ContractDeployer:
    """Handles smart contract deployment."""
    
    VALID_NETWORKS = ["mainnet", "sepolia", "goerli", "polygon", "arbitrum", "optimism", "local"]
    
    def __init__(self):
        """Initialize deployer."""
        self._deployments: List[Dict[str, Any]] = []
    
    def validate_config(self, config: DeploymentConfig) -> Tuple[bool, List[str]]:
        """
        Validate deployment configuration.
        
        Args:
            config: Deployment configuration
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Validate network
        if config.network not in self.VALID_NETWORKS:
            errors.append(f"Invalid network: {config.network}")
        
        # Validate RPC URL format
        if not re.match(r'https://[\w.-]+', config.rpc_url):
            errors.append("Invalid RPC URL format")
        
        # Validate chain ID
        if config.chain_id <= 0:
            errors.append("Chain ID must be positive")
        
        # Validate deployer address format (basic check)
        if not re.match(r'^0x[0-9a-fA-F]{40}$', config.deployer_address):
            errors.append("Invalid deployer address format")
        
        # Validate gas limit if provided
        if config.gas_limit and config.gas_limit <= 0:
            errors.append("Gas limit must be positive")
        
        # Validate fee parameters
        if config.max_fee_per_gas and config.max_fee_per_gas <= 0:
            errors.append("Max fee per gas must be positive")
        
        if config.max_priority_fee_per_gas and config.max_priority_fee_per_gas <= 0:
            errors.append("Max priority fee must be positive")
        
        return len(errors) == 0, errors
    
    def simulate_deployment(self, contract_code: str, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Simulate deployment (dry run).
        
        Args:
            contract_code: Contract source code
            config: Deployment configuration
            
        Returns:
            Simulation results
        """
        # Validate configuration
        is_valid, errors = self.validate_config(config)
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "simulation_type": "validation_failed"
            }
        
        # Basic simulation checks
        issues = []
        
        # Check contract size
        bytecode_estimate = len(contract_code) * 1.5  # Rough estimate
        if bytecode_estimate > 24576:  # EVM contract size limit
            issues.append("Contract too large for deployment")
        
        # Check for potential gas issues
        if 'external.call' in contract_code.lower() or 'transfer(' in contract_code.lower():
            issues.append("External calls may consume high gas")
        
        # Check for optimization opportunities
        optimization_suggestions = []
        if contract_code.count('require(') > 10:
            optimization_suggestions.append("Consider consolidating require statements")
        if len(contract_code) > 5000:
            optimization_suggestions.append("Large contract may benefit from modularization")
        
        return {
            "success": True,
            "estimated_gas": int(bytecode_estimate * 1000),
            "issues": issues,
            "optimization_suggestions": optimization_suggestions,
            "simulation_type": "successful"
        }
    
    def generate_deployment_report(self, contract_name: str, success: bool, 
                                   transaction_hash: Optional[str] = None,
                                   address: Optional[str] = None,
                                   gas_used: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate deployment report.
        
        Args:
            contract_name: Name of deployed contract
            success: Whether deployment was successful
            transaction_hash: Transaction hash (if successful)
            address: Contract address (if successful)
            gas_used: Gas used (if successful)
            
        Returns:
            Deployment report
        """
        report = {
            "contract_name": contract_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "transaction_hash": transaction_hash,
            "contract_address": address,
            "gas_used": gas_used
        }
        
        if success:
            report["status"] = "deployed"
        else:
            report["status"] = "failed"
        
        self._deployments.append(report)
        return report
    
    def get_deployment_history(self) -> List[Dict[str, Any]]:
        """Get deployment history."""
        return self._deployments.copy()
    
    def clear_deployment_history(self) -> None:
        """Clear deployment history."""
        self._deployments = []
