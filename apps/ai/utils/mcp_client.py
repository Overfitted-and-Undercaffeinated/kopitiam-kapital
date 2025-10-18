"""
MCP Client Wrapper for Risk Tools Server
Communicates with TypeScript MCP server for advanced risk calculations
"""
import logging
import subprocess
import asyncio
from typing import Dict, Optional
import json

# Flexible imports
try:
    from ..utils.config import settings
except ImportError:
    from utils.config import settings

logger = logging.getLogger(__name__)

class MCPRiskClient:
    """
    Client for MCP Risk Tools server
    
    Features:
    - Kelly Criterion position sizing
    - Value at Risk (VaR) calculations
    - ATR-based stop loss optimization
    - Risk/reward ratio analysis
    
    Auto-starts MCP server if enabled
    Gracefully falls back to simple calculations if unavailable
    """
    
    def __init__(self):
        self.server_process = None
        self.enabled = settings.use_mcp_risk_tools
        self.server_path = "mcp/risk-tools/dist/index.js"
        
        if self.enabled:
            try:
                # Check if Node.js is available
                result = subprocess.run(['node', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✅ Node.js available: {result.stdout.strip()}")
                else:
                    logger.warning("Node.js not found. MCP server disabled.")
                    self.enabled = False
            except FileNotFoundError:
                logger.warning("Node.js not installed. MCP server disabled.")
                self.enabled = False
        
        if not self.enabled:
            logger.warning("⚠️ MCP Risk Tools disabled - using simple risk calculations")
    
    async def start_server(self):
        """Start MCP server as subprocess"""
        if not self.enabled:
            return False
        
        try:
            logger.info(f"Starting MCP Risk Tools server: {self.server_path}")
            
            self.server_process = subprocess.Popen(
                ['node', self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(0.5)
            
            if self.server_process.poll() is None:
                logger.info("✅ MCP Risk Tools server started successfully")
                return True
            else:
                logger.error("MCP server failed to start")
                self.enabled = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            self.enabled = False
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """
        Call an MCP tool
        
        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments
        
        Returns:
            Tool result or None if unavailable
        """
        if not self.enabled or not self.server_process:
            logger.debug(f"MCP disabled - cannot call {tool_name}")
            return None
        
        try:
            # Build MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Send to MCP server via stdin
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            # Read response from stdout (with timeout)
            try:
                response_line = await asyncio.wait_for(
                    asyncio.to_thread(self.server_process.stdout.readline),
                    timeout=5.0
                )
                
                response = json.loads(response_line)
                
                if 'result' in response:
                    # Extract content from MCP response
                    content = response['result']['content'][0]['text']
                    result = json.loads(content)
                    return result
                else:
                    logger.error(f"MCP error: {response.get('error')}")
                    return None
                    
            except asyncio.TimeoutError:
                logger.error(f"MCP tool call timeout: {tool_name}")
                return None
                
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            return None
    
    async def calculate_position_size(
        self,
        method: str,
        capital: float,
        current_price: float,
        win_rate: Optional[float] = None,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None,
        risk_percent: Optional[float] = None,
        stop_loss: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Calculate position size using MCP server
        
        Methods: 'kelly', 'fixed_percent', 'risk_parity'
        
        Returns:
            {shares, position_value, risk_amount, method} or None
        """
        args = {
            'method': method,
            'capital': capital,
            'current_price': current_price
        }
        
        if win_rate is not None:
            args['win_rate'] = win_rate
        if avg_win is not None:
            args['avg_win'] = avg_win
        if avg_loss is not None:
            args['avg_loss'] = avg_loss
        if risk_percent is not None:
            args['risk_percent'] = risk_percent
        if stop_loss is not None:
            args['stop_loss'] = stop_loss
        
        return await self.call_tool('calculate_position_size', args)
    
    async def optimize_stop_loss(
        self,
        entry_price: float,
        atr: float,
        risk_tolerance: str = 'moderate',
        direction: str = 'BUY'
    ) -> Optional[Dict]:
        """
        Optimize stop loss using ATR
        
        Returns:
            {stop_loss, atr_multiplier, distance_percent} or None
        """
        args = {
            'entry_price': entry_price,
            'atr': atr,
            'risk_tolerance': risk_tolerance,
            'direction': direction
        }
        
        return await self.call_tool('optimize_stop_loss', args)
    
    async def calculate_risk_reward(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        win_rate: float = 0.5,
        position_size: int = 1
    ) -> Optional[Dict]:
        """
        Calculate risk/reward ratio and expected value
        
        Returns:
            {risk_reward_ratio, expected_value, recommendation} or None
        """
        args = {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'win_rate': win_rate,
            'position_size': position_size
        }
        
        return await self.call_tool('calculate_risk_reward', args)
    
    def stop_server(self):
        """Stop MCP server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            logger.info("MCP Risk Tools server stopped")

# Global instance
mcp_risk_client = MCPRiskClient()

