import React, { useState } from "react";
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
import Toastify from "./components/Toastify";
import ProtectedRoutes from "./components/ProtectedRoutes";
import "./App.css";

const App = () => {
  const [user, setUser] = useState({});
  var localUser = JSON.parse(sessionStorage.getItem("user"));
  let token;
  if (localUser) {
    token = localUser.access_token ? localUser.access_token : null;
    const getUser = async () => {
      // Replace 'your_token_here' with the actual token value
      const token_id = token;

      // Create a Headers object and set the Authorization header
      const headers = new Headers();
      headers.append("Authorization", `Bearer ${token_id}`);

      // Create the fetch request with the headers
      const res = await fetch("http://test.sammykingx.tech/user/profile", {
        method: "GET",
        headers: headers,
      });

      const data = await res.json();
      setUser(data);
      getUser();
    };
  }

  return (
    <BrowserRouter>
      <Toastify />
      <SideNav />
      <div className="main-component">
        <Routes>
          <Route element={<ProtectedRoutes />}>
            <Route path="/" element={<Home user={user} />} />{" "}
          </Route>
          <Route element={<ProtectedRoutes />}>
            <Route path="/message" element={<Message token={token} />} />
          </Route>
          <Route element={<ProtectedRoutes />}>
            <Route path="/drafts" element={<Drafts token={token} />} />
          </Route>
          <Route element={<ProtectedRoutes />}>
            <Route path="/files" element={<Files />} />
          </Route>
          <Route element={<ProtectedRoutes />}>
            <Route path="/users" element={<Users />} />
          </Route>
          <Route element={<ProtectedRoutes />}>
            <Route path="/invoices" element={<Invoice />} />
          </Route>
          <Route path="/register" element={<SignUp />} />
          <Route path="/login" element={<SignIn />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
