# AGENTS.md - Blockchain Agent MD Project Context

This folder is home. Treat it that way.

## Project: Blockchain-Agent MD (#50)

### Identity
- **Name**: Blockchain-Agent MD
- **License**: MIT
- **Org**: avasis-ai
- **PyPI**: blockchain-agent-md
- **Version**: 0.1.0
- **Tagline**: Autonomous agents that securely write, audit, and deploy smart contracts

### What It Does
Equipping agents with deep knowledge of Solidity/Rust security patterns, this SKILL.md mandates strict reentrancy checks and mathematical proofs before the agent is allowed to deploy generated code to a testnet, preventing catastrophic hacks.

### Inspired By
- Foundry
- AutoGen
- Crypto + Smart contracts
- Formal verification tools

### Core Components

#### `/auditor/`
- Smart contract security auditing
- Reentrancy vulnerability detection
- Mathematical safety verification
- Common vulnerability scanning

#### `/deployer/`
- Smart contract deployment simulation
- Configuration validation
- Deployment reporting
- Dry-run analysis

### Technical Architecture

**Key Dependencies:**
- `web3>=6.0` - Blockchain interactions (Trust score: 7.1)
- `pyyaml>=6.0` - Configuration parsing (Trust score: verified)
- `click>=8.0` - CLI framework (Trust score: 8.8)

**Core Modules:**
1. `auditor.py` - Smart contract auditing engine
2. `deployer.py` - Deployment simulation utilities
3. `cli.py` - Command-line interface

### AI Coding Agent Guidelines

#### When Contributing:

1. **Understand the domain**: Blockchain security requires precision and mathematical rigor
2. **Use Context7**: Check trust scores for new libraries before adding dependencies
3. **Security first**: Every change must maintain or improve security posture
4. **Formal verification**: Mathematical proofs are essential, not optional
5. **Reentrancy protection**: Must implement checks-effects-interactions pattern
6. **Overflow safety**: Always use SafeMath or Solidity >=0.8.x

#### What to Remember:

- **Mathematical proofs**: Formal verification provides guarantees, not probabilities
- **Reentrancy guards**: Must protect all external calls
- **Overflow protection**: Essential for all arithmetic operations
- **Return value checks**: Always check external call return values
- **Audit trail**: Complete history for compliance and forensics

#### Common Patterns:

**Add reentrancy guard:**
```python
from blockchain_agent_md.auditor import SmartContractAuditor, SecurityLevel

auditor = SmartContractAuditor()
contract_code = """
pragma solidity ^0.8.0;

contract SecureContract {
    function withdraw(uint256 amount) external nonReentrant {
        require(balances[msg.sender] >= amount);
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] -= amount;
    }
}
"""

report = auditor.audit_contract(contract_code, "SecureContract")
assert report.pass_reentrancy_check
```

**Validate deployment:**
```python
from blockchain_agent_md.deployer import ContractDeployer, DeploymentConfig

deployer = ContractDeployer()
config = DeploymentConfig(
    network="sepolia",
    rpc_url="https://sepolia.infura.io/v3/key",
    chain_id=11155111,
    deployer_address="0x123...456"
)

is_valid, errors = deployer.validate_config(config)
if is_valid:
    simulation = deployer.simulate_deployment(contract_code, config)
    print(f"Estimated gas: {simulation['estimated_gas']}")
```

**Check mathematical safety:**
```python
auditor = SmartContractAuditor()
report = auditor.audit_contract(contract_code, "ContractName")

if report.pass_mathematical_proof:
    print("✅ Safe arithmetic patterns detected")
else:
    print("❌ Missing overflow protection")
```

### Project Status

- ✅ Initial implementation complete
- ✅ Smart contract auditing engine
- ✅ Reentrancy detection
- ✅ Mathematical safety verification
- ✅ Common vulnerability scanning
- ✅ Deployment simulation
- ✅ CLI interface
- ✅ Comprehensive test suite
- ⚠️ Formal verification integration pending
- ⚠️ Additional security checks pending

### How to Work with This Project

1. **Read `SOUL.md`** - Understand who you are
2. **Read `USER.md`** - Know who you're helping
3. **Check `memory/YYYY-MM-DD.md`** - Recent context
4. **Read `MEMORY.md`** - Long-term decisions (main session only)
5. **Execute**: Code → Test → Commit

### Red Lines

- **No stubs or TODOs**: Every function must have real implementation
- **Type hints required**: All function signatures must include types
- **Docstrings mandatory**: Explain what, why, and how
- **Test coverage**: New features need tests
- **Security critical**: Never compromise on security

### Development Workflow

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Format code
black src/ tests/
isort src/ tests/

# Check syntax
python -m py_compile src/blockchain_agent_md/*.py

# Run CLI
blockchain-agent --help

# Commit
git add -A && git commit -m "feat: add overflow detection"
```

### Key Files to Understand

- `src/blockchain_agent_md/auditor.py` - Core auditing logic
- `src/blockchain_agent_md/deployer.py` - Deployment utilities
- `src/blockchain_agent_md/cli.py` - Command-line interface
- `tests/test_auditor.py` - Comprehensive tests
- `README.md` - Usage examples

### Security Considerations

- **Formal verification**: Mathematical proofs of safety
- **Reentrancy protection**: Automatic detection
- **Overflow safety**: SafeMath pattern detection
- **Audit trail**: Complete history for compliance
- **Trusted dependencies**: All verified via Context7
- **MIT License**: Open source, community-driven

### Next Steps

1. Add formal verification integration
2. Expand vulnerability database
3. Add more security checks
4. Create web-based dashboard
5. Add automated policy updates
6. Integrate with Foundry/Hevy

### Unique Defensible Moat

The **deep integration with formal verification tools (like Halmos) directly in the agent's execution loop** provides mathematical guarantees of code safety, fundamentally outperforming probabilistic text generation. This requires:

- Deep knowledge of Solidity/Rust security patterns
- Understanding of formal verification methods
- Integration with mathematical proof systems
- Real-time analysis capabilities
- Comprehensive vulnerability database
- Security expertise and best practices

This is complex work requiring both blockchain expertise and security knowledge, making it difficult to replicate.

---

**This file should evolve as you learn more about the project.**
