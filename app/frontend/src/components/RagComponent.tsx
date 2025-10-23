import { useState } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];
export default function MessageBox() {
    const [value, setValue] = useState<Value>(null);
    const [lastQuery, setLastQuery] = useState<string>("");
    const [lastDate, setLastDate] = useState<Value>(null);
    const [message, setMessage] = useState<string>("Event information..");

    const toSQLDate = (date: Date) => {
        // SQL-compatible format: YYYY-MM-DD
        return date.toISOString().split("T")[0];
    };



    const handleSend = (msg: string) => {
        //search string in header "Message"
        //If only one date is selected, then that date is in Date-Start
        //If range is selected, range is in Date-Start and Date-End


        // Prevent spam
        if (value != null && lastDate === value && lastQuery === msg && msg !== "") {
            console.log("nice try");
            return message;
        }

        setLastQuery(msg);
        setLastDate(value);

        const reqHeaders = new Headers();
        reqHeaders.set("Message", msg);

        console.log("Selected dates:", value);

        if (value) {
            if (Array.isArray(value)) {
                const [start, end] = value;
                if (start) reqHeaders.set("Date-Start", toSQLDate(start));
                if (end) reqHeaders.set("Date-End", toSQLDate(end));
            } else {
                reqHeaders.set("Date-Start", toSQLDate(value));
            }
        }

        const options = { headers: reqHeaders };
        console.log([...reqHeaders.entries()]);

        fetch("http://localhost:5000/fetchAll", options)
            .then((res) => res.json())
            .then((data) => setMessage(data))
            .catch(console.error);
    };


    //Fires when range is selected
    const handleChange = (val: Value) => {
        console.log("Range selected:", val);
        setValue(val);
    };

    //Fires when click on day
    const handleClickDay = (val: Date) => {
        console.log("Clicked date:", toSQLDate(val));
        setValue(val);
    };

    return (
        <div className="flex gap-5 flex-col w-1/2 bg-gray-200 rounded-2xl shadow-md p-6">
            <h1 className="text-xl font-semibold text-gray-800">
                What event are you looking for?
            </h1>

            <Calendar
                selectRange
                onChange={handleChange}
                onClickDay={handleClickDay}
                value={value}
            />

            <InputBox handleSend={handleSend} />

            <div className="flex border border-gray-300 rounded-xl p-3 min-h-[100px] text-gray-700 bg-gray-50">
                {message || "Ask me something..."}
            </div>
        </div>
    );
}

interface InputBoxProps {
    handleSend: (msg: string) => void;
}

export function InputBox({ handleSend }: InputBoxProps) {
    const [input, setInput] = useState("");

    const onSubmit = () => {
        handleSend(input);
        setInput("");
    };

    return (
        <div className="flex gap-5">
            <input
                type="text"
                placeholder="Computer science talks.."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-grow border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
                onClick={onSubmit}
                className="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 active:scale-95 transition"
            >
                Send
            </button>
        </div>
    );
}
