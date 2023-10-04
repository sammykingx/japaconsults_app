import React from "react";
import { AiOutlineHome } from "react-icons/ai";
import { BsChatRightText, BsFolder2 } from "react-icons/bs";
import { RiDraftLine } from "react-icons/ri";
import { BiLogOutCircle } from "react-icons/bi";
import { LiaFileInvoiceDollarSolid } from "react-icons/lia";
import "../css/SideNav.css";
import logo from "../images/logo.png";
import { FaUsers } from "react-icons/fa";

const SideNav = () => {
  return (
    <ul className="side-nav">
      <img src={logo} alt="" width="140px" />
      <a href="/">
        <AiOutlineHome />
        <span>Home</span>
      </a>
      <a href="/users">
        <FaUsers />
        <span>Users</span>
      </a>
      <a href="/message">
        <BsChatRightText />
        <span>Messages</span>
      </a>
      <a href="/drafts">
        <RiDraftLine />
        <span>Drafts</span>
      </a>
      <a href="/files">
        <BsFolder2 />
        <span>Files</span>
      </a>
      <a href="/invoices">
        <LiaFileInvoiceDollarSolid />
        <span>Invoice</span>
      </a>
      <span className="logout">
        <BiLogOutCircle />
        <span>Logout</span>
      </span>
    </ul>
  );
};

export default SideNav;
