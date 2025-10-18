/**
 * Fast search using Exa
 */

export interface SearchResult {
  title: string;
  url: string;
  published?: string;
}

export async function searchFast(query: string, numResults: number = 10): Promise<SearchResult[]> {
  // TODO: Implement Exa fast search API call
  return [
    { title: 'Example Result', url: 'https://example.com', published: '2024-01-01' }
  ];
}

