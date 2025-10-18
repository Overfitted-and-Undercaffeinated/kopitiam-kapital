/**
 * Deep search using Exa with full content
 */

export interface DeepSearchResult {
  title: string;
  url: string;
  content: string;
  published?: string;
}

export async function searchDeep(query: string, numResults: number = 10): Promise<DeepSearchResult[]> {
  // TODO: Implement Exa deep search API call
  return [
    { 
      title: 'Example Result', 
      url: 'https://example.com', 
      content: 'Full content here...',
      published: '2024-01-01'
    }
  ];
}

