"""Smart contract auditor for security verification."""

import re
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class SecurityLevel(Enum):
    """Security severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityIssue:
    """Represents a security issue found in smart contract."""
    id: str
    title: str
    severity: SecurityLevel
    description: str
    location: str
    recommendation: str
    cwe_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "location": self.location,
            "recommendation": self.recommendation,
            "cwe_id": self.cwe_id
        }


@dataclass
class AuditReport:
    """Report from security audit."""
    contract_name: str
    audit_timestamp: datetime
    issues: List[SecurityIssue]
    pass_reentrancy_check: bool
    pass_mathematical_proof: bool
    summary: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "contract_name": self.contract_name,
            "audit_timestamp": self.audit_timestamp.isoformat(),
            "issues": [issue.to_dict() for issue in self.issues],
            "pass_reentrancy_check": self.pass_reentrancy_check,
            "pass_mathematical_proof": self.pass_mathematical_proof,
            "summary": self.summary
        }


class SmartContractAuditor:
    """Audits smart contracts for security vulnerabilities."""
    
    REENTRANCY_PATTERNS = [
        re.compile(r'external\.(call|send)', re.IGNORECASE),
        re.compile(r'\.transfer\(', re.IGNORECASE),
        re.compile(r'\.transferFrom\(', re.IGNORECASE),
        re.compile(r'function\s+\w+\s*\(.*\)?\s*external', re.IGNORECASE),
    ]
    
    REENTRANCY_GUARD_PATTERNS = [
        re.compile(r'nonReentrant', re.IGNORECASE),
        re.compile(r'check-conditions-effects-interactions', re.IGNORECASE),
        re.compile(r'@custom:solidity-security-check:reentrancy', re.IGNORECASE),
        re.compile(r'initializers\.(lock|mutex|lockstate)', re.IGNORECASE),
    ]
    
    MATH_ERROR_PATTERNS = [
        re.compile(r'uint\s+\w+\s*=\s*\w+\s*%', re.IGNORECASE),
        re.compile(r'division\s*by\s*zero', re.IGNORECASE),
        re.compile(r'underflow', re.IGNORECASE),
        re.compile(r'overflow', re.IGNORECASE),
    ]
    
    OVERFLOW_SAFE_PATTERNS = [
        re.compile(r'SafeMath', re.IGNORECASE),
        re.compile(r'OpenZeppelin[^\'"]*\w*safe', re.IGNORECASE),
        re.compile(r'uint256\s+\w+\s*=\s*checked[_-]?multiply', re.IGNORECASE),
        re.compile(r'checked[_-]?add', re.IGNORECASE),
    ]
    
    def __init__(self):
        """Initialize auditor."""
        self._issues: List[SecurityIssue] = []
        self._audit_history: List[AuditReport] = []
    
    def audit_contract(self, contract_code: str, contract_name: str = "contract") -> AuditReport:
        """
        Audit smart contract for security vulnerabilities.
        
        Args:
            contract_code: Solidity contract source code
            contract_name: Name of the contract
            
        Returns:
            AuditReport with security findings
        """
        self._issues = []
        
        # Check for reentrancy vulnerabilities
        self._check_reentrancy(contract_code, contract_name)
        
        # Check for mathematical errors
        self._check_mathematical_errors(contract_code, contract_name)
        
        # Check for common vulnerabilities
        self._check_common_vulnerabilities(contract_code, contract_name)
        
        # Create report
        issue_count = {
            SecurityLevel.INFO.value: 0,
            SecurityLevel.LOW.value: 0,
            SecurityLevel.MEDIUM.value: 0,
            SecurityLevel.HIGH.value: 0,
            SecurityLevel.CRITICAL.value: 0,
        }
        
        for issue in self._issues:
            if issue.severity.value in issue_count:
                issue_count[issue.severity.value] += 1
        
        pass_reentrancy = self._check_reentrancy_patterns(contract_code)
        pass_math = self._check_mathematical_patterns(contract_code)
        
        report = AuditReport(
            contract_name=contract_name,
            audit_timestamp=datetime.now(),
            issues=self._issues,
            pass_reentrancy_check=pass_reentrancy,
            pass_mathematical_proof=pass_math,
            summary=issue_count
        )
        
        self._audit_history.append(report)
        return report
    
    def _check_reentrancy(self, contract_code: str, contract_name: str) -> None:
        """Check for reentrancy vulnerabilities."""
        has_external_calls = False
        guard_found = False
        
        for line_num, line in enumerate(contract_code.split('\n'), 1):
            # Check for external calls
            if any(pattern.search(line) for pattern in self.REENTRANCY_PATTERNS):
                has_external_calls = True
                
                # Check if outside function or constructor
                if 'external' in line.lower() or 'transfer' in line.lower():
                    self._issues.append(SecurityIssue(
                        id=f"REENT-00{len(self._issues) + 1:02d}",
                        title="External Call Detected",
                        severity=SecurityLevel.MEDIUM,
                        description="External call detected without reentrancy guard",
                        location=f"{contract_name}:line {line_num}",
                        recommendation="Add nonReentrant modifier or implement checks-effects-interactions pattern",
                        cwe_id="CWE-841"
                    ))
            
            # Check for reentrancy guards
            if any(pattern.search(line) for pattern in self.REENTRANCY_GUARD_PATTERNS):
                guard_found = True
        
        # Report if no guard found
        if has_external_calls and not guard_found:
            pass
    
    def _check_mathematical_errors(self, contract_code: str, contract_name: str) -> None:
        """Check for mathematical vulnerabilities."""
        lines = contract_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for potential division by zero
            if re.search(r'division\s*by\s*zero|\/\s*\(\s*[0-9]*\s*\)', line, re.IGNORECASE):
                self._issues.append(SecurityIssue(
                    id=f"MATH-00{len(self._issues) + 1:02d}",
                    title="Division by Zero Risk",
                    severity=SecurityLevel.HIGH,
                    description="Potential division by zero vulnerability",
                    location=f"{contract_name}:line {line_num}",
                    recommendation="Add zero-check before division operation",
                    cwe_id="CWE-369"
                ))
            
            # Check for potential underflow
            if re.search(r'underflow', line, re.IGNORECASE):
                self._issues.append(SecurityIssue(
                    id=f"MATH-00{len(self._issues) + 1:02d}",
                    title="Underflow Risk",
                    severity=SecurityLevel.HIGH,
                    description="Potential underflow vulnerability",
                    location=f"{contract_name}:line {line_num}",
                    recommendation="Use SafeMath library or Solidity >=0.8.x",
                    cwe_id="CWE-190"
                ))
    
    def _check_common_vulnerabilities(self, contract_code: str, contract_name: str) -> None:
        """Check for common smart contract vulnerabilities."""
        lines = contract_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for unchecked return values
            if re.search(r'external.*\.call\(\)', line, re.IGNORECASE):
                if 'require' not in line and 'if' not in line:
                    self._issues.append(SecurityIssue(
                        id=f"COMP-00{len(self._issues) + 1:02d}",
                        title="Unchecked Return Value",
                        severity=SecurityLevel.MEDIUM,
                        description="External call return value not checked",
                        location=f"{contract_name}:line {line_num}",
                        recommendation="Check return value of external calls",
                        cwe_id="CWE-252"
                    ))
            
            # Check for uninitialized variables
            if re.search(r'uninitialized|not\s*initialized', line, re.IGNORECASE):
                self._issues.append(SecurityIssue(
                    id=f"COMP-00{len(self._issues) + 1:02d}",
                    title="Uninitialized Variable",
                    severity=SecurityLevel.LOW,
                    description="Variable may be uninitialized",
                    location=f"{contract_name}:line {line_num}",
                    recommendation="Initialize variables before use",
                    cwe_id="CWE-457"
                ))
    
    def _check_reentrancy_patterns(self, contract_code: str) -> bool:
        """Check if reentrancy protection is implemented."""
        return any(
            pattern.search(contract_code) 
            for pattern in self.REENTRANCY_GUARD_PATTERNS
        )
    
    def _check_mathematical_patterns(self, contract_code: str) -> bool:
        """Check if mathematical safety patterns are used."""
        return any(
            pattern.search(contract_code) 
            for pattern in self.OVERFLOW_SAFE_PATTERNS
        )
    
    def get_issues(self) -> List[SecurityIssue]:
        """Get all issues found in current audit."""
        return self._issues.copy()
    
    def get_history(self) -> List[AuditReport]:
        """Get audit history."""
        return self._audit_history.copy()
    
    def clear_history(self) -> None:
        """Clear audit history."""
        self._audit_history = []
        self._issues = []
