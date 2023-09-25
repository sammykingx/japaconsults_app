import React, { useState } from "react";
import logo from "../images/logo.png";
import { Link } from "react-router-dom";
import "../css/Auth.css";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const SignIn = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false); // Added loading state

  const { username, password } = formData;

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      return toast.error("PLEASE FILL ALL FIELDS");
    }

    try {
      setIsLoading(true); // Set loading state to true during login request
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await axios.post(
        "http://test.sammykingx.tech/auth",
        formData
      );

      toast.success("LOGIN SUCCESSFUL");
      sessionStorage.setItem("user", JSON.stringify(response.data));
      navigate("/");
      console.log("User logged in successfully:", response.data);
    } catch (error) {
      toast.error("LOGIN FAILED");
      console.error("Error logging in:", error);
    } finally {
      setIsLoading(false); // Set loading state back to false when the request is done
    }
  };

  return (
    <div className="auth-form">
      <form onSubmit={handleLogin}>
        <h3>LOGIN</h3>
        <img src={logo} alt="" width="140px" />
        <div>
          <label htmlFor="username">Email</label>
          <input
            type="text"
            id="username"
            name="username"
            value={username}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={password}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "LOGGING IN..." : "LOGIN"}
          </button>
        </div>
        <section>
          <p>
            New here? <Link to="/register">Register</Link>
          </p>
        </section>
      </form>
    </div>
  );
};

export default SignIn;
