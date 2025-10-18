#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: 'kopitiam-mem0',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_policy',
        description: 'Get user trading policy and preferences from Mem0',
        inputSchema: {
          type: 'object',
          properties: {
            user_id: {
              type: 'string',
              description: 'User ID',
            },
          },
          required: ['user_id'],
        },
      },
      {
        name: 'record_outcome',
        description: 'Record outcome of a trading recommendation',
        inputSchema: {
          type: 'object',
          properties: {
            user_id: { type: 'string', description: 'User ID' },
            recommendation_id: { type: 'string', description: 'Recommendation ID' },
            outcome: { type: 'string', description: 'Outcome description' },
            pnl: { type: 'number', description: 'P&L result' },
          },
          required: ['user_id', 'recommendation_id', 'outcome', 'pnl'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'get_policy':
      // TODO: Implement policy retrieval from Mem0
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              risk_profile: 'Moderate',
              max_position_size: 0.1,
              preferred_sectors: [],
              restricted_symbols: []
            }),
          },
        ],
      };
    
    case 'record_outcome':
      // TODO: Implement outcome recording to Mem0
      return {
        content: [
          {
            type: 'text',
            text: 'Outcome recorded successfully',
          },
        ],
      };
    
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Mem0 MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});

