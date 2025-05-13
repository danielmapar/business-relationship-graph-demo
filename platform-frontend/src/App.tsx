import { GraphCanvas, type GraphCanvasRef } from 'reagraph';
import './App.css'
import { useEffect, useState, useRef, useCallback } from 'react';

// Types for API responses
interface Business {
  id: string;
  name: string;
  category: string;
}

interface Relationship {
  id: string;
  type: string;
  transaction_volume: number;
  name: string;
  category: string;
}

interface BusinessRelationships {
  id: string;
  name: string;
  category: string;
  relationships: Relationship[];
}

// Node type for the graph
interface GraphNode {
  id: string;
  label: string;
  size: number;
  color: string;
  data?: Business;
}

// Edge type for the graph
interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  width?: number;
  color?: string;
  data?: {
    type: string;
    volume: number;
  };
}

// API URL
const API_BASE_URL = 'http://localhost:8080';

// Categories for selection
const CATEGORIES = [
  'Technology', 'Retail', 'Manufacturing', 'Healthcare', 'Financial',
  'Education', 'Food', 'Hospitality', 'Entertainment', 'Automobiles',
  'Construction', 'Real Estate', 'Transportation', 'Energy', 'Agriculture'
];

function App() {
  const ref = useRef<GraphCanvasRef | null>(null);
  const [businessName, setBusinessName] = useState<string>('');
  const [businessCategory, setBusinessCategory] = useState<string>(CATEGORIES[0]);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null);

  // Log edges when they change
  useEffect(() => {
    console.log('Edges updated:', edges);
  }, [edges]);

  // Make sure every edge has a valid source and target node
  useEffect(() => {
    // Validate that all edge sources and targets exist in nodes
    if (edges.length > 0 && nodes.length > 0) {
      const nodeIds = nodes.map(node => node.id);
      const validEdges = edges.filter(edge => 
        nodeIds.includes(edge.source) && nodeIds.includes(edge.target)
      );
      
      // Add width and color to edges to make them more visible
      const enhancedEdges = validEdges.map(edge => ({
        ...edge,
        width: edge.width || 2,
        color: edge.color || '#666666'
      }));
      
      // If there are invalid edges, update the edges state
      if (validEdges.length !== edges.length) {
        console.log('Some edges were invalid and filtered out');
        setEdges(enhancedEdges);
      } else if (enhancedEdges.some(edge => !edge.width || !edge.color)) {
        // If all edges are valid but some lack width or color, update them
        setEdges(enhancedEdges);
      }
    }
  }, [nodes, edges]);

  // Search for a business
  const searchBusiness = useCallback(async () => {
    if (!businessName || !businessCategory) {
      setError('Please enter both business name and category');
      return;
    }

    setLoading(true);
    setError(null);
    console.log('Starting business search for:', businessName, businessCategory);

    try {
      const url = `${API_BASE_URL}/businesses?name=${encodeURIComponent(businessName)}&category=${encodeURIComponent(businessCategory)}`;
      console.log('Fetching from URL:', url);
      
      const response = await fetch(url);
      
      console.log('API response status:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`Error searching business: ${response.statusText}`);
      }

      const business: Business = await response.json();
      console.log('API returned business data:', business);
      
      setSelectedBusiness(business);
      
      // Create a node for the business
      const newNodes: GraphNode[] = [
        {
          id: business.id,
          label: business.name,
          size: 30,
          color: '#1a73e8',
          data: business
        }
      ];
      
      console.log('Creating initial node:', newNodes[0]);
      setNodes(newNodes);
      setEdges([]);
      
      // Fetch relationships for this business
      fetchRelationships(business.id);
    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : 'Failed to search business');
    } finally {
      setLoading(false);
    }
  }, [businessName, businessCategory]);

  // Fetch relationships for a business
  const fetchRelationships = useCallback(async (businessId: string) => {
    setLoading(true);
    console.log('Fetching relationships for business ID:', businessId);
    
    try {
      const url = `${API_BASE_URL}/businesses/${businessId}/relationships`;
      console.log('Relationships API URL:', url);
      
      const response = await fetch(url);
      console.log('Relationships API response status:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`Error fetching relationships: ${response.statusText}`);
      }
      
      const data: BusinessRelationships = await response.json();
      console.log('Full relationships data:', data);
      console.log('Relationships count:', data.relationships.length);
      
      // Use a function with the setState to ensure we have the latest nodes state
      setNodes(currentNodes => {
        console.log('Current nodes in state updater:', currentNodes);
        
        // Create a new array with existing nodes (to avoid mutation)
        const newNodes = [...currentNodes];
        const newNodeIds: string[] = [];
        
        // Process each relationship and add nodes if they don't exist
        data.relationships.forEach((relationship, index) => {
          console.log(`Processing relationship ${index}:`, relationship);
          
          if (!newNodes.some(node => node.id === relationship.id)) {
            const newNode = {
              id: relationship.id,
              label: relationship.name,
              size: 25,
              color: '#ff9900',
              data: {
                id: relationship.id,
                name: relationship.name,
                category: relationship.category
              }
            };
            console.log('Adding new node:', newNode);
            newNodes.push(newNode);
            newNodeIds.push(relationship.id);
          } else {
            console.log('Node already exists for:', relationship.id);
          }
        });
        
        console.log('Final nodes after update:', newNodes);
        console.log('Added node IDs:', newNodeIds);
        
        return newNodes;
      });
      
      // Create edges after nodes are set
      const newEdges: GraphEdge[] = data.relationships.map(relationship => ({
        id: `${data.id}-${relationship.id}`,
        source: data.id,
        target: relationship.id,
        label: `${relationship.type} (${relationship.transaction_volume})`,
        width: 2,
        color: '#666666',
        data: {
          type: relationship.type,
          volume: relationship.transaction_volume
        }
      }));
      
      console.log('Setting edges:', newEdges);
      setEdges(newEdges);
      
    } catch (err) {
      console.error('Relationships fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch relationships');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fit graph to view when nodes change
  useEffect(() => {
    if (nodes.length > 0 && ref.current) {
      setTimeout(() => {
        ref.current?.fitNodesInView();
      }, 500); // Increased delay to allow more time for rendering
    }
  }, [nodes]);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <div style={{
        zIndex: 9,
        position: 'absolute',
        top: 15,
        left: 15,
        background: 'rgba(0, 0, 0, .7)',
        padding: 15,
        color: 'white',
        borderRadius: 5,
        maxWidth: 300
      }}>
        <h3 style={{ margin: '0 0 10px 0' }}>Business Search</h3>
        
        <div style={{ marginBottom: 10 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Business Name:</label>
          <input 
            type="text" 
            value={businessName} 
            onChange={(e) => setBusinessName(e.target.value)}
            style={{ width: '100%', padding: 5 }}
          />
        </div>
        
        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Category:</label>
          <select 
            value={businessCategory} 
            onChange={(e) => setBusinessCategory(e.target.value)}
            style={{ width: '100%', padding: 5 }}
          >
            {CATEGORIES.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
        
        <button
          onClick={searchBusiness}
          disabled={loading}
          style={{ 
            width: '100%',
            padding: '8px',
            backgroundColor: loading ? '#555' : '#1a73e8',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Searching...' : 'Search Business'}
        </button>
        
        {error && (
          <div style={{ color: 'red', marginTop: 10 }}>
            {error}
          </div>
        )}
        
        {selectedBusiness && (
          <div style={{ marginTop: 15 }}>
            <h4 style={{ margin: '0 0 5px 0' }}>Selected Business:</h4>
            <div>ID: {selectedBusiness.id}</div>
            <div>Name: {selectedBusiness.name}</div>
            <div>Category: {selectedBusiness.category}</div>
          </div>
        )}

        <div style={{ marginTop: 15 }}>
          <p>Nodes: {nodes.length}</p>
          <p>Edges: {edges.length}</p>
        </div>
      </div>
      
      <GraphCanvas 
        ref={ref} 
        nodes={nodes} 
        edges={edges}
        edgeArrowPosition="none"
        labelType="all"
        layoutType="forceDirected2d"
        edgeLabelPosition="inline"
      />
    </div>
  );
}

export default App
