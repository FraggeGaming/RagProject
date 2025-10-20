import { useState, useEffect } from 'react';
import MessageBox from './components/RagComponent';
function App() {




  const [message, setMessage] = useState<string>("Loading...");
  const [lastQuery, setLastQuery] = useState<string>("");

  useEffect(() => {

  }, []);

  const SendQuery = (msg: string) => {

    //So user wont try to spam the same query over and over
    if (lastQuery !== "" && lastQuery === msg)
      return message;

    setLastQuery(msg)

    const reqHeaders = new Headers();

    // A cached response is okay unless it's more than a week old
    reqHeaders.set("Message", msg);

    const options = {
      headers: reqHeaders,
    };

    console.log(msg)

    fetch("http://localhost:5000/fetchAll", options)
      .then(res => res.json())
      .then(data => setMessage(data))
      .catch(console.error);

    //Send the message to the backend to generate embedding and return the result
  }

  return (

    <div className="flex flex-col gap-10 items-center min-h-screen bg-gray-600">

      <h1 className="text-5xl font-serif text-zinc-200 mt-10">UMU AI</h1>
      <MessageBox
        SendQuery={SendQuery}
        Message={message}
      />
    </div>

  );
}




export default App
