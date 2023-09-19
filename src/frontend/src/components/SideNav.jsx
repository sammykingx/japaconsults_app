import React from "react";
import { Link } from "react-router-dom";
import { AiOutlineHome } from "react-icons/ai";
import { BsChatRightText, BsFolder2 } from "react-icons/bs";
import { MdOutlineDrafts } from "react-icons/md";
import { BiLogOutCircle } from "react-icons/bi";
import { LiaFileInvoiceDollarSolid } from "react-icons/lia";
import "../css/SideNav.css";
import logo from "../images/logo.png";
import { FaUsers } from "react-icons/fa";

const SideNav = () => {
  return (
    <ul className="side-nav">
      <img src={logo} alt="" width="140px" />
      <Link to="/">
        <AiOutlineHome />
        <span>Home</span>
      </Link>
      <Link to="/users">
        <FaUsers />
        <span>Users</span>
      </Link>
      <Link to="/message">
        <BsChatRightText />
        <span>Messages</span>
      </Link>
      <Link to="/drafts">
        <MdOutlineDrafts />
        <span>Drafts</span>
      </Link>
      <Link to="/files">
        <BsFolder2 />
        <span>Files</span>
      </Link>
      <Link to="/invoices">
        <LiaFileInvoiceDollarSolid />
        <span>Invoice</span>
      </Link>
      <span className="logout">
        <BiLogOutCircle />
        <span>Logout</span>
      </span>
    </ul>
  );
};

export default SideNav;
