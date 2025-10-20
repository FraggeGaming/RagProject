import './App.css'
import { useEffect, useState } from 'react';
function App() {

  const [message, setMessage] = useState<string>("Loading...");


  useEffect(() => {
    fetch("http://localhost:3000/api/hello")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => {
        console.error("Error fetching:", err);
        setMessage("Failed to connect to backend");
      });
  }, []);

  return (
    <>
      <div className='bg-blue-900 w-12 h-20'>
        <p>{message}</p>
      </div>
    </>
  )
}

export default App
