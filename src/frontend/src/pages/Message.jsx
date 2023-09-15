import React, { useState } from "react";
import { Link } from "react-router-dom";
import { FaSearch } from "react-icons/fa";
import "../css/Messages.css";
import img from "../images/gb-profile.png";

const Message = () => {
  let data = [
    {
      id: 1,
      img: img,
      username: "ejovwogfreeman",
      time: "11:17pm",
      msg: "Lorem ipsum dolor sit amet lorem ipsum dolor sit amet",
    },
    {
      id: 2,
      img: img,
      username: "Marksterling123",
      time: "11:17pm",
      msg: "Lorem ipsum dolor sit amet",
    },
    {
      id: 3,
      img: img,
      username: "johndoe27",
      time: "11:17pm",
      msg: "Lorem ipsum dolor sit amet",
    },
  ];
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleInputChange = (event) => {
    setQuery(event.target.value);
    search(event.target.value);
  };

  const search = (query) => {
    const filteredResults = data.filter((item) =>
      item.username.toLowerCase().includes(query.toLowerCase())
    );
    setResults(filteredResults);
  };
  // console.log(query);
  console.log(results);
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
        {results.length > 0 ? (
          results.map((x) => (
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
          ))
        ) : (
          <Link>No result for your search</Link>
        )}
        {!results &&
          data.map((x) => (
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
      </div>
      <div className="center"></div>
      <div className="right"></div>
    </div>
  );
};

export default Message;
