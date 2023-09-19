import React from "react";
import "../css/Home.css";
import { FaUsers } from "react-icons/fa";
import BarChart from "../components/BarCart";
import PieChart from "../components/PieChart";
import { users } from "../data";

const Home = () => {
  const cards = [
    { id: 1, icon: <FaUsers />, text: "Members", num: 55 },
    { id: 2, icon: <FaUsers />, text: "Members", num: 55 },
    { id: 3, icon: <FaUsers />, text: "Members", num: 55 },
    { id: 4, icon: <FaUsers />, text: "Members", num: 55 },
  ];
  return (
    <div className="dashboard-component">
      <div className="top">
        <h2>Dashboard</h2>
      </div>
      <div className="main">
        <div className="cards">
          {cards.map((x) => (
            <div className="card" key={x.id}>
              <span className="info">
                <span>{x.text}</span>
                <FaUsers />
              </span>
              <h3>{x.num}</h3>
            </div>
          ))}
        </div>
        <div className="charts">
          <BarChart />
          <PieChart />
        </div>
        <div className="users">
          <h3>Users</h3>
          {users.map((x) => (
            <div className="user">
              <img src={x.img} alt="" />
              <div>
                <span>{x.username}</span>
                <span>onine</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;
