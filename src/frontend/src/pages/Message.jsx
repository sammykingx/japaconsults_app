// import React, { useState, useEffect } from "react";
// import { Link } from "react-router-dom";
// import { FaSearch } from "react-icons/fa";
// import "../css/Messages.css";
// import img from "../images/gb-profile.png";
// import { IoCallOutline } from "react-icons/io5";
// import { HiOutlineVideoCamera } from "react-icons/hi";
// import { BsSend } from "react-icons/bs";
// import { users, chats } from "../data";
// import Search from "../components/Search";

// const Message = () => {
//   const { query, results, handleInputChange } = Search(users);

//   const [message, setMessage] = useState("");
//   const [messageSaved, setMessageSaved] = useState(false);

//   // Load draft message from localStorage on component mount
//   useEffect(() => {
//     const savedDraft = localStorage.getItem("messageDraft");
//     if (savedDraft) {
//       setMessage(savedDraft);
//     }
//   }, []);

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     console.log(message);

//     // Clear the draft message when the message is sent
//     setMessage("");
//     setMessageSaved(false);

//     // Remove draft from localStorage
//     localStorage.removeItem("messageDraft");
//   };

//   // Save draft message to localStorage whenever it changes
//   useEffect(() => {
//     if (message) {
//       localStorage.setItem("messageDraft", message);
//       setMessageSaved(true);
//     }
//   }, [message]);

//   return (
//     <div className="message-container">
//       <div className="left">
//         <h3>All Messages</h3>
//         <section className="search">
//           <FaSearch />
//           <input
//             type="text"
//             placeholder="Search..."
//             value={query}
//             onChange={handleInputChange}
//           />
//         </section>
//         {results.map((x) => (
//           <Link to="" key={x.id}>
//             <img src={x.img} alt="" />
//             <div>
//               <span className="top">
//                 <span>{x.username}</span>
//                 <span>{x.time}</span>
//               </span>
//               <span className="msg">{x.msg}</span>
//             </div>
//           </Link>
//         ))}
//         {results.length === 0 && query !== "" && (
//           <div>No result for your search</div>
//         )}
//       </div>
//       <div className="center">
//         <div className="top">
//           <div className="top-left">
//             <img src={img} alt="" />
//             <div className="text">
//               <span>ejovwogfreeman</span>
//               <span>online</span>
//             </div>
//           </div>
//           <div className="top-right">
//             <IoCallOutline />
//             <HiOutlineVideoCamera />
//           </div>
//         </div>
//         <div className="chats">
//           {chats.map((x) => (
//             <div
//               className={x.type === "sender" ? "chat sender" : "chat receiver"}
//               key={Math.random()}
//             >
//               <div
//                 className={
//                   x.type === "sender" ? "sender-color" : "receiver-color"
//                 }
//               >
//                 <span>{x.username}</span>
//                 <span>{x.msg}</span>
//                 <span>{x.time}</span>
//               </div>
//             </div>
//           ))}
//         </div>
//         <form onSubmit={handleSubmit}>
//           <input
//             type="text"
//             id="message"
//             value={message}
//             onChange={(e) => setMessage(e.target.value)}
//             placeholder="Type your message here..."
//           />
//           <button>
//             <BsSend />
//           </button>
//         </form>
//       </div>
//       <div className="right">
//         <img src={img} alt="" />
//         <span>Ejovwo Godbless</span>
//         <span>@ejovwogfreeman</span> <br />
//         <p>lorem ipsum dolor sit amet lorem ipsum dolor sit amet</p>
//         <section>
//           <span>Name:</span>
//           <span>Ejovwo Godbless</span>
//         </section>
//         <section>
//           <span>Email :</span>
//           <span>ejovwogfreeman007@gmail.com</span>
//         </section>
//         <section>
//           <span>Date Joined :</span>
//           <span>12/12/2022</span>
//         </section>
//       </div>
//     </div>
//   );
// };

// export default Message;

import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FaSearch } from "react-icons/fa";
import "../css/Messages.css";
import img from "../images/gb-profile.png";
import { IoCallOutline } from "react-icons/io5";
import { HiOutlineVideoCamera } from "react-icons/hi";
import { BsSend } from "react-icons/bs";
import { users, chats } from "../data";
import Search from "../components/Search";
import io from "socket.io-client"; // Import Socket.io;

const Message = ({ token }) => {
  const headers = {
    Authorization: `Bearer ${token}`,
  };

  const socket = io("http://test.sammykingx.tech/", {
    headers,
  });

  const { query, results, handleInputChange } = Search(users);

  const [message, setMessage] = useState("");
  const [messageSaved, setMessageSaved] = useState(false);
  const [receivedMessages, setReceivedMessages] = useState([]); // To store received messages

  useEffect(() => {
    // Listen for incoming messages
    socket.on("connection", () => console.log("connected"));
    socket.on("message", (newMessage) => {
      setReceivedMessages((prevMessages) => [...prevMessages, newMessage]);
    });

    return () => {
      // Disconnect from the socket when component unmounts
      socket.disconnect();
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(); // Call the sendMessage function when the form is submitted
  };

  const sendMessage = () => {
    if (message) {
      const newMessage = {
        username: "YourUsername", // Replace with the sender's username
        msg: message,
        time: new Date().toLocaleTimeString(),
      };
      console.log(message);
      // Emit the message to the server
      socket.emit("message", newMessage);

      // Clear the input field
      setMessage("");

      // Save the message to your local chat (if needed)
      setReceivedMessages((prevMessages) => [...prevMessages, newMessage]);
    }
  };

  // Load draft message from localStorage on component mount
  useEffect(() => {
    const savedDraft = localStorage.getItem("messageDraft");
    if (savedDraft) {
      setMessage(savedDraft);
    }
  }, []);

  // Save draft message to localStorage whenever it changes
  useEffect(() => {
    if (message) {
      localStorage.setItem("messageDraft", message);
      setMessageSaved(true);
    }
  }, [message]);

  return (
    <div className="message-container">
      <div className="left">
        <h3>All Messages</h3>
        <section className="search">
          <FaSearch />
          <input
            type="text"
            placeholder="Search..."
            value={query}
            onChange={handleInputChange}
          />
        </section>
        {results.map((x) => (
          <Link to="" key={x.id}>
            <img src={x.img} alt="" />
            <div>
              <span className="top">
                <span>{x.username}</span>
                <span>{x.time}</span>
              </span>
              <span className="msg">{x.msg}</span>
            </div>
          </Link>
        ))}
        {results.length === 0 && query !== "" && (
          <div>No result for your search</div>
        )}
      </div>
      <div className="center">
        <div className="top">
          <div className="top-left">
            <img src={img} alt="" />
            <div className="text">
              <span>ejovwogfreeman</span>
              <span>online</span>
            </div>
          </div>
          <div className="top-right">
            <IoCallOutline />
            <HiOutlineVideoCamera />
          </div>
        </div>
        <div className="chats">
          {chats.map((x) => (
            <div
              className={x.type === "sender" ? "chat sender" : "chat receiver"}
              key={Math.random()}
            >
              <div
                className={
                  x.type === "sender" ? "sender-color" : "receiver-color"
                }
              >
                <span>{x.username}</span>
                <span>{x.msg}</span>
                <span>{x.time}</span>
              </div>
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message here..."
          />
          <button type="submit">
            <BsSend />
          </button>
        </form>
      </div>
      <div className="right">
        <img src={img} alt="" />
        <span>Ejovwo Godbless</span>
        <span>@ejovwogfreeman</span> <br />
        <p>lorem ipsum dolor sit amet lorem ipsum dolor sit amet</p>
        <section>
          <span>Name:</span>
          <span>Ejovwo Godbless</span>
        </section>
        <section>
          <span>Email :</span>
          <span>ejovwogfreeman007@gmail.com</span>
        </section>
        <section>
          <span>Date Joined :</span>
          <span>12/12/2022</span>
        </section>
      </div>
    </div>
  );
};

export default Message;
