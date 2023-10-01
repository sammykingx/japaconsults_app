import React, { useState } from "react";
import "../css/Files.css";
import { FaSearch } from "react-icons/fa";
import Search from "../components/Search";
import { users } from "../data";
import { AiOutlineCloudUpload } from "react-icons/ai";
import Upload from "../modals/Upload";
import { Link } from "react-router-dom";

const Users = () => {
  const { query, results, handleInputChange } = Search(users);

  const [modal, setModal] = useState(false);
  const handleModal = () => {
    setModal(!modal);
  };

  return (
    <div className="files-container">
      <div className="left">
        <h3>All Users</h3>
        <section className="search">
          <FaSearch />
          <input
            type="text"
            placeholder="Search..."
            value={query}
            onChange={handleInputChange}
          />
        </section>
        <div className="files">
          {results.map((x) => (
            <Link to="" key={Math.random()}>
              <img src={x.img} alt="" />
              <div style={{ marginLeft: "10px" }}>
                <span className="top">
                  <span>{x.username}</span>
                  <span>{x.time}</span>
                </span>
                <span className="msg">{x.msg}</span>
              </div>
            </Link>
          ))}
        </div>
        {results.length === 0 && query !== "" && (
          <div>No result for your search</div>
        )}
      </div>
      <div className="right">
        <div className="top">
          <h3>ejovwogfreeman</h3>
          <AiOutlineCloudUpload onClick={handleModal} />
        </div>
        <div className="images">
          {users.map((x) => (
            <img src={x.img} alt="" key={Math.random()} />
          ))}
        </div>
        {modal && <Upload handleModal={handleModal} />}
      </div>
    </div>
  );
};

export default Users;
