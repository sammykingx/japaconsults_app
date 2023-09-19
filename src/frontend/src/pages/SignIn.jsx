import React from "react";
import logo from "../images/logo.png";
import { Link } from "react-router-dom";
import "../css/Auth.css";

const SignIn = () => {
  return (
    <div className="auth-form">
      <form>
        <h3>LOIGIN</h3>
        <img src={logo} alt="" width="140px" />
        <div>
          <label htmlFor="">Email</label>
          <input type="email" />
        </div>
        <div>
          <label htmlFor="">Password</label>
          <input type="password" />
        </div>
        <div>
          <button>LOGIN</button>
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
