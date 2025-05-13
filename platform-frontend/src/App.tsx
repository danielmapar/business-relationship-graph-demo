import { GraphCanvas, type GraphCanvasRef } from 'reagraph';
import './App.css'
import { useEffect } from 'react';
import { useState } from 'react';
import { useRef } from 'react';

// Helper function for random number generation
const random = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;


function App() {
  const ref = useRef<GraphCanvasRef | null>(null);
  const [nodes, setNodes] = useState([
    {
        id: '1',
        label: '1'
      },
      {
        id: '2',
        label: '2'
      }
    ]);
  const [edges, setEdges] = useState([
    {
      source: '1',
      target: '2',
      id: '1-2',
      label: '1-2'
    },
    {
      source: '2',
      target: '1',
      id: '2-1',
      label: '2-1'
    }
  ]);
  useEffect(() => {
    ref.current?.fitNodesInView();
  }, [nodes]);
  return <div>
      <div style={{
        zIndex: 9,
        position: 'absolute',
        top: 15,
        right: 15,
        background: 'rgba(0, 0, 0, .5)',
        padding: 1,
        color: 'white'
      }}>
        <button style={{
          display: 'block',
          width: '100%'
        }} onClick={() => {

        }}>
            Search business
        </button>
        <button style={{
          display: 'block',
          width: '100%'
        }} onClick={() => {
          setNodes(nodes.filter(n => n.id !== nodes[0]?.id));
        }}>
            Remove Node {nodes[0]?.id}
        </button>
      </div>
      <GraphCanvas ref={ref} nodes={nodes} edges={edges} />
    </div>;
}

export default App
