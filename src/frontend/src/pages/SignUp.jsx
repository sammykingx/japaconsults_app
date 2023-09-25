import React, { useState } from "react";
import logo from "../images/logo.png";
import { Link } from "react-router-dom";
import "../css/Auth.css";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const SignUp = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone_num: "",
    password: "",
    confirmPassword: "",
  });

  const [isLoading, setIsLoading] = useState(false); // Initialize loading state

  const { name, email, phone_num, password, confirmPassword } = formData;

  const infoData = { name, email, phone_num, password };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleRegistration = async (e) => {
    e.preventDefault();
    if (!name || !email || !phone_num || !password || !confirmPassword) {
      return toast.error("PLEASE FILL ALL FIELDS");
    }
    if (password.length < 8) {
      return toast.error("PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG");
    }
    if (password !== confirmPassword) {
      return toast.error("PASSWORDS DO NOT MATCH");
    }

    // Set loading state to true while making the registration request
    setIsLoading(true);

    try {
      const response = await axios.post(
        "http://test.sammykingx.tech/user/register",
        infoData
      );

      toast.success("USER REGISTERED SUCCESSFULLY");
      console.log("User registered successfully:", response.data);
      navigate("/login");
    } catch (error) {
      toast.error("AN ERROR OCCURRED");
      console.error("Error registering user:", error);
    } finally {
      // Set loading state back to false regardless of success or error
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <form onSubmit={handleRegistration}>
        <h3>REGISTER</h3>
        <img src={logo} alt="" width="140px" />
        <div>
          <label htmlFor="name">Full Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={name}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={email}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="phone_num">Phone Number</label>
          <input
            type="text"
            id="phone_num"
            name="phone_num"
            value={phone_num}
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
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={confirmPassword}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          {/* Disable the button and show "REGISTERING..." text when loading */}
          <button type="submit" disabled={isLoading}>
            {isLoading ? "REGISTERING..." : "REGISTER"}
          </button>
        </div>
        <section>
          <p>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </section>
      </form>
    </div>
  );
};

export default SignUp;
