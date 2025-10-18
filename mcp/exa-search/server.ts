#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: 'kopitiam-exa-search',
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
        name: 'search_fast',
        description: 'Fast search for recent news and articles using Exa',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Search query' },
            num_results: { type: 'number', description: 'Number of results', default: 10 },
          },
          required: ['query'],
        },
      },
      {
        name: 'search_deep',
        description: 'Deep search with full content retrieval using Exa',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Search query' },
            num_results: { type: 'number', description: 'Number of results', default: 10 },
          },
          required: ['query'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'search_fast':
      // TODO: Implement Exa fast search
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify([
              { title: 'Example Result', url: 'https://example.com', published: '2024-01-01' }
            ]),
          },
        ],
      };
    
    case 'search_deep':
      // TODO: Implement Exa deep search
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify([
              { title: 'Example Result', url: 'https://example.com', content: 'Full content here...' }
            ]),
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
  console.error('Exa Search MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});

