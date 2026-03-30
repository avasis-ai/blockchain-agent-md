"""Tests for blockchain agent."""

import pytest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from blockchain_agent_md.auditor import (
    SmartContractAuditor,
    SecurityLevel,
    SecurityIssue,
    AuditReport
)
from blockchain_agent_md.deployer import (
    ContractDeployer,
    DeploymentConfig
)


class TestSmartContractAuditor:
    """Tests for SmartContractAuditor."""
    
    def test_initialization(self):
        """Test auditor initialization."""
        auditor = SmartContractAuditor()
        
        assert len(auditor.get_issues()) == 0
        assert len(auditor.get_history()) == 0
    
    def test_audit_clean_contract(self):
        """Test audit with clean contract."""
        auditor = SmartContractAuditor()
        
        clean_contract = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;
        
        contract CleanContract {
            uint256 public value;
            
            function setValue(uint256 _value) public {
                value = _value;
            }
        }
        """
        
        report = auditor.audit_contract(clean_contract, "CleanContract")
        
        assert report.contract_name == "CleanContract"
        assert report.pass_reentrancy_check is True
        assert len(report.issues) == 0
    
    def test_audit_reentrancy_vulnerability(self):
        """Test audit with reentrancy vulnerability."""
        auditor = SmartContractAuditor()
        
        vulnerable_contract = """
        pragma solidity ^0.8.0;
        
        contract VulnerableContract {
            mapping(address => uint) public balances;
            
            function withdraw(uint256 amount) external {
                require(balances[msg.sender] >= amount);
                
                // External call without reentrancy guard
                (bool success, ) = msg.sender.call{value: amount}("");
                require(success);
                
                balances[msg.sender] -= amount;
            }
        }
        """
        
        report = auditor.audit_contract(vulnerable_contract, "VulnerableContract")
        
        assert report.contract_name == "VulnerableContract"
        assert report.pass_reentrancy_check is False
        assert len(report.issues) > 0
        assert any(issue.severity in [SecurityLevel.MEDIUM, SecurityLevel.HIGH] 
                   for issue in report.issues)
    
    def test_audit_mathematical_error(self):
        """Test audit with mathematical vulnerability."""
        auditor = SmartContractAuditor()
        
        math_vulnerable_contract = """
        pragma solidity ^0.8.0;
        
        contract MathVulnerableContract {
            function divide(uint256 a, uint256 b) external pure returns (uint256) {
                // Potential division by zero
                return a / b;
            }
        }
        """
        
        report = auditor.audit_contract(math_vulnerable_contract, "MathVulnerableContract")
        
        assert report.contract_name == "MathVulnerableContract"
        assert len(report.issues) > 0
    
    def test_audit_passes_protection(self):
        """Test audit with protection patterns."""
        auditor = SmartContractAuditor()
        
        protected_contract = """
        pragma solidity ^0.8.0;
        
        contract ProtectedContract {
            mapping(address => uint) public balances;
            
            // Reentrancy guard
            function withdraw(uint256 amount) external nonReentrant {
                require(balances[msg.sender] >= amount);
                
                (bool success, ) = msg.sender.call{value: amount}("");
                require(success);
                
                balances[msg.sender] -= amount;
            }
        }
        """
        
        report = auditor.audit_contract(protected_contract, "ProtectedContract")
        
        assert report.contract_name == "ProtectedContract"
        assert report.pass_reentrancy_check is True
    
    def test_audit_summary(self):
        """Test audit summary generation."""
        auditor = SmartContractAuditor()
        
        contract = """
        pragma solidity ^0.8.0;
        
        contract TestContract {
            function test() external {
                // Multiple issues
            }
        }
        """
        
        report = auditor.audit_contract(contract, "TestContract")
        
        # Summary should have correct counts
        total_issues = sum(report.summary.values())
        assert total_issues == len(report.issues)


class TestContractDeployer:
    """Tests for ContractDeployer."""
    
    def test_initialization(self):
        """Test deployer initialization."""
        deployer = ContractDeployer()
        
        assert len(deployer.get_deployment_history()) == 0
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        deployer = ContractDeployer()
        
        config = DeploymentConfig(
            network="sepolia",
            rpc_url="https://sepolia.infura.io/v3/api-key",
            chain_id=11155111,
            deployer_address="0x1234567890123456789012345678901234567890"
        )
        
        is_valid, errors = deployer.validate_config(config)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_invalid_network(self):
        """Test validation with invalid network."""
        deployer = ContractDeployer()
        
        config = DeploymentConfig(
            network="invalid_network",
            rpc_url="https://example.com",
            chain_id=1,
            deployer_address="0x1234567890123456789012345678901234567890"
        )
        
        is_valid, errors = deployer.validate_config(config)
        
        assert is_valid is False
        assert any("Invalid network" in error for error in errors)
    
    def test_validate_invalid_rpc_url(self):
        """Test validation with invalid RPC URL."""
        deployer = ContractDeployer()
        
        config = DeploymentConfig(
            network="local",
            rpc_url="invalid_url",
            chain_id=1,
            deployer_address="0x1234567890123456789012345678901234567890"
        )
        
        is_valid, errors = deployer.validate_config(config)
        
        assert is_valid is False
        assert any("Invalid RPC URL" in error for error in errors)
    
    def test_validate_invalid_deployer_address(self):
        """Test validation with invalid deployer address."""
        deployer = ContractDeployer()
        
        config = DeploymentConfig(
            network="local",
            rpc_url="https://example.com",
            chain_id=1,
            deployer_address="invalid_address"
        )
        
        is_valid, errors = deployer.validate_config(config)
        
        assert is_valid is False
        assert any("Invalid deployer address" in error for error in errors)
    
    def test_validate_invalid_chain_id(self):
        """Test validation with invalid chain ID."""
        deployer = ContractDeployer()
        
        config = DeploymentConfig(
            network="local",
            rpc_url="https://example.com",
            chain_id=0,
            deployer_address="0x1234567890123456789012345678901234567890"
        )
        
        is_valid, errors = deployer.validate_config(config)
        
        assert is_valid is False
        assert any("Chain ID must be positive" in error for error in errors)
    
    def test_simulate_deployment(self):
        """Test deployment simulation."""
        deployer = ContractDeployer()
        
        config = DeploymentConfig(
            network="sepolia",
            rpc_url="https://sepolia.infura.io/v3/api-key",
            chain_id=11155111,
            deployer_address="0x1234567890123456789012345678901234567890"
        )
        
        result = deployer.simulate_deployment("contract code here", config)
        
        assert result["success"] is True
        assert "estimated_gas" in result
    
    def test_simulate_deployment_validation_fail(self):
        """Test deployment simulation with invalid config."""
        deployer = ContractDeployer()
        
        config = DeploymentConfig(
            network="invalid",
            rpc_url="bad_url",
            chain_id=-1,
            deployer_address="bad_address"
        )
        
        result = deployer.simulate_deployment("contract code", config)
        
        assert result["success"] is False
        assert result["simulation_type"] == "validation_failed"
    
    def test_generate_deployment_report(self):
        """Test deployment report generation."""
        deployer = ContractDeployer()
        
        report = deployer.generate_deployment_report(
            contract_name="TestContract",
            success=True,
            transaction_hash="0x123abc",
            address="0x456def",
            gas_used=150000
        )
        
        assert report["contract_name"] == "TestContract"
        assert report["success"] is True
        assert report["status"] == "deployed"
        assert len(deployer.get_deployment_history()) == 1
    
    def test_deployment_history(self):
        """Test deployment history tracking."""
        deployer = ContractDeployer()
        
        # First deployment
        report1 = deployer.generate_deployment_report(
            contract_name="Contract1",
            success=True
        )
        
        # Second deployment
        report2 = deployer.generate_deployment_report(
            contract_name="Contract2",
            success=False
        )
        
        history = deployer.get_deployment_history()
        
        assert len(history) == 2
        assert history[0]["contract_name"] == "Contract1"
        assert history[1]["contract_name"] == "Contract2"
    
    def test_clear_deployment_history(self):
        """Test clearing deployment history."""
        deployer = ContractDeployer()
        
        # Add some deployments
        deployer.generate_deployment_report("Contract1", True)
        deployer.generate_deployment_report("Contract2", True)
        
        assert len(deployer.get_deployment_history()) == 2
        
        # Clear history
        deployer.clear_deployment_history()
        
        assert len(deployer.get_deployment_history()) == 0


class TestSecurityIssues:
    """Tests for SecurityIssue."""
    
    def test_issue_creation(self):
        """Test creating security issue."""
        issue = SecurityIssue(
            id="TEST-001",
            title="Test Issue",
            severity=SecurityLevel.LOW,
            description="Test description",
            location="Contract.sol:line 10",
            recommendation="Fix this issue",
            cwe_id="CWE-123"
        )
        
        assert issue.id == "TEST-001"
        assert issue.severity == SecurityLevel.LOW
        assert issue.cwe_id == "CWE-123"
    
    def test_issue_to_dict(self):
        """Test converting issue to dictionary."""
        issue = SecurityIssue(
            id="TEST-002",
            title="Test Issue",
            severity=SecurityLevel.MEDIUM,
            description="Test",
            location="Contract.sol:10",
            recommendation="Fix"
        )
        
        data = issue.to_dict()
        
        assert data["id"] == "TEST-002"
        assert data["severity"] == "medium"
        assert data["location"] == "Contract.sol:10"


class TestSecurityLevel:
    """Tests for SecurityLevel enum."""
    
    def test_severity_values(self):
        """Test security level values."""
        assert SecurityLevel.INFO.value == "info"
        assert SecurityLevel.LOW.value == "low"
        assert SecurityLevel.MEDIUM.value == "medium"
        assert SecurityLevel.HIGH.value == "high"
        assert SecurityLevel.CRITICAL.value == "critical"


class TestDeploymentConfig:
    """Tests for DeploymentConfig."""
    
    def test_config_creation(self):
        """Test creating deployment config."""
        config = DeploymentConfig(
            network="sepolia",
            rpc_url="https://example.com",
            chain_id=11155111,
            deployer_address="0x1234567890123456789012345678901234567890"
        )
        
        assert config.network == "sepolia"
        assert config.chain_id == 11155111
        assert config.gas_limit is None
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "network": "local",
            "rpc_url": "http://localhost:8545",
            "chain_id": 1337,
            "deployer_address": "0x1234567890123456789012345678901234567890"
        }
        
        config = DeploymentConfig.from_dict(data)
        
        assert config.network == "local"
        assert config.chain_id == 1337
        assert config.private_key is None
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = DeploymentConfig(
            network="local",
            rpc_url="http://localhost:8545",
            chain_id=1337,
            deployer_address="0x1234567890123456789012345678901234567890"
        )
        
        data = config.to_dict()
        
        assert data["network"] == "local"
        assert "rpc_url" in data
        assert "chain_id" in data


class TestAuditReport:
    """Tests for AuditReport."""
    
    def test_report_creation(self):
        """Test creating audit report."""
        report = AuditReport(
            contract_name="TestContract",
            audit_timestamp=datetime.now(),
            issues=[],
            pass_reentrancy_check=True,
            pass_mathematical_proof=True,
            summary={
                "info": 0,
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            }
        )
        
        assert report.contract_name == "TestContract"
        assert report.pass_reentrancy_check is True
        assert report.pass_mathematical_proof is True
        assert report.audit_timestamp is not None
    
    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        report = AuditReport(
            contract_name="TestContract",
            audit_timestamp=datetime.now(),
            issues=[],
            pass_reentrancy_check=True,
            pass_mathematical_proof=True,
            summary={"info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
        )
        
        data = report.to_dict()
        
        assert data["contract_name"] == "TestContract"
        assert "audit_timestamp" in data
        assert "issues" in data
        assert "pass_reentrancy_check" in data
