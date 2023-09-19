import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import SideNav from "./components/SideNav";
import Home from "./pages/Home";
import Message from "./pages/Message";
import Files from "./pages/Files";
import SignUp from "./pages/SignUp";
import SignIn from "./pages/SignIn";
import Drafts from "./pages/Drafts";
import Users from "./pages/Users";
import Invoice from "./pages/Invoice";
// import Search from "./components/Search";
import "./App.css";

const App = () => {
  return (
    <BrowserRouter>
      <SideNav />
      <div className="main-component">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/message" element={<Message />} />
          <Route path="/drafts" element={<Drafts />} />
          <Route path="/files" element={<Files />} />
          <Route path="/users" element={<Users />} />
          <Route path="/invoices" element={<Invoice />} />
          <Route path="/register" element={<SignUp />} />
          <Route path="/login" element={<SignIn />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
