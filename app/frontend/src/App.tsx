import { useState, useEffect } from 'react';
import MessageBox from './components/RagComponent';
import mainLogo from './assets/UMUAILogo.svg';

function App() {


  return (

    <div className="flex flex-col gap-10 items-center min-h-screen bg-gray-600">

      <div className='flex mt-10'>
        <img src={mainLogo} alt="fireSpot" className="w-52 h-auto" />
      </div>
      <MessageBox/>
    </div>

  );
}




export default App
