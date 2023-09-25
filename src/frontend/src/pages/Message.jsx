// import React, { useState } from "react";
import { Link } from "react-router-dom";
import { FaSearch } from "react-icons/fa";
import "../css/Messages.css";
import img from "../images/gb-profile.png";
import { IoCallOutline } from "react-icons/io5";
import { HiOutlineVideoCamera } from "react-icons/hi";
import { BsSend } from "react-icons/bs";
import { users, chats } from "../data";
import Search from "../components/Search";

const Message = () => {
  const { query, results, handleInputChange } = Search(users);
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
              key={x.id}
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
        <form action="">
          <input type="text" placeholder="Type your message here..." />
          <button>
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
