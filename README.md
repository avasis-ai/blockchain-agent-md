# README.md - Blockchain Agent MD

## The Verifiable, Open-Source Firewall Against Vulnerable Smart Contracts

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/blockchain-agent-md.svg)](https://pypi.org/project/blockchain-agent-md/)

**Blockchain Agent MD** equips agents with deep knowledge of Solidity/Rust security patterns, mandating strict reentrancy checks and mathematical proofs before the agent is allowed to deploy generated code to a testnet, preventing catastrophic hacks.

## 🎯 What It Does

This tool integrates formal verification checks directly into the agent's execution loop, providing mathematical guarantees of code safety and fundamentally outperforming probabilistic text generation for smart contract security.

### Example Use Case

```python
from blockchain_agent_md.auditor import SmartContractAuditor

# Initialize auditor
auditor = SmartContractAuditor()

# Audit contract
contract_code = """
pragma solidity ^0.8.0;

contract VulnerableContract {
    function withdraw(uint256 amount) external {
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
    }
}
"""

report = auditor.audit_contract(contract_code, "VulnerableContract")

print(f"Reentrancy protection: {report.pass_reentrancy_check}")
print(f"Issues found: {len(report.issues)}")
```

## 🚀 Features

- **Reentrancy Detection**: Identifies reentrancy vulnerabilities in smart contracts
- **Mathematical Safety**: Verifies overflow/underflow protection
- **Common Vulnerability Scanning**: Detects common smart contract security issues
- **Deployment Simulation**: Dry-run deployment analysis
- **Formal Verification**: Mathematical proofs of code safety
- **Comprehensive Reporting**: Detailed audit reports with severity levels

### Security Checks

1. **Reentrancy Guards**: Ensures proper protection against reentrancy attacks
2. **Mathematical Safety**: Verifies SafeMath patterns
3. **Return Value Checks**: Detects unchecked external call return values
4. **Initialization**: Identifies uninitialized variables

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- web3, PyYAML, Click for blockchain operations

### Install from PyPI

```bash
pip install blockchain-agent-md
```

### Install from Source

```bash
git clone https://github.com/avasis-ai/blockchain-agent-md.git
cd blockchain-agent-md
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
pip install pytest pytest-mock black isort
```

## 🔧 Usage

### Command-Line Interface

```bash
# Check version
blockchain-agent --version

# Audit contract for security issues
blockchain-agent audit MyContract.sol

# Simulate deployment
blockchain-agent deploy MyContract.sol \
    --network sepolia \
    --rpc-url https://sepolia.infura.io \
    --chain-id 11155111 \
    --deployer 0x123...456

# View history
blockchain-agent history

# Show configuration
blockchain-agent config
```

### Programmatic Usage

```python
from blockchain_agent_md.auditor import SmartContractAuditor, SecurityLevel
from blockchain_agent_md.deployer import ContractDeployer, DeploymentConfig

# Initialize auditor
auditor = SmartContractAuditor()

# Audit smart contract
contract_code = """
pragma solidity ^0.8.0;

contract SecureContract {
    function transfer(address to, uint256 amount) external {
        // Safe transfer
    }
}
"""

report = auditor.audit_contract(contract_code, "SecureContract")

# Check results
if report.pass_reentrancy_check and report.pass_mathematical_proof:
    print("✅ Contract passes security checks")
else:
    print("❌ Contract has security issues")
    for issue in report.issues:
        print(f"  {issue.severity.value}: {issue.title}")
        print(f"    Location: {issue.location}")

# Initialize deployer
deployer = ContractDeployer()

# Validate deployment config
config = DeploymentConfig(
    network="sepolia",
    rpc_url="https://sepolia.infura.io/v3/api-key",
    chain_id=11155111,
    deployer_address="0x1234567890123456789012345678901234567890",
    gas_limit=5000000
)

is_valid, errors = deployer.validate_config(config)

if is_valid:
    # Simulate deployment
    simulation = deployer.simulate_deployment(contract_code, config)
    print(f"Estimated gas: {simulation['estimated_gas']}")
else:
    print("Invalid configuration:")
    for error in errors:
        print(f"  - {error}")
```

## 📚 API Reference

### SmartContractAuditor

Auditor for smart contract security analysis.

#### `audit_contract(contract_code, contract_name)` → AuditReport

Audit smart contract for security vulnerabilities.

#### `get_issues()` → List[SecurityIssue]

Get all issues found in current audit.

#### `get_history()` → List[AuditReport]

Get audit history.

#### `clear_history()`

Clear audit history.

### ContractDeployer

Handles smart contract deployment simulation.

#### `validate_config(config)` → Tuple[bool, List[str]]

Validate deployment configuration.

#### `simulate_deployment(contract_code, config)` → Dict

Simulate contract deployment.

#### `get_deployment_history()` → List[Dict]

Get deployment history.

#### `clear_deployment_history()`

Clear deployment history.

## 🧪 Testing

Run tests with pytest:

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
blockchain-agent-md/
├── README.md
├── pyproject.toml
├── LICENSE
├── src/
│   └── blockchain_agent_md/
│       ├── __init__.py
│       ├── auditor.py
│       └── deployer.py
├── tests/
│   ├── test_auditor.py
│   └── test_deployer.py
└── .github/
    └── ISSUE_TEMPLATE/
        └── bug_report.md
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `python -m pytest tests/ -v`
5. **Submit a pull request**

### Development Setup

```bash
git clone https://github.com/avasis-ai/blockchain-agent-md.git
cd blockchain-agent-md
pip install -e ".[dev]"
pre-commit install
```

## 📝 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## 🎯 Vision

Blockchain Agent MD is an absolute necessity for secure smart contract development in 2026. It prevents massive, highly public financial disasters and lawsuits by mandating rigorous security checks before any deployment.

### Key Innovations

- **Formal Verification**: Mathematical guarantees of code safety
- **Reentrancy Protection**: Automatic detection of reentrancy vulnerabilities
- **Mathematical Safety**: Verification of overflow/underflow protection
- **Real-Time Analysis**: Instant security feedback during development
- **Comprehensive Metrics**: Multiple security dimensions for thorough checking

## 🌟 Impact

This tool enables:

- **Security**: Prevent catastrophic hacks before deployment
- **Formal Verification**: Mathematical proofs of code safety
- **Risk Reduction**: Catch vulnerabilities before they're exploited
- **Legal Protection**: Comprehensive audit trails for compliance
- **Trust**: Verified security in smart contracts
- **Institutional Adoption**: Meet enterprise security requirements

## 🛡️ Security & Trust

- **Trusted dependencies**: web3 (7.1), pyyaml (verified), click (8.8) - [Context7 verified](https://context7.com)
- **MIT License**: Open source, community-driven
- **Formal Verification**: Mathematical guarantees
- **Auditable**: Complete history of all security checks
- **Open Source**: Community-reviewed security

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/avasis-ai/blockchain-agent-md/wiki)
- **Issues**: [GitHub Issues](https://github.com/avasis-ai/blockchain-agent-md/issues)
- **Security**: Report security vulnerabilities to security@avasis.ai

## 🙏 Acknowledgments

- **Solidity Security Best Practices**: Community research
- **OpenZeppelin**: Security patterns inspiration
- **Smart Contract security community**: Shared knowledge and tools
- **Formal verification tools**: Halmos, KEVM inspiration

---

**Made with ❤️ by [Avasis AI](https://avasis.ai)**

*The essential firewall for secure smart contracts. Prevent hacks, ensure safety, build trust.*
