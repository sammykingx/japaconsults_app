import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import SideNav from "./components/SideNav";
import Home from "./pages/Home";
import Message from "./pages/Message";
import Files from "./pages/Files";
import "./App.css";

const App = () => {
  return (
    <BrowserRouter>
      <SideNav />
      <div className="main-component">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/message" element={<Message />} />
          <Route path="/files" element={<Files />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
