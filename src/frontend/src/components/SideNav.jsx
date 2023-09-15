import React from "react";
import { Link } from "react-router-dom";
import { AiOutlineHome } from "react-icons/ai";
import { BsChatRightText, BsFolder2 } from "react-icons/bs";
import { MdNotificationsNone, MdOutlineAddIcCall } from "react-icons/md";
import "../css/SideNav.css";

const SideNav = () => {
  return (
    <ul className="side-nav">
      <h3>JAPA CONSULT</h3>
      <Link to="/">
        <AiOutlineHome />
        <span>Home</span>
      </Link>
      <Link to="/message">
        <BsChatRightText />
        <span>Messages</span>
      </Link>
      <Link to="/files">
        <BsFolder2 />
        <span>Files</span>
      </Link>
      <Link to="/notifications">
        <MdNotificationsNone />
        <span>Notifications</span>
      </Link>
      <Link to="/calls">
        <MdOutlineAddIcCall />
        <span>Calls</span>
      </Link>
    </ul>
  );
};

export default SideNav;
