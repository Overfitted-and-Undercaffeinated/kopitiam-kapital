/**
 * Kopitiam Capital - Risk Tools MCP Server
 * 
 * Provides risk calculation tools for trading agents:
 * - Position sizing (Kelly Criterion, Fixed %, Risk Parity)
 * - VaR (Value at Risk) calculations
 * - Portfolio risk metrics
 * - Stop loss / take profit optimization
 * 
 * Built with Model Context Protocol (MCP) for agent-to-agent communication
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { 
  calculatePositionSize,
  calculateVaR,
  calculateSharpeRatio,
  calculateMaxDrawdown,
  optimizeStopLoss,
  calculateRiskReward,
  PositionSizingParams,
  VaRParams,
  RiskRewardParams
} from './risk-calculations.js';

/**
 * Available risk calculation tools
 */
const TOOLS: Tool[] = [
  {
    name: 'calculate_position_size',
    description: 'Calculate optimal position size based on risk parameters. Supports Kelly Criterion, Fixed Percentage, and Risk Parity methods.',
    inputSchema: {
      type: 'object',
      properties: {
        method: {
          type: 'string',
          enum: ['kelly', 'fixed_percent', 'risk_parity'],
          description: 'Position sizing method'
        },
        capital: {
          type: 'number',
          description: 'Total portfolio capital'
        },
        win_rate: {
          type: 'number',
          description: 'Historical win rate (0-1). Required for Kelly.'
        },
        avg_win: {
          type: 'number',
          description: 'Average win amount. Required for Kelly.'
        },
        avg_loss: {
          type: 'number',
          description: 'Average loss amount. Required for Kelly.'
        },
        risk_percent: {
          type: 'number',
          description: 'Fixed risk percentage (e.g., 0.02 for 2%). Required for fixed_percent.'
        },
        current_price: {
          type: 'number',
          description: 'Current stock price'
        },
        stop_loss: {
          type: 'number',
          description: 'Stop loss price'
        }
      },
      required: ['method', 'capital', 'current_price']
    }
  },
  
  {
    name: 'calculate_var',
    description: 'Calculate Value at Risk (VaR) for a position or portfolio. Uses historical simulation method.',
    inputSchema: {
      type: 'object',
      properties: {
        returns: {
          type: 'array',
          items: { type: 'number' },
          description: 'Array of historical returns'
        },
        confidence_level: {
          type: 'number',
          description: 'Confidence level (e.g., 0.95 for 95%)',
          default: 0.95
        },
        position_value: {
          type: 'number',
          description: 'Current position value'
        },
        holding_period_days: {
          type: 'number',
          description: 'Holding period in days',
          default: 1
        }
      },
      required: ['returns', 'position_value']
    }
  },
  
  {
    name: 'optimize_stop_loss',
    description: 'Optimize stop loss placement based on volatility (ATR) and historical performance.',
    inputSchema: {
      type: 'object',
      properties: {
        entry_price: {
          type: 'number',
          description: 'Entry price'
        },
        atr: {
          type: 'number',
          description: 'Average True Range (volatility measure)'
        },
        risk_tolerance: {
          type: 'string',
          enum: ['conservative', 'moderate', 'aggressive'],
          description: 'Risk tolerance level',
          default: 'moderate'
        },
        direction: {
          type: 'string',
          enum: ['BUY', 'SELL'],
          description: 'Trade direction',
          default: 'BUY'
        }
      },
      required: ['entry_price', 'atr']
    }
  },
  
  {
    name: 'calculate_risk_reward',
    description: 'Calculate risk/reward ratio and expected value for a trade setup.',
    inputSchema: {
      type: 'object',
      properties: {
        entry_price: {
          type: 'number',
          description: 'Entry price'
        },
        stop_loss: {
          type: 'number',
          description: 'Stop loss price'
        },
        take_profit: {
          type: 'number',
          description: 'Take profit price'
        },
        win_rate: {
          type: 'number',
          description: 'Expected win rate (0-1)',
          default: 0.5
        },
        position_size: {
          type: 'number',
          description: 'Position size (number of shares)',
          default: 1
        }
      },
      required: ['entry_price', 'stop_loss', 'take_profit']
    }
  }
];

/**
 * MCP Server for Risk Tools
 */
class RiskToolsServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'kopitiam-capital-risk-tools',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: TOOLS,
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'calculate_position_size':
            return await this.handlePositionSize(args as PositionSizingParams);

          case 'calculate_var':
            return await this.handleVaR(args as VaRParams);

          case 'optimize_stop_loss':
            return await this.handleOptimizeStopLoss(args);

          case 'calculate_risk_reward':
            return await this.handleRiskReward(args as RiskRewardParams);

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${errorMessage}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  private async handlePositionSize(params: PositionSizingParams) {
    const result = calculatePositionSize(params);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  private async handleVaR(params: VaRParams) {
    const result = calculateVaR(params);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  private async handleOptimizeStopLoss(params: any) {
    const result = optimizeStopLoss(params);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  private async handleRiskReward(params: RiskRewardParams) {
    const result = calculateRiskReward(params);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Kopitiam Capital Risk Tools MCP server running on stdio');
  }
}

// Start server
const server = new RiskToolsServer();
server.run().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});

