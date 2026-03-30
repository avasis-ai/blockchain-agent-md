"""Command-line interface for blockchain agent."""

import click
import yaml
from typing import Optional, List
import json

from .auditor import SmartContractAuditor, SecurityLevel, AuditReport
from .deployer import ContractDeployer, DeploymentConfig


@click.group()
@click.version_option(version="0.1.0", prog_name="blockchain-agent")
def main() -> None:
    """Blockchain Agent - Secure smart contract analysis and deployment."""
    pass


@main.command()
@click.argument("contract_file", type=click.Path(exists=True))
@click.option("--network", "-n", default="local", help="Target network")
@click.option("--rpc-url", "-r", default="http://localhost:8545", help="RPC URL")
@click.option("--chain-id", "-c", default=1337, help="Chain ID")
@click.option("--deployer", "-d", required=True, help="Deployer address")
@click.option("--gas-limit", "-g", default=5000000, help="Gas limit")
def deploy(contract_file: str, network: str, rpc_url: str, 
           chain_id: int, deployer: str, gas_limit: int) -> None:
    """Simulate smart contract deployment."""
    deployer_instance = ContractDeployer()
    
    try:
        with open(contract_file, 'r') as f:
            contract_code = f.read()
        
        # Validate contract name
        contract_name = f"Contract_{contract_file.split('/')[-1].replace('.sol', '')}"
        
        # Create config
        config = DeploymentConfig(
            network=network,
            rpc_url=rpc_url,
            chain_id=chain_id,
            deployer_address=deployer,
            gas_limit=gas_limit
        )
        
        # Simulate deployment
        result = deployer_instance.simulate_deployment(contract_code, config)
        
        if result["success"]:
            click.echo(f"\nDeployment Simulation: {contract_name}")
            click.echo("=" * 50)
            click.echo(f"Estimated Gas: {result['estimated_gas']:,} gas units")
            
            if result.get("issues"):
                click.echo("\nPotential Issues:")
                for issue in result["issues"]:
                    click.echo(f"  ⚠️  {issue}")
            
            if result.get("optimization_suggestions"):
                click.echo("\nOptimization Suggestions:")
                for suggestion in result["optimization_suggestions"]:
                    click.echo(f"  💡 {suggestion}")
            
            click.echo("\n✅ Deployment simulation successful!")
        else:
            click.echo("\n❌ Deployment simulation failed!")
            for error in result.get("errors", []):
                click.echo(f"   Error: {error}")
                
    except FileNotFoundError:
        click.echo(f"Error: Contract file '{contract_file}' not found")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@main.command()
@click.argument("contract_file", type=click.Path(exists=True))
def audit(contract_file: str) -> None:
    """Audit smart contract for security vulnerabilities."""
    auditor = SmartContractAuditor()
    
    try:
        with open(contract_file, 'r') as f:
            contract_code = f.read()
        
        # Extract contract name from file
        contract_name = f"Contract_{contract_file.split('/')[-1].replace('.sol', '')}"
        
        # Run audit
        report = auditor.audit_contract(contract_code, contract_name)
        
        click.echo(f"\nSecurity Audit: {contract_name}")
        click.echo("=" * 50)
        
        # Summary
        click.echo("\n📊 Summary:")
        for severity, count in report.summary.items():
            emoji = {
                "info": "ℹ️",
                "low": "💡",
                "medium": "⚠️",
                "high": "🔴",
                "critical": "🚨"
            }.get(severity, "❓")
            click.echo(f"   {emoji} {severity.capitalize()}: {count}")
        
        click.echo(f"\n🔐 Security Checks:")
        reentrancy_status = "✅ PASS" if report.pass_reentrancy_check else "❌ FAIL"
        math_status = "✅ PASS" if report.pass_mathematical_proof else "❌ FAIL"
        click.echo(f"   {reentrancy_status} Reentrancy protection")
        click.echo(f"   {math_status} Mathematical safety")
        
        # Issues
        if report.issues:
            click.echo(f"\n🔍 Issues Found ({len(report.issues)}):")
            for issue in report.issues:
                emoji = {
                    SecurityLevel.INFO: "ℹ️",
                    SecurityLevel.LOW: "💡",
                    SecurityLevel.MEDIUM: "⚠️",
                    SecurityLevel.HIGH: "🔴",
                    SecurityLevel.CRITICAL: "🚨"
                }.get(issue.severity, "❓")
                click.echo(f"\n   {emoji} [{issue.severity.value.upper()}] {issue.title}")
                click.echo(f"      Location: {issue.location}")
                click.echo(f"      Description: {issue.description}")
                click.echo(f"      Recommendation: {issue.recommendation}")
                if issue.cwe_id:
                    click.echo(f"      CWE: {issue.cwe_id}")
        else:
            click.echo("\n✅ No security issues found!")
        
        # Export report
        output_file = contract_file.replace('.sol', '_audit_report.json')
        with open(output_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        click.echo(f"\n📁 Report saved to: {output_file}")
        
    except FileNotFoundError:
        click.echo(f"Error: Contract file '{contract_file}' not found")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@main.command()
def history() -> None:
    """Show audit and deployment history."""
    auditor = SmartContractAuditor()
    deployer = ContractDeployer()
    
    audit_history = auditor.get_history()
    deployment_history = deployer.get_deployment_history()
    
    click.echo(f"\n📜 Audit History ({len(audit_history)} audits):")
    for i, report in enumerate(audit_history, 1):
        click.echo(f"  {i}. {report.contract_name} - {report.audit_timestamp.strftime('%Y-%m-%d %H:%M')}")
        click.echo(f"     Issues: {sum(report.summary.values())} | Passes: "
                  f"Reentrancy={report.pass_reentrancy_check}, Math={report.pass_mathematical_proof}")
    
    if not audit_history:
        click.echo("  No audit history yet.")
    
    click.echo(f"\n📦 Deployment History ({len(deployment_history)} deployments):")
    for i, deployment in enumerate(deployment_history, 1):
        status = "✅" if deployment["success"] else "❌"
        click.echo(f"  {i}. {status} {deployment['contract_name']} - {deployment['timestamp']}")
        if deployment.get("contract_address"):
            click.echo(f"     Address: {deployment['contract_address']}")
    
    if not deployment_history:
        click.echo("  No deployment history yet.")


@main.command()
@click.argument("issue_id", required=False)
@click.option("--clear", is_flag=True, help="Clear all issues")
def show_issues(issue_id: Optional[str], clear: bool) -> None:
    """Show current audit issues or clear them."""
    auditor = SmartContractAuditor()
    
    if clear:
        auditor.clear_history()
        click.echo("✅ All issues cleared.")
        return
    
    issues = auditor.get_issues()
    
    if not issues:
        click.echo("✅ No issues found in current audit.")
        return
    
    if issue_id:
        # Show specific issue
        for issue in issues:
            if issue.id == issue_id:
                click.echo(f"\nIssue: {issue.title}")
                click.echo(f"Severity: {issue.severity.value.upper()}")
                click.echo(f"Location: {issue.location}")
                click.echo(f"Description: {issue.description}")
                click.echo(f"Recommendation: {issue.recommendation}")
                if issue.cwe_id:
                    click.echo(f"CWE: {issue.cwe_id}")
                return
        click.echo(f"❌ Issue '{issue_id}' not found.")
    else:
        # Show all issues
        click.echo(f"\n🔍 Current Issues ({len(issues)}):")
        for issue in issues:
            click.echo(f"\n  {issue.id}: {issue.title} [{issue.severity.value.upper()}]")
            click.echo(f"    Location: {issue.location}")
            click.echo(f"    Description: {issue.description}")


@main.command()
def config() -> None:
    """Show configuration information."""
    deployer = ContractDeployer()
    
    click.echo("\n🔧 Blockchain Agent Configuration")
    click.echo("=" * 50)
    
    click.echo(f"\n📡 Supported Networks:")
    for network in deployer.VALID_NETWORKS:
        click.echo(f"   • {network}")
    
    click.echo(f"\n📦 Version: 0.1.0")
    click.echo(f"🏢 Organization: Avasis AI")
    click.echo(f"📧 Contact: contact@avasis.ai")


@main.command()
def help_text() -> None:
    """Show extended help information."""
    click.echo("""
Blockchain Agent - Secure Smart Contract Analysis

FEATURES:
  • Security auditing for smart contracts
  • Reentrancy vulnerability detection
  • Mathematical safety verification
  • Common vulnerability scanning
  • Deployment simulation
  • Comprehensive reporting

USAGE:
  blockchain-audit CONTRACT_FILE    Audit a contract for security issues
  blockchain-deploy CONTRACT_FILE   Simulate contract deployment
  blockchain-history                Show audit and deployment history
  blockchain-show-issues [ID]       Show current audit issues
  blockchain-config                 Show configuration info
  blockchain-help                   Show this help

EXAMPLES:
  blockchain-audit MyContract.sol
  blockchain-deploy --network sepolia --rpc-url https://sepolia.infura.io MyContract.sol

For more information, visit: https://github.com/avasis-ai/blockchain-agent-md
    """)


def main_entry() -> None:
    """Main entry point."""
    main(prog_name="blockchain-agent")


if __name__ == "__main__":
    main_entry()
