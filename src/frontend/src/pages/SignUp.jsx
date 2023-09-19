import React from "react";
import logo from "../images/logo.png";
import { Link } from "react-router-dom";
import "../css/Auth.css";

const SignUp = () => {
  return (
    <div className="auth-form">
      <form>
        <h3>REGISTER</h3>
        <img src={logo} alt="" width="140px" />
        <div>
          <label htmlFor="">Full Name</label>
          <input type="text" />
        </div>
        <div>
          <label htmlFor="">Email</label>
          <input type="email" />
        </div>
        <div>
          <label htmlFor="">Password</label>
          <input type="password" />
        </div>
        <div>
          <button>REGISTER</button>
        </div>
        <section>
          <p>
            Already have an acount? <Link to="/login">Login</Link>
          </p>
        </section>
      </form>
    </div>
  );
};

export default SignUp;
