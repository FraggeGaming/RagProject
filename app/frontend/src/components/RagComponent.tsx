import { useState } from "react";

interface MessageBoxProps {
    SendQuery: (msg: string) => void;
    Message: string;
}
export default function MessageBox({ SendQuery, Message }: MessageBoxProps) {
    //const [output, setOutput] = useState("");

    const handleSend = (msg: string) => {
        // Example logic — replace with your backend call if needed
        //setOutput(`You sent: ${input}`);
        SendQuery(msg)
        console.log("Sent to server")

    };

    return (
        <div className="flex gap-5 flex-col w-1/2 bg-gray-200 rounded-2xl shadow-md p-6 ">
            <h1 className="text-xl font-semibold text-gray-800">Message Sender</h1>

            <InputBox
                handleSend={handleSend}
            />
            <div className="flex border border-gray-300 rounded-xl p-3 min-h-[100px] text-gray-700 bg-gray-50">
                {Message || "Ask me something..."}
            </div>

        </div>
    );
}

interface InputBoxProps {
    handleSend: (msg: string) => void;
}
export function InputBox({ handleSend }: InputBoxProps) {
    const [input, setInput] = useState("");

    const OnSubmit = () => {
        handleSend(input);
        setInput("");
    }
    return (
        <div className="flex gap-5">
            <input
                type="text"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-grow border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
                onClick={OnSubmit}
                className="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 active:scale-95 transition"
            >
                Send
            </button>
        </div>

    );


}

